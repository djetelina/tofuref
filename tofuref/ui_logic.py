from typing import Optional, List, cast, Collection

from tofuref.data.resources import Resource
from tofuref.data.providers import Provider
from tofuref.data.registry import registry
from tofuref.widgets import (
    ResourcesOptionList,
    ProvidersOptionList,
    ContentWindow,
)


async def load_provider_resources(
    provider: Provider,
    navigation_resources: ResourcesOptionList = None,
    content_markdown: ContentWindow = None,
):
    if navigation_resources is None or content_markdown is None:
        return

    navigation_resources.loading = True
    content_markdown.loading = True
    await provider.load_resources()
    content_markdown.update(await provider.overview())
    content_markdown.document.border_subtitle = (
        f"{provider.display_name} {provider.active_version} Overview"
    )
    populate_resources(provider, navigation_resources=navigation_resources)
    navigation_resources.focus()
    navigation_resources.highlighted = 0
    content_markdown.loading = False
    navigation_resources.loading = False


def populate_providers(
    providers: Optional[Collection[str]] = None,
    navigation_providers: ProvidersOptionList = None,
) -> None:
    if navigation_providers is None:
        return

    if providers is None:
        providers = registry.providers.keys()
    providers = cast(Collection[str], providers)
    navigation_providers.clear_options()
    navigation_providers.border_subtitle = f"{len(providers)}/{len(registry.providers)}"
    for name in providers:
        navigation_providers.add_option(name)


def populate_resources(
    provider: Optional[Provider] = None,
    resources: Optional[List[Resource]] = None,
    navigation_resources: ResourcesOptionList = None,
) -> None:
    if navigation_resources is None:
        return

    navigation_resources.clear_options()
    if provider is None:
        return
    navigation_resources.border_subtitle = (
        f"{provider.organization}/{provider.name} {provider.active_version}"
    )

    if resources is None:
        for resource in provider.resources:
            navigation_resources.add_option(resource)
    else:
        navigation_resources.add_options(resources)
