from dataclasses import field, dataclass
from typing import Dict, TYPE_CHECKING


if TYPE_CHECKING:
    from tofuref.data.providers import Provider


@dataclass
class Registry:
    providers: Dict[str, "Provider"] = field(default_factory=dict)


registry = Registry()
