from datetime import datetime

from anyio import Path
from platformdirs import user_cache_path

from tofuref.config import config


def get_cache_path() -> Path:
    """Gets the user cache path converted to Path"""
    # This can't be a variable because pytest doesn't like that.
    # And we leave ensure_exists synchronous, because it doesn't matter really
    # (The real reason is it's also in the default factory of bookmarks, so who knows what gets called first)
    return Path(user_cache_path("tofuref", ensure_exists=True))


async def cached_file_path(endpoint: str, glob: bool = False) -> Path:
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
        matches = [p async for p in get_cache_path().glob(filename)]
        if matches:
            return Path(matches[0])
    return get_cache_path() / filename


async def save_to_cache(endpoint: str, contents: str) -> None:
    if not config.disable_cache:
        cached_file = await cached_file_path(endpoint)
        await cached_file.write_text(contents)


async def is_provider_index_expired(file: Path) -> bool:
    """
    Provider index is mutable, we consider it expired after 31 days (unconfigurable for now)

    One request per month is not too bad (we could have static fallback for the cases where this is hit when offline).
    New providers that people actually want probably won't be showing too often, so a month should be okay.
    """
    timeout = config.index_cache_duration_days * 86400
    now = datetime.now().timestamp()
    return file == await cached_file_path("index.json") and now - (await file.stat()).st_mtime >= timeout


async def get_from_cache(endpoint: str) -> str | None:
    """Loads from cache, unless the provider index is expired or cache is disabled in config"""
    cached_file = await cached_file_path(endpoint)
    if not await cached_file.exists() or await is_provider_index_expired(cached_file) or config.disable_cache:
        return None
    return await cached_file.read_text()


async def clear_from_cache(endpoint: str) -> None:
    """Removes all cached files (for all versions if given with a wildcard) for a given endpoint"""
    cached_file = await cached_file_path(endpoint, glob=True)
    while await cached_file.exists():
        await cached_file.unlink()
        # Load another
        cached_file = await cached_file_path(endpoint, glob=True)


async def get_cached_providers() -> list[str]:
    """For optimized marking of cached providers"""
    cached = [f.stem async for f in get_cache_path().glob("*_index.json")]
    return [f"{c.split('_')[0]}/{c.split('_')[1]}" for c in cached]


async def get_cached_resources(organization, name, version) -> list[str]:
    """For optimized marking of cached resources"""
    cached = [f.stem async for f in get_cache_path().glob(f"{organization}_{name}_{version}_*_*.md")]
    return [f"{c.split('_')[3]}/{'_'.join(c.split('_')[4:]).split('.')[0]}" for c in cached]
