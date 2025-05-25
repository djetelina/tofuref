from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from tofuref.data.helpers import (
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


@dataclass
class Resource:
    name: str
    provider: "Provider"
    type: ResourceType
    _content: str | None = None

    def __lt__(self, other: "Resource") -> bool:
        return self.name < other.name

    def __gt__(self, other: "Resource") -> bool:
        return self.name > other.name

    def __str__(self):
        return f"[cyan]{self.type.value[0].upper()}[/] {self.name}"

    def __rich__(self):
        return str(self)

    def __hash__(self):
        return hash(f"{self.provider.name}_{self.type}_{self.name}")

    async def content(self):
        if self._content is None:
            doc_data = await get_registry_api(
                f"{self.provider.organization}/{self.provider.name}/{self.provider.active_version}/{self.type.value}s/{self.name}.md",
                json=False,
                log_widget=self.provider.log_widget,
            )
            _, self._content = header_markdown_split(doc_data)
        return self._content
