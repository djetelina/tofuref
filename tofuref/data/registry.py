from dataclasses import field, dataclass
from typing import Dict, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tofuref.data.providers import Provider


@dataclass
class Registry:
    providers: Dict[str, "Provider"] = field(default_factory=dict)
    active_provider: Optional["Provider"] = None


registry = Registry()
