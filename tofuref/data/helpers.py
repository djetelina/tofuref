import re
from typing import Tuple, Union, Dict

import httpx
from yaml import safe_load
from yaml.scanner import ScannerError

from tofuref.widgets import log_widget


def header_markdown_split(contents: str) -> Tuple[dict, str]:
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


async def get_registry_api(endpoint: str, json=True) -> Union[Dict[str, dict], str]:
    uri = f"https://api.opentofu.org/registry/docs/providers/{endpoint}"
    async with httpx.AsyncClient() as client:
        r = await client.get(uri)

    log_widget.write(f"GET [cyan]{endpoint}[/] [bold]{r.status_code}[/]")
    if json:
        return r.json()
    else:
        return r.text
