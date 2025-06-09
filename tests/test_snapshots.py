import json  # For RECENTS_CACHE_FILE, though save_recents handles it
import os
from unittest.mock import patch

import pytest  # Not strictly needed if pytestmark is removed and no other pytest features used directly here

# config import is kept for now, in case other tests use it, though not for favorites.
from tofuref.config import config
from tofuref.data.helpers import save_favorites as save_favorites_to_file

# RECENTS_CACHE_FILE and FAVORITES_CACHE_FILE are no longer needed here, paths are monkeypatched.
from tofuref.data.helpers import save_recents

# pytestmark for ensure_clean_favorites_recents_state is removed as mock_cache_files_paths handles it.

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


# This is the correct definition of set_recents_for_test.
# The floating save_recents(recent_ids) above it was the syntax error.
def set_recents_for_test(recent_ids: list[str]):
    save_recents(recent_ids)


# Removed clear_recents_for_test and clear_favorites_for_test.
# Their functionality is replaced by the autouse mock_cache_files_paths fixture
# in conftest.py, which ensures clean temp files for each test via tmp_path.


def setup_favorites_and_recents_state(fav_providers=None, fav_resources=None, recent_items=None):
    """
    Helper to set up favorites and recents state.
    Relies on mock_cache_files_paths fixture to ensure files are temporary and clean.
    The monkeypatch argument is removed as it's no longer needed for this function's core purpose.
    """
    # The autouse mock_cache_files_paths fixture ensures FAVORITES_CACHE_FILE
    # and RECENTS_CACHE_FILE point to clean temp files for each test.
    # So, no explicit clearing of files is needed here as tmp_path handles it.

    # Setup favorites
    providers = fav_providers if fav_providers is not None else []
    resources = fav_resources if fav_resources is not None else []
    # Only write a favorites file if there are actual favorites to set for the test.
    # Otherwise, the non-existence of the file is the "no favorites" state.
    if providers or resources:
        favorites_data = {"providers": providers, "resources": resources}
        save_favorites_to_file(favorites_data)
    # If both are empty or None, favorites.json might not be created by this function,
    # which is handled by load_favorites() returning defaults.

    # Setup recents
    # Only write a recents file if there are actual recents to set.
    if recent_items:
        set_recents_for_test(recent_items)  # save_recents is an alias for the real save_recents
    # If recent_items is None, recents.json might not be created by this function,
    # which is handled by load_recents() returning an empty list.


# Removed cleanup_favorites_and_recents_state function.
# File cleanup is automatically handled by pytest's tmp_path fixture.

# --- New Snapshot Tests for Favorites and Recents ---


def test_provider_list_with_favorites_and_recents(snap_compare, monkeypatch):  # monkeypatch might still be used by app or other test aspects
    fav_provider = KNOWN_PROVIDER_1_UNIQUE_ID
    recent_provider = KNOWN_PROVIDER_2_UNIQUE_ID

    setup_favorites_and_recents_state(fav_providers=[fav_provider], recent_items=[recent_provider])

    # try/finally for cleanup is removed as tmp_path handles it.
    assert snap_compare(APP_PATH, terminal_size=(200, 60), press=["wait:1.0"])


def test_resource_list_with_favorites_and_recents(snap_compare, monkeypatch):
    fav_resource_hash = KNOWN_RESOURCE_TIME_STATIC_HASH
    recent_resource_hash = KNOWN_RESOURCE_TIME_SLEEP_HASH

    setup_favorites_and_recents_state(
        fav_resources=[fav_resource_hash],
        recent_items=[recent_resource_hash],
    )
    press_sequence = ["t", "i", "m", "e", "enter", "enter", "wait:1.0"]
    assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence)


def test_toggle_provider_favorite_and_sort(snap_compare, monkeypatch):
    # Initial state is clean (no favorites/recents files) due to mock_cache_files_paths.
    # Explicitly calling setup_favorites_and_recents_state() with no args
    # ensures this, though it's redundant if files are guaranteed non-existent.
    setup_favorites_and_recents_state()

    press_sequence_part1 = ["r", "a", "n", "d", "o", "m", "enter", "b", "wait:1.0"]
    assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence_part1)

    press_sequence_part2 = ["b", "wait:1.0"]
    assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence_part2)


