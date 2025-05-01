import asyncio
from typing import Iterable, Optional, List

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import (
    Footer,
    Input,
    OptionList,
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
        ("p", "providers", "Providers"),
        ("r", "resources", "Resources"),
        ("c", "content", "Content"),
        ("l", "log", "Show Log"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
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
        """Set up the application when it starts."""
        log_widget.write("Fetching OpenTofu registry")
        content_markdown.document.classes = "bordered content"
        content_markdown.document.border_title = "Content"
        content_markdown.document.border_subtitle = "Welcome"
        self.screen.refresh()
        await asyncio.sleep(0.1)
        self.app.run_worker(self._preload, name="preload")

    async def _preload(self):
        registry.providers = await populate_providers()
        log_widget.write(f"Providers loaded ([cyan bold]{len(registry.providers)}[/])")
        _populate_providers()
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
                search.offset = navigation_providers.offset + (
                    0,
                    navigation_providers.size.height - 3,
                )

    def action_log(self) -> None:
        log_widget.display = not log_widget.display

    def action_providers(self):
        navigation_providers.focus()

    def action_resources(self):
        navigation_resources.focus()

    def action_content(self):
        content_markdown.document.focus()

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
            await provider_selected.load_resources()
            content_markdown.document.update(await provider_selected.overview())
            content_markdown.border_subtitle = f"{provider_selected.display_name}"
            _populate_resources(provider_selected)
            navigation_resources.focus()
        elif event.control == navigation_resources:
            resource_selected = event.option.prompt
            content_markdown.document.update(await resource_selected.content())
            content_markdown.document.border_subtitle = f"{resource_selected.type.value} - {resource_selected.provider.name}_{resource_selected.name}"
            content_markdown.document.focus()


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
