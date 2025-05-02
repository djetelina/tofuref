from dataclasses import field, dataclass
from typing import Dict, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tofuref.data.providers import Provider


@dataclass
class Registry:
    """Not just for providers, so kinda also application state"""

    fullscreen_mode: bool = False
    providers: Dict[str, "Provider"] = field(default_factory=dict)
    active_provider: Optional["Provider"] = None


registry = Registry()