# --- Tests for Search with Favorites/Recents ---


def test_search_providers_with_favorites_and_recents(snap_compare, monkeypatch):
    # Using known providers from fallback data for predictability
    # hashicorp/aws: popularity 36283
    # hashicorp/random: popularity 2031
    # hashicorp/time: popularity 2471
    # hashicorp/null: popularity 1000

    fav_provider = "hashicorp/aws"
    recent_provider = "hashicorp/random"
    # "hashicorp/time" and "hashicorp/null" will be "other" matches

    setup_favorites_and_recents_state(fav_providers=[fav_provider], recent_items=[recent_provider])

    # Simulate typing "hashicorp" into search and submitting
    # The app starts with provider list active, so search applies to providers.
    # Need to focus search input first. Standard Textual key for focusing next focusable is Tab.
    # Or, if search input is always focusable or has a direct key:
    # Let's assume user types '/' to focus search (common pattern in this app)
    search_query = "hashicorp"
    press_sequence = ["/", *list(search_query), "enter", "wait:1.0"]

    # Expected order in search results:
    # 1. ⭐ hashicorp/aws (Favorite)
    # 2. 🕐 hashicorp/random (Recent)
    # 3. hashicorp/time (Other, higher popularity than null)
    # 4. hashicorp/null (Other, lower popularity than time)
    # Note: The test snapshot will verify the exact order and appearance.
    assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence)


def test_search_resources_with_favorites_and_recents(snap_compare, monkeypatch):
    # Using "hashicorp/time" provider. Its resources are time_date, time_offset, time_rotating, time_sleep, time_static.
    # Hashes are:
    # time_date: str(hash("time_resource_time_date")) -> not used here, but for reference
    # time_offset: KNOWN_RESOURCE_TIME_OFFSET_HASH
    # time_rotating: str(hash("time_resource_time_rotating")) -> not used here
    # time_sleep: KNOWN_RESOURCE_TIME_SLEEP_HASH
    # time_static: KNOWN_RESOURCE_TIME_STATIC_HASH

    fav_resource_hash = KNOWN_RESOURCE_TIME_STATIC_HASH  # "time_static"
    recent_resource_hash = KNOWN_RESOURCE_TIME_SLEEP_HASH  # "time_sleep"
    # Other matching resource: "time_offset" (KNOWN_RESOURCE_TIME_OFFSET_HASH)

    setup_favorites_and_recents_state(
        fav_providers=[KNOWN_PROVIDER_1_UNIQUE_ID],  # Favorite "hashicorp/time" to easily select it
        fav_resources=[fav_resource_hash],
        recent_items=[recent_resource_hash],  # Recents are global, so this could be a provider or resource ID
    )

    # Navigate to "hashicorp/time" (it's favorited, so it should be at/near the top)
    # Assuming it's the first one after initial load due to favorite status.
    press_to_provider = ["enter", "wait:0.5"]  # Select top provider (should be hashicorp/time)

    # Search for "time" within resources of hashicorp/time
    # Need to focus search input. Assume '/' works here too after navigating to resource list.
    search_query = "time"  # This will match time_static, time_sleep, time_offset, time_date, time_rotating
    press_sequence = [*press_to_provider, "/", *list(search_query), "enter", "wait:1.0"]

    # Expected order in search results for "time" within hashicorp/time:
    # 1. ⭐ R time_static (Favorite)
    # 2. 🕐 R time_sleep (Recent)
    # 3. R time_date (alphabetical)
    # 4. R time_offset (alphabetical)
    # (time_rotating would also match "time")
    # The snapshot will verify the exact content and order.
    assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence)


def test_toggle_resource_favorite_and_sort(snap_compare, monkeypatch):
    # Initial state is clean.
    setup_favorites_and_recents_state()

    press_to_provider = ["t", "i", "m", "e", "enter", "enter", "wait:0.5"]
    press_sequence_part1 = [*press_to_provider, "j", "j", "b", "wait:1.0"]
    assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence_part1)

    press_sequence_part2 = ["b", "wait:1.0"]
    assert snap_compare(APP_PATH, terminal_size=(200, 60), press=press_sequence_part2)
