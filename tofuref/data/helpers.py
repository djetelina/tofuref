import json as jsonlib
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import httpx
from xdg_base_dirs import xdg_cache_home
from yaml import safe_load
from yaml.scanner import ScannerError

from tofuref import __version__

LOGGER = logging.getLogger(__name__)


def header_markdown_split(contents: str) -> Tuple[dict, str]:
    """
    Most of the documentation files from the registry have a YAML "header"
    that we mostly (at the moment) don't care about. Either way we
    check for the header and if it's there, we split it.
    """
    header = {}
    if re.match(r"^---$", contents, re.MULTILINE):
        split_contents = re.split(r"^---$", contents, 3, re.MULTILINE)
        try:
            header = safe_load(split_contents[1])
        except ScannerError as _:
            header = {}
        markdown_content = split_contents[2]
    else:
        markdown_content = contents
    return header, markdown_content

def cached_file_path(endpoint: str) -> Path:
    return xdg_cache_home() / "tofuref" / endpoint.replace('/', '_')

def save_to_cache(endpoint: str, contents: str) -> None:
    cached_file = cached_file_path(endpoint)
    cached_file.parent.mkdir(parents=True, exist_ok=True)
    with cached_file.open('w') as f:
        f.write(contents)

def is_provider_index_expired(file: Path, timeout: int=31*86400) -> bool:
    """
    Provider index is mutable, we consider it expired after 31 days (unconfigurable for now)

    One request per month is not too bad (we could have static fallback for the cases where this is hit when offline).
    New providers that people actually want probably won't be showing too often, so a month should be okay.
    """
    now = datetime.now().timestamp()
    if file == cached_file_path("index.json") and now - file.stat().st_mtime >= timeout:
        return True
    return False

def get_from_cache(endpoint: str) -> Optional[str]:
    cached_file = cached_file_path(endpoint)
    if not cached_file.exists() or is_provider_index_expired(cached_file):
        return None
    with cached_file.open('r') as f:
        return f.read()


async def get_registry_api(
    endpoint: str, json: bool = True, log_widget: Optional[Any] = None
) -> Union[Dict[str, dict], str]:
    """
    Sends GET request to opentofu providers registry to a given endpoint
    and returns the response either as a JSON or as a string. It also "logs" the request.

    Local cache is used to save/retrieve API responses.
    """
    uri = f"https://api.opentofu.org/registry/docs/providers/{endpoint}"
    if cached_content := get_from_cache(endpoint):
        LOGGER.info(f"Using cached file for {endpoint}")
        if log_widget is not None:
            log_widget.write(f"GET [cyan]{endpoint}[/] [bold]from cache[/]")
        return jsonlib.loads(cached_content) if json else cached_content
    LOGGER.debug("Starting async client")
    async with httpx.AsyncClient(
        headers={"User-Agent": f"tofuref v{__version__}"}
    ) as client:
        LOGGER.debug("Client started, sending request")
        try:
            r = await client.get(uri)
            LOGGER.debug("Request sent, response received")
        except Exception as e:
            LOGGER.error("Something went wrong", exc_info=e)
            if log_widget is not None:
                log_widget.write(f"Something went wrong: {e}")
            return ""

    if log_widget is not None:
        log_widget.write(f"GET [cyan]{endpoint}[/] [bold]{r.status_code}[/]")

    # Saving as text, because we are loading JSON if desired during cache hit
    save_to_cache(endpoint, r.text)

    return r.json() if json else r.text
