import json
import logging
from collections.abc import Collection
from pathlib import Path
from typing import ClassVar, cast

from textual.binding import Binding, BindingType
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from tofuref.data.helpers import (
    add_to_recents,
    get_recents,
    get_registry_api,
    load_favorites,
    save_favorites,
)
from tofuref.data.providers import Provider
from tofuref.widgets.keybindings import VIM_OPTION_LIST_NAVIGATE

LOGGER = logging.getLogger(__name__)


class ProvidersOptionList(OptionList):
    BINDINGS: ClassVar[list[BindingType]] = [
        *OptionList.BINDINGS,
        *VIM_OPTION_LIST_NAVIGATE,
        Binding("b", "toggle_favorite", "Bookmark"),
    ]

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
            # This means we are populating all providers, not a filtered list
            # So we can update flags here
            recent_provider_ids = get_recents()
            for _p_unique_id, p_obj in self.app.providers.items():
                # Update is_recent
                if p_obj.unique_id in recent_provider_ids:
                    p_obj.is_recent = True
                else:
                    p_obj.is_recent = False  # Ensure it's reset

                # Update is_favorite
                favorites_data = load_favorites()
                if p_obj.unique_id in favorites_data["providers"]:
                    p_obj.is_favorite = True
                else:
                    p_obj.is_favorite = False  # Ensure it's reset

            # Re-sort providers based on new status (favorite, recent), then popularity
            # Note: This sorting will be complex if we want to maintain original sort within groups.
            # For now, let's rely on the fact that display_name includes the prefix
            # and OptionList might sort by that, or we sort here before creating options.
            # The previous subtask handled sorting for Resources, not Providers directly in a list.
            # Let's sort the app.providers dictionary itself before creating options.
            # This is tricky because dicts are ordered but re-sorting them based on value attributes is complex.
            # A better approach might be to sort the list of keys passed to add_option.

            provider_keys = list(self.app.providers.keys())

            # Custom sort for provider keys based on Provider object properties
            def sort_key(provider_display_name):
                provider_obj = self.app.providers[provider_display_name]
                # Sort order: Favorite, Recent, Popularity (desc)
                return (
                    not provider_obj.is_favorite,  # False (Favorite) comes before True (Not Favorite)
                    not provider_obj.is_recent,  # False (Recent) comes before True (Not Recent)
                    -provider_obj.popularity,  # Negative for descending popularity
                )

            sorted_provider_keys = sorted(provider_keys, key=sort_key)
            # 'providers' variable for option adding loop below should be these sorted keys
            provider_unique_ids_to_display = sorted_provider_keys
        else:
            # If a specific list of provider unique_ids (e.g. search results) is given
            provider_unique_ids_from_search = cast(Collection[str], providers)

            # 1. Retrieve the actual Provider objects for these names
            provider_objects_to_filter = [self.app.providers[uid] for uid in provider_unique_ids_from_search if uid in self.app.providers]

            # 2. For each of these Provider objects, ensure their is_favorite and is_recent are set
            recent_provider_ids = get_recents()
            favorites_data = load_favorites()
            for p_obj in provider_objects_to_filter:
                if p_obj.unique_id in recent_provider_ids:
                    p_obj.is_recent = True
                else:
                    p_obj.is_recent = False

                if p_obj.unique_id in favorites_data["providers"]:
                    p_obj.is_favorite = True
                else:
                    p_obj.is_favorite = False

            # 3. Sort this list of Provider objects
            # Re-use the sort_key function defined above for consistency, but adapt it for objects
            def sort_provider_objects_key(p_obj: Provider):
                return (
                    not p_obj.is_favorite,
                    not p_obj.is_recent,
                    -p_obj.popularity,
                )

            sorted_provider_objects = sorted(provider_objects_to_filter, key=sort_provider_objects_key)
            # The loop below expects unique_ids to fetch the object again, so extract them.
            provider_unique_ids_to_display = [p.unique_id for p in sorted_provider_objects]

        self.clear_options()
        # Use the count of unique IDs intended for display for the subtitle
        self.border_subtitle = f"{len(provider_unique_ids_to_display)}/{len(self.app.providers)}"
        for name_key in provider_unique_ids_to_display:
            provider_obj = self.app.providers[name_key]
            self.add_option(Option(provider_obj.display_name, id=provider_obj.unique_id))

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
                # Store by unique_id to avoid issues with display_name changes
                providers[provider.unique_id] = provider

        # Initial sort by popularity when loading the index.
        # Recents and favorites will be applied on populate.
        providers = {k: v for k, v in sorted(providers.items(), key=lambda p: p[1].popularity, reverse=True)}

        return providers

    async def on_option_selected(self, option: Option) -> None:
        # option.id is the unique_id of the provider
        provider_unique_id = cast(str, option.id)
        provider_selected = self.app.providers[provider_unique_id]

        add_to_recents(provider_selected.unique_id)
        self.app.active_provider = provider_selected  # This is used by other parts of the app
        if self.app.fullscreen_mode:
            self.screen.maximize(self.app.navigation_resources)
        await self.app.navigation_resources.load_provider_resources(provider_selected)

    def action_toggle_favorite(self) -> None:
        """Toggles the favorite status of the currently highlighted provider."""
        if self.highlighted is None:
            return

        option = self.get_option_at_index(self.highlighted)
        if option.id is None:  # Should not happen if populated correctly
            LOGGER.error("Highlighted option has no ID for toggling favorite.")
            return

        provider_unique_id = cast(str, option.id)
        provider_obj = self.app.providers.get(provider_unique_id)

        if not provider_obj:
            LOGGER.error(f"Provider with ID {provider_unique_id} not found for toggling favorite.")
            return

        favorites_data = load_favorites()
        if provider_unique_id in favorites_data["providers"]:
            favorites_data["providers"].remove(provider_unique_id)
            provider_obj.is_favorite = False
            self.app.notify(f"Removed {provider_obj.unique_id} from favorites.")
        else:
            favorites_data["providers"].append(provider_unique_id)
            provider_obj.is_favorite = True
            self.app.notify(f"Added {provider_obj.unique_id} to favorites ⭐.")

        save_favorites(favorites_data)
        self.populate()  # Re-populate to reflect sort changes and display name update
        # Try to keep the same item highlighted if possible
        # This is tricky because the list re-sorts. A simple approach:
        try:
            # Find new index of the item
            new_index = -1
            for i, opt_id in enumerate(self._option_ids):  # _option_ids is internal but stores IDs
                if opt_id == provider_unique_id:
                    new_index = i
                    break
            if new_index != -1:
                self.highlighted = new_index
        except Exception:  # Catch any error if _option_ids is not as expected or item not found
            pass
