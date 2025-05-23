from typing import Optional, List

from textual.widgets import OptionList
from textual.widgets.option_list import Option
from tofuref.data.resources import Resource
from tofuref.data.providers import Provider


class ResourcesOptionList(OptionList):
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
        provider: Optional[Provider] = None,
        resources: Optional[List[Resource]] = None,
    ) -> None:
        self.clear_options()
        if provider is None:
            return
        self.border_subtitle = (
            f"{provider.organization}/{provider.name} {provider.active_version}"
        )

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
        await provider.load_resources()
        self.app.content_markdown.update(await provider.overview())
        self.app.content_markdown.document.border_subtitle = (
            f"{provider.display_name} {provider.active_version} Overview"
        )
        self.populate(provider)
        self.focus()
        self.highlighted = 0
        self.app.content_markdown.loading = False
        self.loading = False

    async def on_option_selected(self, option: Option):
        resource_selected = option.prompt
        self.app.active_resource = resource_selected
        if self.app.fullscreen_mode:
            self.screen.maximize(self.app.content_markdown)
        self.app.content_markdown.loading = True
        self.app.content_markdown.update(await resource_selected.content())
        self.app.content_markdown.document.border_subtitle = f"{resource_selected.type.value} - {resource_selected.provider.name}_{resource_selected.name}"
        self.app.content_markdown.document.focus()
        self.app.content_markdown.loading = False
