from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tofuref.data.providers import Provider


@dataclass
class Resource:
    provider: "Provider"
    name: str
    description: str
    type: str
    content: str

    def __lt__(self, other: "Resource") -> bool:
        return self.name < other.name

    def __gt__(self, other: "Resource") -> bool:
        return self.name > other.name

    def __str__(self):
        return self.name

    def __rich__(self):
        return self.name

    def __hash__(self):
        return hash(f"{self.provider.name}_{self.type}_{self.name}")
