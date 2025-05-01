import os
from dataclasses import field, dataclass
from pathlib import Path
from typing import Dict, TYPE_CHECKING
from asyncio import subprocess

from tofuref.data.helpers import get_repo_dir

if TYPE_CHECKING:
    from tofuref.data.providers import Provider


@dataclass
class Registry:
    providers: Dict[str, "Provider"] = field(default_factory=dict)


registry = Registry()


async def ensure_registry() -> Path:
    registry_dir = get_repo_dir("opentofu_registry")
    registry_url = "https://github.com/opentofu/registry.git"

    if registry_dir.exists() and (registry_dir / ".git").exists():
        cwd = os.getcwd()
        os.chdir(registry_dir)

        await subprocess.create_subprocess_exec(
            "git",
            "pull",
            "--rebase",
            stdout=subprocess.PIPE,
        )
        os.chdir(cwd)
    else:
        registry_dir.parent.mkdir(parents=True, exist_ok=True)
        await subprocess.create_subprocess_exec(
            "git",
            "clone",
            "--depth",
            "1",
            registry_url,
            str(registry_dir),
            stdout=subprocess.PIPE,
        )
    return registry_dir
