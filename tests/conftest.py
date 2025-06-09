import shutil
from pathlib import Path

import pytest
from platformdirs import user_config_path

from tofuref.data.helpers import cached_file_path

# Removed: from tests.test_snapshots import clear_favorites_for_test, clear_recents_for_test
# as these will be handled by tmp_path based fixtures for cache files.


@pytest.fixture(scope="session", autouse=True)
def clear_provider_index_cache():
    # This fixture seems to manage a real cache file, not a temp one for tests.
    # It copies a fallback to where the app expects the index.
    # This should be fine to keep as is, as it's about providing a known index state.
    cached_file = cached_file_path("index.json")
    cached_file.parent.mkdir(parents=True, exist_ok=True)
    if cached_file.exists():
        cached_file.unlink()
    fallback_file = Path(__file__).parent.parent / "tofuref" / "fallback" / "providers.json"
    shutil.copy(str(fallback_file), str(cached_file))
    yield
    if cached_file.exists():
        cached_file.unlink()


@pytest.fixture(scope="session", autouse=True)
def config_file():
    """Manages the main config.toml file, backing it up and restoring."""
    config_file_path = user_config_path("tofuref") / "config.toml"
    backup_config_file_path = user_config_path("tofuref") / "config.toml.bak"
    moved = False
    if config_file_path.exists():
        moved = True
        shutil.move(str(config_file_path), str(backup_config_file_path))
    yield
    if moved:
        shutil.move(str(backup_config_file_path), str(config_file_path))


@pytest.fixture
def temp_favorites_file(tmp_path: Path) -> Path:
    """Create a temporary favorites.json file and yield its path."""
    # tmp_path ensures this is a unique temp dir per test function
    return tmp_path / "favorites.json"


@pytest.fixture
def temp_recents_file(tmp_path: Path) -> Path:
    """Create a temporary recents.json file and yield its path."""
    return tmp_path / "recents.json"


@pytest.fixture(autouse=True)
def mock_cache_files_paths(monkeypatch, temp_favorites_file: Path, temp_recents_file: Path):
    """
    Monkeypatches the paths for FAVORITES_CACHE_FILE and RECENTS_CACHE_FILE
    in tofuref.data.helpers to use temporary files for each test.
    This ensures test isolation for favorites and recents state.
    """
    monkeypatch.setattr("tofuref.data.helpers.FAVORITES_CACHE_FILE", temp_favorites_file)
    monkeypatch.setattr("tofuref.data.helpers.RECENTS_CACHE_FILE", temp_recents_file)
    # The yielded paths (temp_favorites_file, temp_recents_file) will be empty
    # at the start of each test that uses this autouse fixture, because tmp_path
    # provides a fresh directory. Any files written by tests will be cleaned up
    # automatically when tmp_path is torn down.
    # No explicit yield needed here as monkeypatch handles its own teardown.
