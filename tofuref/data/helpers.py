import json as jsonlib
import logging
from typing import Any

import httpx

from tofuref import __version__
from tofuref.config import config
from tofuref.data.cache import cached_file_path, get_from_cache, save_to_cache

LOGGER = logging.getLogger(__name__)

CODEBLOCK_REGEX = r"^```([a-z]+)\n([\s\S]*?)^```"


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
    LOGGER.info(f"Cache miss for {endpoint}")
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
    LOGGER.info(f"Saving {endpoint} to cache")
    save_to_cache(endpoint, r.text)

    return r.json() if json else r.text
