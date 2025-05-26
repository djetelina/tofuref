import json as jsonlib
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from platformdirs import user_cache_path
from yaml import safe_load
from yaml.scanner import ScannerError

from tofuref import __version__
from tofuref.config import config

LOGGER = logging.getLogger(__name__)

CODEBLOCK_REGEX = r"^```([a-z]+)\n([\s\S]*?)^```"


def header_markdown_split(contents: str) -> tuple[dict, str]:
    """
    Most of the documentation files from the registry have a YAML "header"
    that we mostly (at the moment) don't care about. Either way we
    check for the header, and if it's there, we split it.
    """
    header = {}
    if re.match(r"^---$", contents, re.MULTILINE):
        split_contents = re.split(r"^---$", contents, maxsplit=2, flags=re.MULTILINE)
        try:
            header = safe_load(split_contents[1])
        except ScannerError as _:
            header = {}
        markdown_content = split_contents[2]
    else:
        markdown_content = contents
    return header, markdown_content


def cached_file_path(endpoint: str) -> Path:
    return user_cache_path("tofuref", ensure_exists=True) / endpoint.replace("/", "_")


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


async def get_registry_api(endpoint: str, json: bool = True, log_widget: Any | None = None) -> dict[str, dict] | str:
    """
    Sends GET request to opentofu providers registry to a given endpoint
    and returns the response either as a JSON or as a string. It also "logs" the request.

    Local cache is used to save/retrieve API responses.
    """
    uri = f"https://api.opentofu.org/registry/docs/providers/{endpoint}"
    if cached_content := get_from_cache(endpoint):
        LOGGER.info(f"Using cached file for {endpoint} from {cached_file_path(endpoint)}")
        if log_widget is not None:
            log_widget.write(f"Cache hit [cyan]{cached_file_path(endpoint)}[/]")
        return jsonlib.loads(cached_content) if json else cached_content
    LOGGER.debug("Starting async client")
    async with httpx.AsyncClient(headers={"User-Agent": f"tofuref v{__version__}"}) as client:
        LOGGER.debug("Client started, sending request")
        try:
            r = await client.get(uri, timeout=config.http_request_timeout)
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
