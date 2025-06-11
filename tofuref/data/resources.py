from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from textual.content import Content

from tofuref.config import config
from tofuref.data.helpers import (
    cached_file_path,
    get_registry_api,
    header_markdown_split,
)

if TYPE_CHECKING:
    from tofuref.data.providers import Provider


class ResourceType(Enum):
    RESOURCE = "resource"
    DATASOURCE = "datasource"
    GUIDE = "guide"
    FUNCTION = "function"

type_to_emoji = {
    ResourceType.RESOURCE: "📦",
    ResourceType.DATASOURCE: "🌐",
    ResourceType.GUIDE: "📚",
    ResourceType.FUNCTION: "📈",
}


@dataclass
class Resource:
    name: str
    provider: "Provider"
    type: ResourceType
    _content: str | None = None
    _cached: bool | None = None

    def __lt__(self, other: "Resource") -> bool:
        return self.name < other.name

    def __gt__(self, other: "Resource") -> bool:
        return self.name > other.name

    def visualize(self):
        icon = type_to_emoji[self.type] if config.theme.emoji else f"[$secondary]{self.type.value[0].upper()}[/]"
        cached_icon = "🕓 " if config.theme.emoji else "[$success]C[/] "
        return Content.from_markup(f"{icon} {cached_icon if self.cached else ''}{self.name}")

    def __hash__(self):
        return hash(f"{self.provider.name}_{self.type}_{self.name}")

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
            _, self._content = header_markdown_split(doc_data)
            self._cached = True
            self.provider.sort_resources()
        return self._content
