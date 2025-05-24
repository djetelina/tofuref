import shutil
from pathlib import Path

import pytest
from xdg_base_dirs import xdg_config_home

from tofuref.data.helpers import cached_file_path


@pytest.fixture(scope="session", autouse=True)
def clear_provider_index_cache():
    cached_file = cached_file_path("index.json")
    cached_file.parent.mkdir(parents=True, exist_ok=True)
    if cached_file.exists():
        cached_file.unlink()
    fallback_file = Path(__file__).parent.parent / "tofuref" / "fallback" / "providers.json"
    shutil.copy(str(fallback_file), str(cached_file))
    print(str(fallback_file))
    yield
    if cached_file.exists():
        cached_file.unlink()


@pytest.fixture(scope="session", autouse=True)
def config_file():
    """Yeah, let's add argparse for an alternative config file later, please"""
    config_file = xdg_config_home() / "tofuref" / "config.toml"
    backup_config_file = xdg_config_home() / "tofuref" / "config.toml.bak"
    moved = False
    if config_file.exists():
        moved = True
        shutil.move(str(config_file), str(backup_config_file))
    yield
    if moved:
        shutil.move(str(backup_config_file), str(config_file))
