import json
import logging
from collections.abc import Collection
from pathlib import Path
from typing import ClassVar

from textual.binding import BindingType
from textual.widgets.option_list import Option

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
            classes="nav-selector bordered",
            **kwargs,
        )
        self.border_title = "Providers"
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
        providers = {}

        data = await get_registry_api(
            "index.json",
            log_widget=self.app.log_widget,
        )
        if not data:
            data = json.loads(self.fallback_providers_file.read_text())
            self.app.notify(
                "Something went wrong while fetching index of providers, using limited fallback.",
                title="Using fallback",
                severity="error",
            )

        LOGGER.debug("Got API response (or fallback)")
        await self.app.pause()

        for provider_json in data["providers"]:
            provider = Provider.from_json(provider_json)
            provider.log_widget = self.app.log_widget
            filter_in = (
                provider.versions,
                not provider.blocked,
                (not provider.fork_of or provider.organization == "opentofu"),
                provider.organization not in ["terraform-providers"],
            )
            if all(filter_in):
                providers[provider.display_name] = provider
                if self.app.bookmarks.check("providers", provider.identifying_name):
                    provider.bookmarked = True
        await self.app.pause()
        providers = {k: v for k, v in sorted(providers.items(), key=lambda p: (p[1].bookmarked, p[1].cached, p[1].popularity), reverse=True)}

        await self.app.pause()
        return providers

    async def on_option_selected(self, option: Option) -> None:
        provider_selected = option.prompt
        self.app.active_provider = provider_selected
        if self.app.fullscreen_mode:
            self.screen.maximize(self.app.navigation_resources)
        await self.app.pause()
        await self.app.navigation_resources.load_provider_resources(provider_selected)
        await self.app.pause()
        self.replace_option_prompt_at_index(self.highlighted, option.prompt)

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
