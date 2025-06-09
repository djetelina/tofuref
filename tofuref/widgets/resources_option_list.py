from typing import ClassVar, cast

from textual.binding import Binding, BindingType
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from tofuref.data.helpers import (
    add_to_recents,
    get_recents,
    load_favorites,
    save_favorites,
)
from tofuref.data.providers import Provider
from tofuref.data.resources import Resource
from tofuref.widgets.keybindings import VIM_OPTION_LIST_NAVIGATE


class ResourcesOptionList(OptionList):
    BINDINGS: ClassVar[list[BindingType]] = [
        *OptionList.BINDINGS,
        *VIM_OPTION_LIST_NAVIGATE,
        Binding("b", "toggle_favorite", "Bookmark"),
    ]

    def __init__(self, **kwargs):
        super().__init__(
            name="Resources",
            id="nav-resources",
            classes="nav-selector bordered",
            **kwargs,
        )
        self.border_title = "Resources"

    def populate(
        self,
        provider: Provider | None = None,
        resources: list[Resource] | None = None,
    ) -> None:
        self.clear_options()
        if provider is None:
            return
        self.border_subtitle = f"{provider.organization}/{provider.name} {provider.active_version}"

        # Determine the list of resources to display
        display_resources: list[Resource]
        if resources is None:
            display_resources = provider.resources
            # Update is_recent and is_favorite status only when showing all resources for a provider
            recent_resource_hashes = get_recents()
            for res in display_resources:
                res_hash = str(hash(res))
                # Update is_recent
                if res_hash in recent_resource_hashes:
                    res.is_recent = True
                else:
                    res.is_recent = False  # Ensure it's reset

                # Update is_favorite
                favorites_data = load_favorites()
                if res_hash in favorites_data["resources"]:
                    res.is_favorite = True
                else:
                    res.is_favorite = False  # Ensure it's reset

            # Resources are already sorted by __lt__ and __gt__ in the Resource class
            # which now includes favorite and recent status.
            # So, sorting the list here should apply the desired order.
            display_resources.sort()
        else:
            # If a specific list of resources (e.g., search results) is given.
            # Ensure their favorite/recent status is up-to-date and then sort this subset.
            recent_resource_hashes = get_recents()
            favorites_data = load_favorites()
            for res in resources:  # 'resources' is the input list here
                res_hash = str(hash(res))
                # Update is_recent
                if res_hash in recent_resource_hashes:
                    res.is_recent = True
                else:
                    res.is_recent = False

                # Update is_favorite
                if res_hash in favorites_data["resources"]:
                    res.is_favorite = True
                else:
                    res.is_favorite = False

            resources.sort()  # Sort the provided list in-place
            display_resources = resources

        for resource in display_resources:
            self.add_option(Option(resource, id=str(hash(resource))))

    async def load_provider_resources(
        self,
        provider: Provider,
    ):
        self.loading = True
        self.app.content_markdown.loading = True
        await provider.load_resources()
        self.app.content_markdown.update(await provider.overview())
        self.app.content_markdown.document.border_subtitle = f"{provider.display_name} {provider.active_version} Overview"
        self.populate(provider)
        self.focus()
        self.highlighted = 0
        self.app.content_markdown.loading = False
        self.loading = False

    async def on_option_selected(self, option: Option):
        resource_selected = cast(Resource, option.prompt)
        add_to_recents(str(hash(resource_selected)))
        self.app.active_resource = resource_selected
        if self.app.fullscreen_mode:
            self.screen.maximize(self.app.content_markdown)
        self.app.content_markdown.loading = True
        self.app.content_markdown.update(await resource_selected.content())
        self.app.content_markdown.document.border_subtitle = (
            f"{resource_selected.type.value} - {resource_selected.provider.name}_{resource_selected.name}"
        )
        self.app.content_markdown.document.focus()
        self.app.content_markdown.loading = False

    def action_toggle_favorite(self) -> None:
        """Toggles the favorite status of the currently highlighted resource."""
        if self.highlighted is None or self.app.active_provider is None:
            return

        option = self.get_option_at_index(self.highlighted)
        # option.prompt is the Resource object, option.id is its hash string
        resource_obj = cast(Resource, option.prompt)
        resource_hash = cast(str, option.id)

        favorites_data = load_favorites()
        if resource_hash in favorites_data["resources"]:
            favorites_data["resources"].remove(resource_hash)
            resource_obj.is_favorite = False
            self.app.notify(f"Removed {resource_obj.name} from favorites.")
        else:
            favorites_data["resources"].append(resource_hash)
            resource_obj.is_favorite = True
            self.app.notify(f"Added {resource_obj.name} to favorites ⭐.")

        save_favorites(favorites_data)
        # Re-populate to reflect sort changes and display name update
        # Crucially, this needs the current provider context
        current_provider = self.app.active_provider
        self.populate(provider=current_provider)

        # Try to keep the same item highlighted
        try:
            new_index = -1
            for i, opt_id in enumerate(self._option_ids):  # _option_ids is internal, stores IDs
                if opt_id == resource_hash:
                    new_index = i
                    break
            if new_index != -1:
                self.highlighted = new_index
        except Exception:
            pass
