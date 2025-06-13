import json
import logging
from collections.abc import Collection
from pathlib import Path

from textual.widgets.option_list import Option

from tofuref.data.helpers import get_registry_api
from tofuref.data.providers import Provider
from tofuref.widgets.menu_option_list_base import MenuOptionListBase

LOGGER = logging.getLogger(__name__)


class ProvidersOptionList(MenuOptionListBase):
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
        self.border_subtitle = f"{len(providers)}/{len(self.app.providers)}"
        for provider in providers:
            self.add_option(provider)

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

        providers = {k: v for k, v in sorted(providers.items(), key=lambda p: (p[1].bookmarked, p[1].cached, p[1].popularity), reverse=True)}

        return providers

    async def on_option_selected(self, option: Option) -> None:
        provider_selected = option.prompt
        self.app.active_provider = provider_selected
        if self.app.fullscreen_mode:
            self.screen.maximize(self.app.navigation_resources)
        await self.app.navigation_resources.load_provider_resources(provider_selected)
        self.replace_option_prompt_at_index(self.highlighted, option.prompt)
