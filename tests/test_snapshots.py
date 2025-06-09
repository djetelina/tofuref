import json  # For RECENTS_CACHE_FILE, though save_recents handles it
import os
from unittest.mock import patch

import pytest  # Added for pytestmark

# config import might be removed if no longer needed after this refactoring
from tofuref.config import config
from tofuref.data.helpers import FAVORITES_CACHE_FILE, RECENTS_CACHE_FILE, save_recents
from tofuref.data.helpers import save_favorites as save_favorites_to_file

APP_PATH = "../tofuref/main.py"

SEARCH_GITHUB = ["s", "g", "i", "t", "h", "u", "b"]


def test_welcome(snap_compare):
    assert snap_compare(APP_PATH, terminal_size=(200, 60))


def test_welcome_fullscreen(snap_compare):
    assert snap_compare(APP_PATH)


@patch("tofuref.main.get_current_pypi_version")
@patch("tofuref.__version__", "1.0.0")
def test_welcome_update_available(mock_coro, snap_compare):
    mock_coro.return_value = "1.0.1"
    assert snap_compare(APP_PATH)


def test_toggle_fullscreen(snap_compare):
    # Result: fullscreen mode off, even though it's a small window
    assert snap_compare(APP_PATH, press=["f"])


def test_content(snap_compare):
    assert snap_compare(APP_PATH, press=["c", "pagedown"])


def test_content_toc_on(snap_compare):
    assert snap_compare(APP_PATH, press=["c", "t"])


def test_content_toc_off(snap_compare):
    assert snap_compare(APP_PATH, press=["c", "t", "t"])


def test_content_toc_submit(snap_compare):
    assert snap_compare(APP_PATH, press=["c", "t", "down", "down", "down", "down", "down", "enter"])


def test_use_none_selected(snap_compare):
    assert snap_compare(APP_PATH, press=["u"])


def test_search_github(snap_compare):
    assert snap_compare(APP_PATH, press=SEARCH_GITHUB)


def test_search_github_cancel(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "escape"])


def test_open_github(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter"])


def test_open_github_membership(snap_compare):
    assert snap_compare(
        APP_PATH,
        press=[*SEARCH_GITHUB, "enter", "enter", "s", "m", "e", "m", "b", "e", "r", "enter", "enter"],
    )


def test_back_to_providers(snap_compare):
    assert snap_compare(APP_PATH, press=["enter", "p"])


def test_provider_overview(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "c"])


def test_version_picker(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "v"])


def test_version_picker_submit(snap_compare):
    assert snap_compare(
        APP_PATH,
        press=[*SEARCH_GITHUB, "enter", "enter", "v", "down", "enter"],
    )


def test_use(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "u"])


def test_copy_selection_github_overview(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "c", "y"])


def test_copy_selection_github_overview_copy_first(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "c", "y", "enter"])


def test_vim_providers(snap_compare):
    assert snap_compare(APP_PATH, press=["j"])


def test_vim_resources(snap_compare):
    assert snap_compare(APP_PATH, press=["enter", "j"])


def test_vim_content(snap_compare):
    assert snap_compare(APP_PATH, press=["c", "j"])


def test_config_theme(snap_compare):
    os.environ["TOFUREF_THEME_UI"] = "monokai"
    os.environ["TOFUREF_THEME_CODEBLOCKS"] = "monokai"
    os.environ["TOFUREF_THEME_BORDERS_STYLE"] = "solid"
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "c", "pagedown"])
    os.environ.pop("TOFUREF_THEME_UI")
    os.environ.pop("TOFUREF_THEME_CODEBLOCKS")
    os.environ.pop("TOFUREF_THEME_BORDERS_STYLE")


# --- Helpers for Favorites and Recents ---

# It's important that these providers are in the fallback data for predictability
KNOWN_PROVIDER_1_UNIQUE_ID = "hashicorp/time"  # Small provider, good for testing
KNOWN_PROVIDER_2_UNIQUE_ID = "hashicorp/random"  # Another small one
KNOWN_PROVIDER_3_UNIQUE_ID = "hashicorp/null"  # Often used, good for variety

