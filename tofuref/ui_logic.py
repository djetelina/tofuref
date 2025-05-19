from typing import Optional, List, cast, Collection, Any

from tofuref.data.resources import Resource
from tofuref.data.providers import Provider
from tofuref.data.registry import registry


async def load_provider_resources(provider: Provider, app: Any = None):
    if app is None:
        return

    app.navigation_resources.loading = True
    app.content_markdown.loading = True
    await provider.load_resources()
    app.content_markdown.document.update(await provider.overview())
    app.content_markdown.document.border_subtitle = (
        f"{provider.display_name} {provider.active_version} Overview"
    )
    populate_resources(provider, app=app)
    app.navigation_resources.focus()
    app.navigation_resources.highlighted = 0
    app.content_markdown.loading = False
    app.navigation_resources.loading = False


def populate_providers(providers: Optional[Collection[str]] = None, app: Any = None) -> None:
    if app is None:
        return

    if providers is None:
        providers = registry.providers.keys()
    providers = cast(Collection[str], providers)
    app.navigation_providers.clear_options()
    app.navigation_providers.border_subtitle = f"{len(providers)}/{len(registry.providers)}"
    for name in providers:
        app.navigation_providers.add_option(name)


def populate_resources(
    provider: Optional[Provider] = None,
    resources: Optional[List[Resource]] = None,
    app: Any = None
) -> None:
    if app is None:
        return

    app.navigation_resources.clear_options()
    if provider is None:
        return
    app.navigation_resources.border_subtitle = (
        f"{provider.organization}/{provider.name} {provider.active_version}"
    )

    if resources is None:
        for resource in provider.resources:
            app.navigation_resources.add_option(resource)
    else:
        app.navigation_resources.add_options(resources)
