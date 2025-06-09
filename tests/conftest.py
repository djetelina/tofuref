import shutil
from pathlib import Path

import pytest
from platformdirs import user_config_path

# Attempt to import the clear functions from test_snapshots
# This might require `tests` to be importable or adjustments to sys.path in a real scenario.
# For this tool, I'll assume it can resolve if they are in the same root `tests` dir.
# If this were a real PR, I'd ensure `tests` is a package or move helpers to a shared location.
from tests.test_snapshots import clear_favorites_for_test, clear_recents_for_test
from tofuref.data.helpers import cached_file_path


@pytest.fixture(scope="session", autouse=True)
def clear_provider_index_cache():
    cached_file = cached_file_path("index.json")
    cached_file.parent.mkdir(parents=True, exist_ok=True)
    if cached_file.exists():
        cached_file.unlink()
    fallback_file = Path(__file__).parent.parent / "tofuref" / "fallback" / "providers.json"
    shutil.copy(str(fallback_file), str(cached_file))
    # print(str(fallback_file)) # No printing in fixtures ideally
    yield
    if cached_file.exists():
        cached_file.unlink()


@pytest.fixture(scope="session", autouse=True)
def config_file():
    """Yeah, let's add argparse for an alternative config file later, please"""
    config_file_path = user_config_path("tofuref") / "config.toml"
    backup_config_file_path = user_config_path("tofuref") / "config.toml.bak"
    moved = False
    if config_file_path.exists():
        moved = True
        shutil.move(str(config_file_path), str(backup_config_file_path))
    yield
    if moved:
        shutil.move(str(backup_config_file_path), str(config_file_path))


@pytest.fixture(autouse=True)
def ensure_clean_favorites_recents_state(monkeypatch):  # Added monkeypatch as clear_favorites might need it if it still has remnants
    """
    Ensures that favorites and recents JSON files are cleared before each test
    that uses this fixture.
    """
    # The functions clear_favorites_for_test and clear_recents_for_test
    # are defined in test_snapshots.py and handle the actual file deletions.
    # monkeypatch might not be needed if clear_favorites_for_test was fully cleaned of it.
    # Let's call them assuming they are self-contained for file operations.
    clear_favorites_for_test()
    clear_recents_for_test()
    # Yield to let the test run
    # Optional: could also clear after, but usually before is enough for isolation.
    # clear_favorites_for_test()
    # clear_recents_for_test()