# For resources, we'll use resources from hashicorp/time as it's simple
# The hash is f"{self.provider.name}_{self.type}_{self.name}"
# Provider name for hashicorp/time is 'time' (from addr.name)
KNOWN_RESOURCE_TIME_STATIC_HASH = str(hash("time_resource_time_static"))
KNOWN_RESOURCE_TIME_SLEEP_HASH = str(hash("time_resource_time_sleep"))
KNOWN_RESOURCE_TIME_OFFSET_HASH = str(hash("time_resource_time_offset"))


def set_recents_for_test(recent_ids: list[str]):
    save_recents(recent_ids)


def clear_recents_for_test():
    if RECENTS_CACHE_FILE.exists():
        RECENTS_CACHE_FILE.unlink()


def clear_favorites_for_test():
    if FAVORITES_CACHE_FILE.exists():
        FAVORITES_CACHE_FILE.unlink()


def setup_favorites_and_recents_state(monkeypatch, fav_providers=None, fav_resources=None, recent_items=None):
    """Helper to set up a clean state and then desired state."""
    # Clear first
    clear_recents_for_test()
    clear_favorites_for_test()  # Deletes the favorites.json file

    # Setup favorites
    providers = fav_providers if fav_providers is not None else []
    resources = fav_resources if fav_resources is not None else []
    if fav_providers is not None or fav_resources is not None:
        favorites_data = {"providers": providers, "resources": resources}
        save_favorites_to_file(favorites_data)

    # Setup recents (remains the same)
    if recent_items:
        set_recents_for_test(recent_items)

    # No need to monkeypatch config for favorites anymore


def cleanup_favorites_and_recents_state(monkeypatch):  # monkeypatch might be removable if not used for other things
    """Helper to clean up state after a test."""
    clear_recents_for_test()
    clear_favorites_for_test()  # Deletes the favorites.json file

    # No need to monkeypatch config for favorites anymore


# --- New Snapshot Tests for Favorites and Recents ---


def test_provider_list_with_favorites_and_recents(snap_compare, monkeypatch):
    fav_provider = KNOWN_PROVIDER_1_UNIQUE_ID  # hashicorp/time
    recent_provider = KNOWN_PROVIDER_2_UNIQUE_ID  # hashicorp/random

    setup_favorites_and_recents_state(monkeypatch, fav_providers=[fav_provider], recent_items=[recent_provider])

    try:
        # The app loads providers on startup.
        # Sorting by favorite, then recent, then popularity should apply.
        # hashicorp/time (fav) should be first.
        # hashicorp/random (recent) should be second.
        # Others follow (e.g. hashicorp/null by popularity if not fav/recent)
        assert snap_compare(APP_PATH, terminal_size=(200, 60), press=["wait:1.0"])  # wait for list to process
    finally:
        cleanup_favorites_and_recents_state(monkeypatch)


def test_resource_list_with_favorites_and_recents(snap_compare, monkeypatch):
    # We will navigate to hashicorp/time provider
    # Provider "hashicorp/time" unique_id is "hashicorp/time"
    # Its resources are time_static, time_sleep, time_offset, time_rotating (from registry)
    # Hashes are calculated based on provider.name ('time'), type ('resource'), and resource name.

    fav_resource_hash = KNOWN_RESOURCE_TIME_STATIC_HASH
    recent_resource_hash = KNOWN_RESOURCE_TIME_SLEEP_HASH

    setup_favorites_and_recents_state(
        monkeypatch,
        fav_resources=[fav_resource_hash],
        recent_items=[recent_resource_hash],  # Recents list is global for providers and resources
    )

    # Navigate to hashicorp/time provider's resources
    # 1. Type "time" to filter providers
    # 2. Press Enter to select the first filtered (should be hashicorp/time)
    #    (Need to ensure it's the first, or use more specific navigation)
    #    Let's find "time" provider: 't', 'i', 'm', 'e' then Enter should usually work if it's high enough.
    #    Fallback data has "hashicorp/time" with popularity 2471.
    #    "hashicorp/random" has 2031. "hashicorp/null" has 1000.
    #    So "hashicorp/time" should be first among these if no fav/recent.
    #    If we make it favorite, it will be at the top.
    #    If we make it recent, it will be near top.
    #    Let's assume default order first, then select.
    #    Press sequence to select "hashicorp/time":
    #    - Type 't', 'i', 'm', 'e', 'Enter' (to select search box)
    #    - 'Enter' (to select the provider from list - assuming it's the first one after search)

    # Simpler navigation:
    # The test_app starts with provider list.
    # "hashicorp/time" is KNOWN_PROVIDER_1_UNIQUE_ID.
    # If we make it favorite, it will be at the top.
    # Let's make it favorite to ensure it's the first one for easy selection.
    # Or, even better, just use key navigation 'j', 'k' if we know its default position.
    # The fallback data is sorted by popularity.
    # hashicorp/terraform (99999)
    # hashicorp/aws (36000)
    # ... many others ...
    # hashicorp/time (2471) - this will be some way down.
    # Let's assume we search for it to select it.

    press_sequence = ["t", "i", "m", "e", "enter", "enter", "wait:1.0"]  # search "time", select search box, select provider

    try:
        # time_static (fav) should be first.
        # time_sleep (recent) should be second.
        # time_offset, time_rotating should follow, sorted alphabetically.
        assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence)
    finally:
        cleanup_favorites_and_recents_state(monkeypatch)


