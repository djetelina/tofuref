from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Literal

import frontmatter
from textual.content import Content

from tofuref.config import config
from tofuref.data import emojis
from tofuref.data.cache import cached_file_path, clear_from_cache
from tofuref.data.helpers import (
    get_registry_api,
)
from tofuref.data.meta import Item

if TYPE_CHECKING:
    from tofuref.data.providers import Provider


class ResourceType(Enum):
    RESOURCE = "resource"
    DATASOURCE = "datasource"
    GUIDE = "guide"
    FUNCTION = "function"


@dataclass
class Resource(Item):
    name: str
    provider: "Provider"
    type: ResourceType
    _content: str | None = None
    _cached: bool | None = None
    _title: str | None = None
    bookmarked: bool = False
    kind: Literal["resources"] = "resources"

    def __lt__(self, other: "Resource") -> bool:
        return self.name < other.name

    def __gt__(self, other: "Resource") -> bool:
        return self.name > other.name

    @property
    def display_name(self):
        return self._title if self._title is not None else self.name

    def visualize(self):
        cached_icon = emojis.CACHE if config.theme.emoji else "[$success]C[/] "
        bookmark_icon = emojis.BOOKMARK if config.theme.emoji else "[$success]B[/] "
        if self.bookmarked:
            prefix = bookmark_icon
        elif self.cached:
            prefix = cached_icon
        else:
            prefix = ""
        resource_icon = emojis.RESOURCE_TYPE[self.type.value] if config.theme.emoji else f"[$secondary]{self.type.value[0].upper()}[/]"
        return Content.from_markup(f"{resource_icon} {prefix}{self.display_name}")

    @property
    def identifying_name(self):
        return f"{self.provider.name}_{self.type.value}_{self.name}"

    def __hash__(self):
        return hash(self.identifying_name)

    @property
    def endpoint(self) -> str:
        return f"{self.provider.organization}/{self.provider.name}/{self.provider.active_version}/{self.type.value}s/{self.name}.md"

    @property
    def cached(self) -> bool:
        if self._cached is None:
            return cached_file_path(self.endpoint.replace(self.provider.active_version, "*"), glob=True).exists()
        return self._cached

    async def content(self):
        if self._content is None:
            doc_data = await get_registry_api(
                self.endpoint,
                json=False,
                log_widget=self.provider.log_widget,
            )
            doc = frontmatter.loads(doc_data)
            self._content = doc.content
            if self.type == ResourceType.GUIDE:
                # noinspection PyTypeChecker
                self._title = doc.metadata["page_title"]
            self._cached = True
        return self._content

    def clear_from_cache(self) -> None:
        if self.cached:
            clear_from_cache(self.endpoint)
            self._cached = False
