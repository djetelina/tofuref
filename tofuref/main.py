import asyncio
import locale
import logging
import sys
import time
from typing import ClassVar

import httpx
from packaging.version import Version
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Container, Middle
from textual.theme import BUILTIN_THEMES
from textual.widgets import (
    Footer,
    Input,
    OptionList,
    Select,
    TabbedContent,
    TabPane,
)

from tofuref import __version__
from tofuref.config import config
from tofuref.data.bookmarks import Bookmarks
from tofuref.widgets import CodeBlockSelect, ContentWindow, Logo, ProvidersOptionList, ResourcesOptionList, SearchInput, StartProgress, Status

LOGGER = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, "")


class TofuRefApp(App):
    CSS_PATH = "tofuref.tcss"
    BINDINGS: ClassVar[list[BindingType]] = [
        ("/", "search", "Search"),
        Binding("s", "search", "Search", show=False),
        ("y", "use", "Use provider"),
        Binding("u", "use", "Use provider", show=False),
        ("v", "version", "Provider Version"),
        Binding("p", "providers", "Providers", show=False),
        Binding("r", "resources", "Resources", show=False),
        Binding("c", "content", "Content", show=False),
        Binding("ctrl+l", "log", "Show Log", show=False),
        Binding("q", "quit", "Quit"),
    ]
    TITLE = "TofuRef - OpenTofu Provider Reference"
    ESCAPE_TO_MINIMIZE = False

    def __init__(self, *args, **kwargs):
        self.__start_time: float = time.perf_counter()
        # We are updating config in the tests, we need to reload config
        if "pytest" in sys.modules:
            config.load(reset=True)
        # We have to do this super early, otherwise tests are flaky
        for theme in BUILTIN_THEMES.values():
            theme.variables.update({"border-style": config.theme.borders_style})

        super().__init__(*args, **kwargs)
        # Widgets for easier reference, they could be replaced by query method
        self.content_markdown = ContentWindow()
        self.navigation_providers = ProvidersOptionList()
        self.navigation_resources = ResourcesOptionList()
        self.search = SearchInput()
        self.code_block_selector = CodeBlockSelect()
        self.initial_progress = StartProgress(total=7, show_eta=False, show_percentage=False)

        # Internal state
        self.bookmarks = Bookmarks()
        self.providers = {}
        self._active_provider = None
        self._active_resource = None
        self._search_target: ProvidersOptionList | ResourcesOptionList | None = None

        self.theme = config.theme.ui
        self.__load_time: float | None = None

    @property
    def active_provider(self):
        return self._active_provider

    @active_provider.setter
    def active_provider(self, provider):
        status = self.query_one("Status")
        status.provider.content = provider.display_name
        status.version.content = provider.active_version
        status.resource.content = "Overview"
        self._active_provider = provider

    @property
    def active_resource(self):
        return self._active_resource

    @active_resource.setter
    def active_resource(self, resource):
        self.query_one("Status").resource.content = f"{resource.provider.name}_{resource.name}"
        self._active_resource = resource

    def compose(self) -> ComposeResult:
        # Navigation
        with Container(id="header"):
            yield Status()
            yield Logo()

        with Container(id="navigation"):
            with Center(), Middle():
                yield self.initial_progress
            with TabbedContent():
                with TabPane("Providers"):
                    yield self.navigation_providers
                with TabPane("Resources"):
                    yield self.navigation_resources

        self.screen.maximize(self.initial_progress)

        # Main content area
        with Container(id="content"):
            yield self.content_markdown

        yield Footer()

    async def on_ready(self) -> None:
        # Draw the initial layout
        await self.force_draw(initial=True)
        self.call_next(self.load_content)
        self.call_later(self.check_for_new_version)

    async def load_content(self) -> None:
        await self.force_draw(initial=True)
        await self.load_providers_and_bookmarks()
        await self.force_draw(initial=True)
        self.navigation_providers.populate()
        await self.rearrange_loaded()
        await self.force_draw(initial=True)
        if config.show_load_times:
            self.__load_time = time.perf_counter() - self.__start_time
            self.notify(f"Loaded in {int(self.__load_time * 1000)}ms", timeout=10)

    async def load_providers_and_bookmarks(self) -> None:
        to_load = [self.navigation_providers.load_index(), self.bookmarks.async_post_init()]
        self.providers, _ = await asyncio.gather(*to_load)

    async def rearrange_loaded(self) -> None:
        # Start showing providers and resources
        self.navigation_providers.display = True
        self.navigation_resources.display = True
        self.screen.minimize()
        # Focus the first provider
        self.navigation_providers.focus()
        self.navigation_providers.highlighted = 0
        # We no longer need the progress bar
        await self.screen.remove_children([self.query_one("Center")])
        LOGGER.info("Initial load complete")

    async def force_draw(self, seconds=0.001, initial=False):
        """Used to yield event loop to textual so that it can render."""
        if initial:
            self.initial_progress.advance(1)
        if "pytest" not in sys.modules:
            await asyncio.sleep(seconds)

    async def check_for_new_version(self) -> None:
        newest_version = await get_current_pypi_version()
        version = Version(__version__)
        if version < newest_version:
            self.notify(f"✨ Version {newest_version} is available!\n[dim]Update now for the latest improvements[/dim]", timeout=20)

    def _focused_search_target(self) -> ProvidersOptionList | ResourcesOptionList | None:
        for searchable in (self.navigation_providers, self.navigation_resources):
            if searchable.has_focus:
                return searchable
        return None

    def _close_search(self) -> None:
        if self.search.has_parent:
            self.search.remove()
        self._search_target = None

    def action_search(self) -> None:
        """Focus the search input."""
        searchable = self._focused_search_target() or self._search_target
        if searchable is None:
            return

        self._close_search()
        self._search_target = searchable

        search_host = searchable.parent
        if not isinstance(search_host, TabPane):
            return

        self.search.value = ""
        self.search.styles.position = "absolute"
        self.search.styles.layer = "top"
        search_host.mount(self.search)
        self.search.offset = searchable.offset + (0, max(0, searchable.size.height - 3))  # noqa: RUF005
        self.search.focus()

    async def action_use(self) -> None:
        if not self.content_markdown.document.has_focus:
            if self.active_provider:
                to_copy = self.active_provider.use_configuration
            elif self.navigation_providers.highlighted is not None:
                highlighted_provider = self.navigation_providers.options[self.navigation_providers.highlighted].prompt
                to_copy = highlighted_provider.use_configuration
            else:
                return
            self.copy_to_clipboard(to_copy)
            self.notify(to_copy, title="Copied to clipboard", timeout=10)

    def action_providers(self) -> None:
        self.navigation_providers.focus()

    def action_resources(self) -> None:
        self.navigation_resources.focus()

    def action_content(self) -> None:
        self.content_markdown.document.focus()

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
            self.query_one("Status").version.content = event.value
            await self.navigation_resources.load_provider_resources(self.active_provider)
            # TODO open the resource that was selected before version change
            await self.navigation_resources.remove_children("#version-select")

    @on(Input.Changed, "#search")
    def search_input_changed(self, event: Input.Changed) -> None:
        query = event.value.strip()
        search_target = self._search_target
        if search_target == self.navigation_providers:
            if not query:
                self.navigation_providers.populate()
            else:
                self.navigation_providers.populate([v for p, v in self.providers.items() if query in p])
        elif search_target == self.navigation_resources and self.active_provider:
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
    def search_input_submitted(self, _event: Input.Submitted) -> None:
        search_target = self._search_target
        if search_target is not None:
            search_target.focus()
            if search_target.option_count > 0:
                search_target.highlighted = 0
        self._close_search()

    @on(OptionList.OptionSelected)
    async def option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        await event.control.on_option_selected(event.option)


async def get_current_pypi_version() -> Version:
    async with httpx.AsyncClient(headers={"User-Agent": f"tofuref v{__version__}"}) as client:
        try:
            r = await client.get("https://pypi.org/pypi/tofuref/json", timeout=config.http_request_timeout)
        except Exception as _:
            return Version("0.0.0")
        return Version(r.json()["info"]["version"])


def main() -> None:
    LOGGER.debug("Starting tofuref")
    TofuRefApp().run()


if __name__ == "__main__":
    main()
