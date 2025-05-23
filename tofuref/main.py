import logging
from typing import Iterable

from textual import on
from textual.app import App, ComposeResult, SystemCommand
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Input,
    OptionList,
    Select,
)
from rich.markdown import Markdown

from tofuref.widgets import (
    CustomRichLog,
    ContentWindow,
    ProvidersOptionList,
    ResourcesOptionList,
    SearchInput,
    CodeBlockSelect,
)

LOGGER = logging.getLogger(__name__)


class TofuRefApp(App):
    CSS_PATH = "tofuref.tcss"
    TITLE = "TofuRef - OpenTofu Provider Reference"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "search", "Search"),
        ("/", "search", "Search"),
        ("v", "version", "Provider Version"),
        ("p", "providers", "Providers"),
        ("y", "use", "Use provider"),
        ("u", "use", "Use provider"),
        ("r", "resources", "Resources"),
        ("c", "content", "Content"),
        ("f", "fullscreen", "Fullscreen Mode"),
        Binding("ctrl+l", "log", "Show Log", show=False),
    ]
    ESCAPE_TO_MINIMIZE = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_widget = CustomRichLog()
        self.content_markdown = ContentWindow()
        self.navigation_providers = ProvidersOptionList()
        self.navigation_resources = ResourcesOptionList()
        self.search = SearchInput()
        self.code_block_selector = CodeBlockSelect()
        self.fullscreen_mode = False
        self.providers = {}
        self.active_provider = None
        self.active_resource = None

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand("Log", "Toggle log widget (^l)", self.action_log)

    def compose(self) -> ComposeResult:
        # Navigation
        with Container(id="sidebar"):
            with Container(id="navigation"):
                yield self.navigation_providers
                yield self.navigation_resources

        # Main content area
        with Container(id="content"):
            yield self.content_markdown

        yield self.log_widget

        yield Footer()

    async def on_ready(self) -> None:
        LOGGER.debug("Starting on ready")
        self.log_widget.write("Populating providers from the registry API")
        self.content_markdown.document.classes = "bordered content"
        self.content_markdown.document.border_title = "Content"
        self.content_markdown.document.border_subtitle = "Welcome"
        if self.size.width < 125:
            self.fullscreen_mode = True
        if self.fullscreen_mode:
            self.navigation_providers.styles.column_span = 2
            self.navigation_resources.styles.column_span = 2
            self.content_markdown.styles.column_span = 2
            self.screen.maximize(self.navigation_providers)
        self.navigation_providers.loading = True
        self.screen.refresh()
        LOGGER.debug("Starting on ready done, running preload worker")
        self.app.run_worker(self._preload, name="preload")

    async def _preload(self) -> None:
        LOGGER.debug("preload start")
        self.providers = await self.navigation_providers.load_index()
        self.log_widget.write(f"Providers loaded ([cyan bold]{len(self.providers)}[/])")
        self.navigation_providers.populate()
        self.navigation_providers.loading = False
        self.navigation_providers.highlighted = 0
        self.log_widget.write(Markdown("---"))
        LOGGER.info("Initial load complete")

    def action_search(self) -> None:
        """Focus the search input."""
        if self.search.has_parent:
            self.search.parent.remove_children([self.search])
        for searchable in [self.navigation_providers, self.navigation_resources]:
            if searchable.has_focus:
                self.search.value = ""
                searchable.mount(self.search)
                self.search.focus()
                self.search.offset = searchable.offset + (
                    0,
                    searchable.size.height - 3,
                )

    async def action_use(self) -> None:
        if not self.content_markdown.document.has_focus:
            if self.active_provider:
                to_copy = self.active_provider.use_configuration
            elif self.navigation_providers.highlighted is not None:
                highlighted_provider = self.navigation_providers.options[
                    self.navigation_providers.highlighted
                ].prompt
                to_copy = self.providers[highlighted_provider].use_configuration
            else:
                return
            self.copy_to_clipboard(to_copy)
            self.notify(to_copy, title="Copied to clipboard", timeout=10)

    def action_log(self) -> None:
        self.log_widget.display = not self.log_widget.display

    def action_providers(self) -> None:
        if self.fullscreen_mode:
            self.screen.maximize(self.navigation_providers)
        self.navigation_providers.focus()

    def action_resources(self) -> None:
        if self.fullscreen_mode:
            self.screen.maximize(self.navigation_resources)
        self.navigation_resources.focus()

    def action_content(self) -> None:
        if self.fullscreen_mode:
            self.screen.maximize(self.content_markdown)
        self.content_markdown.document.focus()

    def action_fullscreen(self) -> None:
        if self.fullscreen_mode:
            self.fullscreen_mode = False
            self.navigation_providers.styles.column_span = 1
            self.navigation_resources.styles.column_span = 1
            self.content_markdown.styles.column_span = 1
            self.screen.minimize()
        else:
            self.fullscreen_mode = True
            self.navigation_providers.styles.column_span = 2
            self.navigation_resources.styles.column_span = 2
            self.content_markdown.styles.column_span = 2
            self.screen.maximize(self.screen.focused)

    async def action_version(self) -> None:
        if self.active_provider is None:
            self.notify(
                "Provider Version can only be changed after one is selected.",
                title="No provider selected",
                severity="warning",
            )
            return
        if self.navigation_resources.children:
            await self.navigation_resources.remove_children("#version-select")
        else:
            version_select = Select.from_values(
                (v["id"] for v in self.active_provider.versions),
                prompt="Select Provider Version",
                allow_blank=False,
                value=self.active_provider.active_version,
                id="version-select",
            )
            await self.navigation_resources.mount(version_select)
            version_select.action_show_overlay()

    @on(Select.Changed, "#version-select")
    async def change_provider_version(self, event: Select.Changed) -> None:
        if event.value != self.active_provider.active_version:
            self.active_provider.active_version = event.value
            await self.navigation_resources.load_provider_resources(
                self.active_provider
            )
            await self.navigation_resources.remove_children("#version-select")

    @on(Input.Changed, "#search")
    def search_input_changed(self, event: Input.Changed) -> None:
        query = event.value.strip()
        if self.search.parent == self.navigation_providers:
            if not query:
                self.navigation_providers.populate()
            else:
                self.navigation_providers.populate(
                    [p for p in self.providers.keys() if query in p]
                )
        elif self.search.parent == self.navigation_resources:
            if not query:
                self.navigation_resources.populate(
                    self.active_provider,
                )
            else:
                self.navigation_resources.populate(
                    self.active_provider,
                    [r for r in self.active_provider.resources if query in r.name],
                )

    @on(Input.Submitted, "#search")
    def search_input_submitted(self, event: Input.Submitted) -> None:
        event.control.parent.focus()
        event.control.parent.highlighted = 0
        event.control.parent.remove_children([event.control])

    @on(OptionList.OptionSelected)
    async def option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        await event.control.on_option_selected(event.option)


def main() -> None:
    LOGGER.debug("Starting tofuref")
    TofuRefApp().run()


if __name__ == "__main__":
    main()
