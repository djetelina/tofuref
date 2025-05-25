import json
import logging
from collections.abc import Collection
from pathlib import Path
from typing import ClassVar, cast

from textual.binding import BindingType
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from tofuref.data.helpers import get_registry_api
from tofuref.data.providers import Provider
from tofuref.widgets.keybindings import VIM_OPTION_LIST_NAVIGATE

LOGGER = logging.getLogger(__name__)


class ProvidersOptionList(OptionList):
    BINDINGS: ClassVar[list[BindingType]] = [*OptionList.BINDINGS, *VIM_OPTION_LIST_NAVIGATE]

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
        providers: Collection[str] | None = None,
    ) -> None:
        if providers is None:
            providers = self.app.providers.keys()
        providers = cast(Collection[str], providers)
        self.clear_options()
        self.border_subtitle = f"{len(providers)}/{len(self.app.providers)}"
        for name in providers:
            self.add_option(name)

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

        providers = {k: v for k, v in sorted(providers.items(), key=lambda p: p[1].popularity, reverse=True)}

        return providers

    async def on_option_selected(self, option: Option) -> None:
        provider_selected = self.app.providers[option.prompt]
        self.app.active_provider = provider_selected
        if self.app.fullscreen_mode:
            self.screen.maximize(self.app.navigation_resources)
        await self.app.navigation_resources.load_provider_resources(provider_selected)
