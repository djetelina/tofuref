import asyncio
from typing import ClassVar, cast

from textual.binding import BindingType
from textual.widgets.option_list import Option

from tofuref.data.providers import Provider
from tofuref.data.resources import Resource
from tofuref.widgets.keybindings import BACK, LEFT_BACK
from tofuref.widgets.menu_option_list_base import MenuOptionListBase


class ResourcesOptionList(MenuOptionListBase):
    BINDINGS: ClassVar[list[BindingType]] = [*MenuOptionListBase.BINDINGS, BACK, LEFT_BACK]

    def __init__(self, **kwargs):
        super().__init__(
            name="Resources",
            id="nav-resources",
            classes="nav-selector bordered",
            **kwargs,
        )
        self.border_title = "Resources"
        self.display = False

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
            self.add_options(provider.resources)
        else:
            self.add_options(resources)

    async def load_provider_resources(
        self,
        provider: Provider,
    ):
        self.loading = True
        self.app.content_markdown.loading = True
        self.border_subtitle = "Fetching provider data..."
        self.app.content_markdown.border_subtitle = "Fetching provider overview..."
        # Let the loading paint
        await self.app.force_draw()
        loaders = [self.render_overview(provider), provider.load_resources(bookmarks=self.app.bookmarks)]
        await asyncio.gather(*loaders)
        # Let the content update behind the loading screen
        await self.app.force_draw()
        self.app.content_markdown.loading = False
        self.populate(provider)
        self.focus()
        self.highlighted = 0
        self.loading = False

    async def render_overview(self, provider):
        overview = await provider.overview()
        await self.app.content_markdown.update(overview)
        self.app.content_markdown.border_subtitle = f"{provider.display_name} {provider.active_version} Overview"
        await self.app.force_draw()

    async def on_option_selected(self, option: Option):
        resource_selected = cast(Resource, option.prompt)
        self.app.active_resource = resource_selected
        if self.app.fullscreen_mode:
            self.screen.maximize(self.app.content_markdown)
        self.app.content_markdown.loading = True
        was_cached = resource_selected.cached
        await self.app.content_markdown.update(await resource_selected.content())
        is_cached = resource_selected.cached
        if was_cached != is_cached:
            self.replace_option_prompt_at_index(self.highlighted, option.prompt)
        self.app.content_markdown.border_subtitle = (
            f"{resource_selected.type.value} - {resource_selected.provider.name}_{resource_selected.name}"
        )
        self.app.content_markdown.document.focus()
        self.app.content_markdown.loading = False

    def action_back(self):
        self.app.action_providers()
