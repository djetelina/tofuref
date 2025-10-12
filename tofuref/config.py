from dataclasses import dataclass, field

from textual.constants import DEFAULT_THEME
from yaucl import BaseConfig, BaseSectionConfig


@dataclass
class ThemeConfig(BaseSectionConfig):
    ui: str = DEFAULT_THEME
    codeblocks: str = "material"
    borders_style: str = "vkey"
    emoji: bool = True


@dataclass
class Config(BaseConfig):
    """Can contain primitives or subclasses of ConfigSection"""

    theme: ThemeConfig = field(default_factory=ThemeConfig)
    http_request_timeout: float = 3.0
    index_cache_duration_days: int = 31
    markdown_length_target: int = 40_000

    # Undocumented, for development and experimentation
    show_load_times: bool = False
    disable_cache: bool = False


config = Config.init(app_name="tofuref")
