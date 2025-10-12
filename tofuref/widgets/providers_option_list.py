import json
import logging
import time
from collections.abc import Collection
from pathlib import Path
from typing import ClassVar, cast

from textual.binding import BindingType
from textual.widgets.option_list import Option

from tofuref.config import config
from tofuref.data.cache import get_cached_providers
from tofuref.data.helpers import get_registry_api
from tofuref.data.providers import Provider
from tofuref.widgets import keybindings
from tofuref.widgets.menu_option_list_base import MenuOptionListBase

LOGGER = logging.getLogger(__name__)


class ProvidersOptionList(MenuOptionListBase):
    BINDINGS: ClassVar[list[BindingType]] = [*MenuOptionListBase.BINDINGS, keybindings.OPEN_GITHUB, keybindings.GITHUB_STATS]

    def __init__(self, **kwargs):
        super().__init__(
            name="Providers",
            id="nav-provider",
            classes="nav-selector",
            **kwargs,
        )
        self.display = False
        self.fallback_providers_file = Path(__file__).resolve().parent.parent / "fallback" / "providers.json"

    def populate(
        self,
        providers: Collection[Provider] | None = None,
    ) -> None:
        if providers is None:
            providers = self.app.providers.values()
        self.clear_options()
        self.add_options(providers)
        self.border_subtitle = f"{len(providers):n} / {len(self.app.providers):n}"

    async def load_index(self) -> dict[str, Provider]:
        LOGGER.debug("Loading providers")

        data = await get_registry_api("index.json")
        await self.app.force_draw(initial=True)
        if not data:
            data = json.loads(self.fallback_providers_file.read_text())
            self.app.notify(
                "Something went wrong while fetching index of providers, using limited fallback.",
                title="Using fallback",
                severity="error",
            )

        LOGGER.debug("Got API response (or fallback)")
        await self.app.force_draw(initial=True)

        providers = await self.load_providers(data)

        providers = dict(sorted(providers.items(), key=lambda p: (p[1].bookmarked, p[1].cached, p[1].popularity), reverse=True))
        await self.app.force_draw(initial=True)
        return providers

    async def load_providers(self, data: dict) -> dict[str, Provider]:
        """
        Loads providers from API data. To show up in tofuref, it must:

        * have version
        * not be blocked in the registry
        * not be a fork
        * not be part of the organizations opentofu or terraform-providers, because those are just duplicates
        """
        providers = {}
        cached_providers = await get_cached_providers()

        for provider_json in data["providers"]:
            provider = Provider.from_json(provider_json)

            filter_in = (
                provider.versions,
                not provider.blocked,
                not provider.fork_of,
                provider.organization not in ["terraform-providers", "opentofu"],
            )
            if all(filter_in):
                providers[provider.display_name] = provider
                if self.app.bookmarks.check("providers", provider.identifying_name):
                    provider.bookmarked = True
                if provider.display_name in cached_providers:
                    provider.cached = True
        return providers

    async def on_option_selected(self, option: Option) -> None:
        __start_time = time.perf_counter()

        provider_selected = cast(Provider, option.prompt)
        self.app.active_provider = provider_selected

        await self.app.force_draw()
        await self.app.navigation_resources.load_provider_resources(provider_selected)

        self.app.navigation_resources.focus()

        await self.app.force_draw()
        self.replace_option_prompt_at_index(self.highlighted, option.prompt)

        if config.show_load_times:
            __load_time = time.perf_counter() - __start_time
            self.app.notify(f"Provider {provider_selected.name} loaded in {int(__load_time * 1000)}ms", timeout=10)

    def action_open_github(self):
        if self.highlighted is None:
            return
        option = self.get_option_at_index(self.highlighted)
        provider: Provider = option.prompt
        self.app.open_url(provider.github_url)

    async def action_github_stats(self):
        if self.highlighted is None:
            return
        option = self.get_option_at_index(self.highlighted)
        provider: Provider = option.prompt
        stats = await provider.github_stats()
        if stats:
            msg = f"Stars: [$primary]{stats['stars']}[/]\nOpen issues/PRs: [$primary]{stats['open_issues']}[/]"
            if stats["archived"]:
                msg += "\n[bold $warning]Archived[/]"
            self.app.notify(
                msg,
                title=f"GitHub stats for {provider.organization}/{provider.name}",
                timeout=15,
            )
        else:
            self.app.notify(
                "Something went wrong while fetching GitHub stats.",
                title="GitHub stats error",
                severity="error",
            )