def test_toggle_provider_favorite_and_sort(snap_compare, monkeypatch):
    # Ensure KNOWN_PROVIDER_2_UNIQUE_ID (hashicorp/random) is not favorite initially
    # It has popularity 2031. hashicorp/time has 2471.
    # So 'time' is above 'random' in default sort from fallback.
    # 'hashicorp/null' (1000) is below 'random'.
    # Let's favorite 'hashicorp/random'. It should move to the top.

    provider_to_toggle = KNOWN_PROVIDER_2_UNIQUE_ID  # hashicorp/random

    setup_favorites_and_recents_state(monkeypatch)  # Clear all

    # Initial state: hashicorp/random is not favorited.
    # It should be below hashicorp/time.
    # We need to navigate to it. It might be the second or third visible.
    # Let's assume it's reachable by 'j' (down) once or twice if list is not too long.
    # Fallback: hashicorp/terraform, hashicorp/aws, hashicorp/google, hashicorp/azurerm, ... then hashicorp/time, then hashicorp/random
    # This means hashicorp/random is many items down.
    # Searching is more robust.

    # Search for "random" provider, it should be the first result. Then bookmark it.
    press_sequence_part1 = ["r", "a", "n", "d", "o", "m", "enter", "b", "wait:1.0"]  # search, select search, bookmark highlighted

    try:
        # Snapshot 1: hashicorp/random is now favorite and at the top.
        assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence_part1)

        # Part 2: Un-favorite it. It's currently highlighted and at the top.
        # Press 'b' again.
        press_sequence_part2 = ["b", "wait:1.0"]
        assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence_part2)
    finally:
        cleanup_favorites_and_recents_state(monkeypatch)


def test_toggle_resource_favorite_and_sort(snap_compare, monkeypatch):
    # Navigate to hashicorp/time
    # Then toggle favorite for 'time_sleep' resource.
    # Default order: time_offset, time_rotating, time_sleep, time_static (alphabetical for resources)

    setup_favorites_and_recents_state(monkeypatch)  # Clear all

    # Navigate to hashicorp/time provider's resources
    # Search "time", select provider
    press_to_provider = ["t", "i", "m", "e", "enter", "enter", "wait:0.5"]

    # 'time_sleep' is third in alpha sort (time_offset, time_rotating, time_sleep). So two 'j' presses.
    press_sequence_part1 = [*press_to_provider, "j", "j", "b", "wait:1.0"]  # Highlight time_sleep, bookmark

    try:
        # Snapshot 1: time_sleep is now favorite and at the top of resources for hashicorp/time.
        assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence_part1)

        # Part 2: Un-favorite it. It's currently highlighted and at the top.
        # Press 'b' again.
        press_sequence_part2 = ["b", "wait:1.0"]
        assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence_part2)
    finally:
        cleanup_favorites_and_recents_state(monkeypatch)
