import asyncio

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
    log_widget,
    content_markdown,
    navigation_providers,
    navigation_resources,
    search,
)

import logging

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

    def compose(self) -> ComposeResult:
        LOGGER.info("Composing UI")
        # Navigation
        with Container(id="sidebar"):
            with Container(id="navigation"):
                yield navigation_providers
                yield navigation_resources

        # Main content area
        with Container(id="content"):
            yield content_markdown

        yield log_widget

        yield Footer()
        LOGGER.info("Composing UI done")

    async def on_ready(self) -> None:
        LOGGER.info("Starting on ready")
        log_widget.write("Populating providers from the registry API")
        content_markdown.document.classes = "bordered content"
        content_markdown.document.border_title = "Content"
        content_markdown.document.border_subtitle = "Welcome"
        if self.size.width < 125:
            registry.fullscreen_mode = True
        if registry.fullscreen_mode:
            navigation_providers.styles.column_span = 2
            navigation_resources.styles.column_span = 2
            content_markdown.styles.column_span = 2
            self.screen.maximize(navigation_providers)
        navigation_providers.loading = True
        self.screen.refresh()
        await asyncio.sleep(0.001)
        LOGGER.info("Starting on ready done, running preload worker")
        self.app.run_worker(self._preload, name="preload")

    @staticmethod
    async def _preload() -> None:
        LOGGER.info("preload start")
        registry.providers = await populate_providers()
        log_widget.write(f"Providers loaded ([cyan bold]{len(registry.providers)}[/])")
        ui_populate_providers()
        navigation_providers.loading = False
        navigation_providers.highlighted = 0
        log_widget.write(Markdown("---"))
        LOGGER.info("preload done")

    def action_search(self) -> None:
        """Focus the search input."""
        if search.has_parent:
            search.parent.remove_children([search])
        for searchable in [navigation_providers, navigation_resources]:
            if searchable.has_focus:
                search.value = ""
                searchable.mount(search)
                search.focus()
                search.offset = searchable.offset + (
                    0,
                    searchable.size.height - 3,
                )

    def action_use(self) -> None:
        if registry.active_provider:
            self.copy_to_clipboard(registry.active_provider.use_configuration)
            self.notify(registry.active_provider.use_configuration, title="Copied")

    def action_log(self) -> None:
        log_widget.display = not log_widget.display

    def action_providers(self) -> None:
        if registry.fullscreen_mode:
            self.screen.maximize(navigation_providers)
        navigation_providers.focus()

    def action_resources(self) -> None:
        if registry.fullscreen_mode:
            self.screen.maximize(navigation_resources)
        navigation_resources.focus()

    def action_content(self) -> None:
        if registry.fullscreen_mode:
            self.screen.maximize(content_markdown)
        content_markdown.document.focus()

    def action_fullscreen(self) -> None:
        if registry.fullscreen_mode:
            registry.fullscreen_mode = False
            navigation_providers.styles.column_span = 1
            navigation_resources.styles.column_span = 1
            content_markdown.styles.column_span = 1
            self.screen.minimize()
        else:
            registry.fullscreen_mode = True
            navigation_providers.styles.column_span = 2
            navigation_resources.styles.column_span = 2
            content_markdown.styles.column_span = 2
            self.screen.maximize(self.screen.focused)

    async def action_version(self) -> None:
        if registry.active_provider is None:
            self.notify(
                "Provider Version can only be changed after one is selected.",
                title="No provider selected",
                severity="warning",
            )
            return
        if navigation_resources.children:
            navigation_resources.remove_children("#version-select")
        else:
            version_select = Select.from_values(
                (v["id"] for v in registry.active_provider.versions),
                prompt="Select Provider Version",
                allow_blank=False,
                value=registry.active_provider.active_version,
                id="version-select",
            )
            navigation_resources.mount(version_select)
            await asyncio.sleep(0.1)
            version_select.action_show_overlay()

    @on(Select.Changed, "#version-select")
    async def change_provider_version(self, event: Select.Changed) -> None:
        if event.value != registry.active_provider.active_version:
            registry.active_provider.active_version = event.value
            await load_provider_resources(registry.active_provider)
            navigation_resources.remove_children("#version-select")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "search":
            return

        query = event.value.strip()
        if search.parent == navigation_providers:
            if not query:
                ui_populate_providers()
            else:
                ui_populate_providers(
                    [p for p in registry.providers.keys() if query in p]
                )
        elif search.parent == navigation_resources:
            if not query:
                populate_resources(registry.active_provider)
            else:
                populate_resources(
                    registry.active_provider,
                    [r for r in registry.active_provider.resources if query in r.name],
                )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        search.parent.focus()
        search.parent.highlighted = 0
        search.parent.remove_children([search])

    async def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        if event.control == navigation_providers:
            provider_selected = registry.providers[event.option.prompt]
            registry.active_provider = provider_selected
            if registry.fullscreen_mode:
                self.screen.maximize(navigation_resources)
            await load_provider_resources(provider_selected)
        elif event.control == navigation_resources:
            resource_selected = event.option.prompt
            if registry.fullscreen_mode:
                self.screen.maximize(content_markdown)
            content_markdown.loading = True
            content_markdown.document.update(await resource_selected.content())
            content_markdown.document.border_subtitle = f"{resource_selected.type.value} - {resource_selected.provider.name}_{resource_selected.name}"
            content_markdown.document.focus()
            content_markdown.loading = False


def main() -> None:
    LOGGER.info("Starting tofuref")
    TofuRefApp().run()


if __name__ == "__main__":
    main()
