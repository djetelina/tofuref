import asyncio
from typing import Iterable, Optional, List

import textual.app
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

from tofuref.data.resources import Resource
from tofuref.data.providers import populate_providers, Provider
from tofuref.data.registry import registry
from tofuref.widgets import (
    log_widget,
    content_markdown,
    navigation_providers,
    navigation_resources,
    search,
)


class TofuRefApp(App):
    CSS_PATH = "tofuref.tcss"
    TITLE = "TofuRef - OpenTofu Provider Reference"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "search", "Search"),
        ("/", "search", "Search"),
        ("v", "version", "Provider Version"),
        ("p", "providers", "Providers"),
        ("r", "resources", "Resources"),
        ("c", "content", "Content"),
        ("f", "fullscreen", "Fullscreen Mode"),
        ("l", "log", "Show Log"),
    ]

    def compose(self) -> ComposeResult:
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

    async def on_ready(self) -> None:
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
        await asyncio.sleep(0.1)
        self.app.run_worker(self._preload, name="preload")

    @staticmethod
    async def _preload():
        registry.providers = await populate_providers()
        log_widget.write(f"Providers loaded ([cyan bold]{len(registry.providers)}[/])")
        _populate_providers()
        navigation_providers.loading = False
        navigation_providers.highlighted = 0
        log_widget.write(Markdown("---"))

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

    def action_log(self) -> None:
        log_widget.display = not log_widget.display

    def action_providers(self):
        if registry.fullscreen_mode:
            self.screen.maximize(navigation_providers)
        navigation_providers.focus()

    def action_resources(self):
        if registry.fullscreen_mode:
            self.screen.maximize(navigation_resources)
        navigation_resources.focus()

    def action_content(self):
        if registry.fullscreen_mode:
            self.screen.maximize(content_markdown)
        content_markdown.document.focus()

    def action_fullscreen(self):
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

    async def action_version(self):
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
            await _load_provider_resources(registry.active_provider)
            navigation_resources.remove_children("#version-select")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "search":
            return

        query = event.value.strip()
        if search.parent == navigation_providers:
            if not query:
                _populate_providers()
            else:
                _populate_providers(
                    [p for p in registry.providers.keys() if query in p]
                )
        elif search.parent == navigation_resources:
            if not query:
                _populate_resources(registry.active_provider)
            else:
                _populate_resources(
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
            await _load_provider_resources(provider_selected)
        elif event.control == navigation_resources:
            resource_selected = event.option.prompt
            if registry.fullscreen_mode:
                self.screen.maximize(content_markdown)
            content_markdown.loading = True
            content_markdown.document.update(await resource_selected.content())
            content_markdown.document.border_subtitle = f"{resource_selected.type.value} - {resource_selected.provider.name}_{resource_selected.name}"
            content_markdown.document.focus()
            content_markdown.loading = False


async def _load_provider_resources(provider: Provider):
    navigation_resources.loading = True
    content_markdown.loading = True
    await provider.load_resources()
    content_markdown.document.update(await provider.overview())
    content_markdown.document.border_subtitle = (
        f"{provider.display_name} {provider.active_version} Overview"
    )
    _populate_resources(provider)
    navigation_resources.focus()
    navigation_resources.highlighted = 0
    content_markdown.loading = False
    navigation_resources.loading = False


def _populate_providers(providers: Optional[Iterable[str]] = None) -> None:
    if providers is None:
        providers = registry.providers.keys()
    navigation_providers.clear_options()
    navigation_providers.border_subtitle = f"{len(providers)}/{len(registry.providers)}"
    for name in providers:
        navigation_providers.add_option(name)


def _populate_resources(
    provider: Optional[Provider] = None, resources: Optional[List[Resource]] = None
) -> None:
    navigation_resources.clear_options()
    if provider is None:
        return
    navigation_resources.border_subtitle = (
        f"{provider.organization}/{provider.name} {provider.active_version}"
    )

    if resources is None:
        for resource in provider.resources:
            navigation_resources.add_option(resource)
    else:
        navigation_resources.add_options(resources)


def main():
    TofuRefApp().run()


if __name__ == "__main__":
    main()
