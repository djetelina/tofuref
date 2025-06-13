from datetime import datetime
from pathlib import Path

from platformdirs import user_cache_path

from tofuref.config import config


def cached_file_path(endpoint: str, glob: bool = False) -> Path:
    """
    Args:
        endpoint: http endpoint of the registry API
        glob: Looks for glob matches in the cache directory, never use with saving into cache.

    Returns:
        Path to the cached file for a given endpoint.
        If glob is True, returns the first match, check `exists()`!.
    """
    filename = endpoint.replace("/", "_")
    if glob:
        matches = list(user_cache_path("tofuref", ensure_exists=True).glob(filename))
        if matches:
            return Path(matches[0])
    return user_cache_path("tofuref", ensure_exists=True) / filename


def save_to_cache(endpoint: str, contents: str) -> None:
    cached_file = cached_file_path(endpoint)
    cached_file.write_text(contents)


def is_provider_index_expired(file: Path) -> bool:
    """
    Provider index is mutable, we consider it expired after 31 days (unconfigurable for now)

    One request per month is not too bad (we could have static fallback for the cases where this is hit when offline).
    New providers that people actually want probably won't be showing too often, so a month should be okay.
    """
    timeout = config.index_cache_duration_days * 86400
    now = datetime.now().timestamp()
    return file == cached_file_path("index.json") and now - file.stat().st_mtime >= timeout


def get_from_cache(endpoint: str) -> str | None:
    cached_file = cached_file_path(endpoint)
    if not cached_file.exists() or is_provider_index_expired(cached_file):
        return None
    return cached_file.read_text()


def clear_from_cache(endpoint: str) -> None:
    cached_file = cached_file_path(endpoint, glob=True)
    while cached_file.exists():
        cached_file.unlink()
        cached_file = cached_file_path(endpoint, glob=True)
