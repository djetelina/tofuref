import asyncio
from typing import Iterable, Optional

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import (
    Footer,
    Input,
    OptionList,
)
from rich.markdown import Markdown

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
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        # Sidebar with search and provider tree
        with Container(id="sidebar"):
            yield search
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
        self.screen.refresh()
        await asyncio.sleep(0.1)
        self.app.run_worker(self._preload, name="preload")

    async def _preload(self):
        registry.providers = await populate_providers()
        log_widget.write(f"Providers loaded ([cyan bold]{len(registry.providers)}[/])")
        _populate_providers()
        log_widget.write(Markdown("---"))

    def action_search(self) -> None:
        """Focus the search input."""
        search.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "search":
            return

        query = event.value.strip()
        if not query:
            _populate_providers()
        else:
            _populate_providers([p for p in registry.providers.keys() if query in p])

    def on_input_submitted(self, event: Input.Submitted) -> None:
        navigation_providers.focus()
        navigation_providers.highlighted = 0

    async def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        if event.control == navigation_providers:
            provider_selected = registry.providers[event.option.prompt]
            log_widget.write(provider_selected)
            await provider_selected.load_resources()
            content_markdown.document.update(await provider_selected.overview())
            content_markdown.border_subtitle = f"{provider_selected.display_name}"
            _populate_resources(provider_selected)
            navigation_resources.focus()
        elif event.control == navigation_resources:
            resource_selected = event.option.prompt
            content_markdown.document.update(await resource_selected.content())
            content_markdown.border_subtitle = f"{resource_selected.type.value} - {resource_selected.provider.name}_{resource_selected.name}"
            content_markdown.focus()


def _populate_providers(providers: Optional[Iterable[str]] = None) -> None:
    if providers is None:
        providers = registry.providers.keys()
    navigation_providers.clear_options()
    navigation_providers.border_subtitle = f"{len(providers)}/{len(registry.providers)}"
    for name in providers:
        navigation_providers.add_option(name)


def _populate_resources(provider: Optional[Provider] = None) -> None:
    navigation_resources.clear_options()
    if provider is None:
        return
    i = 0
    navigation_resources.border_subtitle = (
        f"{provider.organization}/{provider.name} {provider.active_version}"
    )

    for resource in provider.resources:
        navigation_resources.add_option(resource)


def main():
    TofuRefApp().run()


if __name__ == "__main__":
    main()
