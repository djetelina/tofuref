from typing import cast

from textual.widgets.option_list import Option

from tofuref.data.providers import Provider
from tofuref.data.resources import Resource
from tofuref.widgets.menu_option_list_base import MenuOptionListBase


class ResourcesOptionList(MenuOptionListBase):
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

        if resources is None:
            for resource in provider.resources:
                self.add_option(resource)
        else:
            self.add_options(resources)

    async def load_provider_resources(
        self,
        provider: Provider,
    ):
        self.loading = True
        self.app.content_markdown.loading = True
        await provider.load_resources(bookmarks=self.app.bookmarks)
        self.app.content_markdown.update(await provider.overview())
        self.app.content_markdown.document.border_subtitle = f"{provider.display_name} {provider.active_version} Overview"
        self.populate(provider)
        self.focus()
        self.highlighted = 0
        self.app.content_markdown.loading = False
        self.loading = False

    async def on_option_selected(self, option: Option):
        resource_selected = cast(Resource, option.prompt)
        self.app.active_resource = resource_selected
        if self.app.fullscreen_mode:
            self.screen.maximize(self.app.content_markdown)
        self.app.content_markdown.loading = True
        was_cached = resource_selected.cached
        self.app.content_markdown.update(await resource_selected.content())
        is_cached = resource_selected.cached
        if was_cached != is_cached:
            self.replace_option_prompt_at_index(self.highlighted, option.prompt)
        self.app.content_markdown.document.border_subtitle = (
            f"{resource_selected.type.value} - {resource_selected.provider.name}_{resource_selected.name}"
        )
        self.app.content_markdown.document.focus()
        self.app.content_markdown.loading = False
