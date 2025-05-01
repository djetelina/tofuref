import re
from pathlib import Path
from typing import Tuple

import appdirs
from yaml import safe_load
from yaml.scanner import ScannerError


def get_app_data_dir() -> Path:
    # Get the user data directory for this application
    data_dir = Path(appdirs.user_data_dir("tofuref"))

    # Create the directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)

    return data_dir


def get_repo_dir(repo_name: str) -> Path:
    safe_name = (
        repo_name.replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace(".", "_")
    )

    # Get the path to the repository directory
    repo_dir = get_app_data_dir() / safe_name

    return repo_dir


def header_markdown_split(contents: str) -> Tuple[dict, str]:
    header = {}
    if "---" in contents:
        split_contents = re.split(r"^---$", contents, 3, re.MULTILINE)
        try:
            header = safe_load(split_contents[1])
        except ScannerError as _:
            header = {}
        markdown_content = split_contents[2]
    else:
        markdown_content = contents
    return header, markdown_content
