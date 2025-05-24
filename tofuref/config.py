"""
I couldn't find a library that does this. Dynaconf is really
close but is intended for apps that get deployed. So
POTENTIALLY, this might be a good idea to separate into
a library.

IF this was to become a separate library, some thoughts:
* Get rid of constants
* Introduce argparse layer
* Composable layer ordering (load_from...)
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from textual.constants import DEFAULT_THEME
from xdg_base_dirs import xdg_config_home

APP_NAME: str = "tofuref"


class SectionConfig:
    """Sections in config should be subclasses of this, as it allows for some magic"""

    def update(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def update_from_env(self, section_key: str) -> None:
        """Looks for env variables that correspond to the section passed"""
        section_env_values = {}
        for key, expected_type in self.__annotations__.items():
            env_value = _get_env_value(f"{section_key}_{key}", expected_type)
            if env_value is not None:
                section_env_values[key] = env_value
        if section_env_values:
            self.update(section_env_values)


@dataclass
class ThemeConfig(SectionConfig):
    ui: str = DEFAULT_THEME
    codeblocks: str = "material"
    borders_style: str = "ascii"


# TODO having this as singleton would be great (especially for the timout that's now passed around a lot,
#  I need to check it doesn't break snapshot tests = I already broke them a few times by trying to use singletons
@dataclass
class Config:
    """Can contain primitives or subclasses of ConfigSection"""

    theme: ThemeConfig = field(default_factory=ThemeConfig)
    http_request_timeout: float = 3.0
    index_cache_duration_days: int = 31
    fullscreen_init_threshold: int = 125

    @classmethod
    def load(cls) -> "Config":
        config = cls()

        config.update_from_file()

        config.update_from_env()

        return config

    @property
    def _sections(self) -> list[str]:
        return [s for s, t in self.__annotations__.items() if isinstance(t, type) and issubclass(t, SectionConfig)]

    @property
    def file(self) -> Path:
        return xdg_config_home() / APP_NAME / "config.toml"

    def update_from_file(self) -> None:
        if self.file.exists():
            with self.file.open("rb") as f:
                config_data = tomllib.load(f)

            for key, value in config_data.items():
                if key in self._sections and isinstance(value, dict):
                    section = getattr(self, key)
                    section.update(value)
                elif hasattr(self, key):
                    setattr(self, key, value)

    def update_from_env(self) -> None:
        for key, expected_type in self.__annotations__.items():
            if key in self._sections:
                section = getattr(self, key)
                section.update_from_env(key)
            else:
                env_value = _get_env_value(key, expected_type)
                if env_value is not None:
                    setattr(self, key, env_value)


def _get_env_value(key: str, expected_type: type):
    """Gets env value (adds a prefix) and converts it to the expected type."""
    env_var_name = f"{APP_NAME}_{key}".upper()
    env_value = os.getenv(env_var_name)

    if env_value is None:
        return None

    try:
        if expected_type is bool:
            return env_value.lower() in ("true", "1", "yes", "y", "t")
        return expected_type(env_value)
    except (ValueError, TypeError) as _:
        return None
