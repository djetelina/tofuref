import asyncio
import logging

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import (
    Footer,
    Input,
    OptionList,
    Select,
)
from rich.markdown import Markdown

from tofuref.data.providers import populate_providers
from tofuref.data.registry import registry
from tofuref.ui_logic import (
    load_provider_resources,
    populate_providers as ui_populate_providers,
    populate_resources,
)
from tofuref.widgets import (
    CustomRichLog,
    WelcomeMarkdownViewer,
    ProvidersOptionList,
    ResourcesOptionList,
    SearchInput,
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
        ("u", "use", "Use provider"),
        ("y", "use", "Use provider"),
        ("r", "resources", "Resources"),
        ("c", "content", "Content"),
        ("f", "fullscreen", "Fullscreen Mode"),
        ("l", "log", "Show Log"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_widget = CustomRichLog()
        self.content_markdown = WelcomeMarkdownViewer()
        self.navigation_providers = ProvidersOptionList()
        self.navigation_resources = ResourcesOptionList()
        self.search = SearchInput()

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
            registry.fullscreen_mode = True
        if registry.fullscreen_mode:
            self.navigation_providers.styles.column_span = 2
            self.navigation_resources.styles.column_span = 2
            self.content_markdown.styles.column_span = 2
            self.screen.maximize(self.navigation_providers)
        self.navigation_providers.loading = True
        self.screen.refresh()
        await asyncio.sleep(0.001)
        LOGGER.debug("Starting on ready done, running preload worker")
        self.app.run_worker(self._preload, name="preload")

    async def _preload(self) -> None:
        LOGGER.debug("preload start")
        registry.providers = await populate_providers(log_widget=self.log_widget)
        self.log_widget.write(
            f"Providers loaded ([cyan bold]{len(registry.providers)}[/])"
        )
        ui_populate_providers(navigation_providers=self.navigation_providers)
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

    def action_use(self) -> None:
        if registry.active_provider:
            self.copy_to_clipboard(registry.active_provider.use_configuration)
            self.notify(
                registry.active_provider.use_configuration, title="Copied", timeout=10
            )

    def action_log(self) -> None:
        self.log_widget.display = not self.log_widget.display

    def action_providers(self) -> None:
        if registry.fullscreen_mode:
            self.screen.maximize(self.navigation_providers)
        self.navigation_providers.focus()

    def action_resources(self) -> None:
        if registry.fullscreen_mode:
            self.screen.maximize(self.navigation_resources)
        self.navigation_resources.focus()

    def action_content(self) -> None:
        if registry.fullscreen_mode:
            self.screen.maximize(self.content_markdown)
        self.content_markdown.document.focus()

    def action_fullscreen(self) -> None:
        if registry.fullscreen_mode:
            registry.fullscreen_mode = False
            self.navigation_providers.styles.column_span = 1
            self.navigation_resources.styles.column_span = 1
            self.content_markdown.styles.column_span = 1
            self.screen.minimize()
        else:
            registry.fullscreen_mode = True
            self.navigation_providers.styles.column_span = 2
            self.navigation_resources.styles.column_span = 2
            self.content_markdown.styles.column_span = 2
            self.screen.maximize(self.screen.focused)

    async def action_version(self) -> None:
        if registry.active_provider is None:
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
                (v["id"] for v in registry.active_provider.versions),
                prompt="Select Provider Version",
                allow_blank=False,
                value=registry.active_provider.active_version,
                id="version-select",
            )
            await self.navigation_resources.mount(version_select)
            await asyncio.sleep(0.1)
            version_select.action_show_overlay()

    @on(Select.Changed, "#version-select")
    async def change_provider_version(self, event: Select.Changed) -> None:
        if event.value != registry.active_provider.active_version:
            registry.active_provider.active_version = event.value
            await load_provider_resources(
                registry.active_provider,
                navigation_resources=self.navigation_resources,
                content_markdown=self.content_markdown,
            )
            await self.navigation_resources.remove_children("#version-select")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "search":
            return

        query = event.value.strip()
        if self.search.parent == self.navigation_providers:
            if not query:
                ui_populate_providers(navigation_providers=self.navigation_providers)
            else:
                ui_populate_providers(
                    [p for p in registry.providers.keys() if query in p],
                    navigation_providers=self.navigation_providers,
                )
        elif self.search.parent == self.navigation_resources:
            if not query:
                populate_resources(
                    registry.active_provider,
                    navigation_resources=self.navigation_resources,
                )
            else:
                populate_resources(
                    registry.active_provider,
                    [r for r in registry.active_provider.resources if query in r.name],
                    navigation_resources=self.navigation_resources,
                )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.search.parent.focus()
        self.search.parent.highlighted = 0
        self.search.parent.remove_children([self.search])

    async def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        if event.control == self.navigation_providers:
            provider_selected = registry.providers[event.option.prompt]
            registry.active_provider = provider_selected
            if registry.fullscreen_mode:
                self.screen.maximize(self.navigation_resources)
            await load_provider_resources(
                provider_selected,
                navigation_resources=self.navigation_resources,
                content_markdown=self.content_markdown,
            )
        elif event.control == self.navigation_resources:
            resource_selected = event.option.prompt
            if registry.fullscreen_mode:
                self.screen.maximize(self.content_markdown)
            self.content_markdown.loading = True
            await self.content_markdown.document.update(
                await resource_selected.content()
            )
            self.content_markdown.document.border_subtitle = f"{resource_selected.type.value} - {resource_selected.provider.name}_{resource_selected.name}"
            self.content_markdown.document.focus()
            self.content_markdown.loading = False


def main() -> None:
    LOGGER.debug("Starting tofuref")
    TofuRefApp().run()


if __name__ == "__main__":
    main()
