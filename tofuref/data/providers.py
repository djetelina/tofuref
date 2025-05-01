import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional
from asyncio import subprocess

from tofuref.data.helpers import get_repo_dir, header_markdown_split
from tofuref.data.resources import Resource


@dataclass
class Provider:
    organization: str
    name: str
    repository_url: str
    version: str
    index: str = "This provider doesn't have an index"
    ready: bool = False
    _version: str = field(init=False)
    docs_dir: Optional[Path] = None
    resource_dir: Optional[Path] = None
    resources: Dict[str, Resource] = field(default_factory=dict)
    data_sources_dir: Optional[Path] = None
    data_sources: Dict[str, Resource] = field(default_factory=dict)

    @property
    def repo_dir(self) -> Path:
        return get_repo_dir(f"{self.organization}_{self.name}_{self.version}")

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value
        self.ready = False

    async def load_resources(self):
        if not self.ready:
            await self.ensure_repo()
            self._find_docs()
            self._extract_docs()
            self.ready = True

    async def ensure_repo(self):

        if self.repo_dir.exists() and (self.repo_dir / ".git").exists():
            # We checked out a specific version, that is immutable
            # We could have checked self.ready technically, but due to version let's leave it like this :)
            return
        else:
            self.repo_dir.parent.mkdir(parents=True, exist_ok=True)
            # TODO --single-branch --branch TAG
            clone = await subprocess.create_subprocess_exec(
                "git",
                "clone",
                "--depth",
                "1",
                self.repository_url,
                str(self.repo_dir),
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            await clone.wait()

    def _find_docs(self):
        # Need to check website first, because docs can be used for repo docs (e.g. opentofu/aws)
        self.docs_dir = (
            self.repo_dir / "website" / "docs"
            if (self.repo_dir / "website" / "docs").exists()
            else self.repo_dir / "docs"
        )
        possible_resources = {
            "long": self.docs_dir / "resources",
            "short": self.docs_dir / "r",
            "cdk_py_long": self.docs_dir / "cdktf" / "python" / "resources",
            "cdk_ts_long": self.docs_dir / "cdktf" / "typescript" / "resources",
            "cdk_py_short": self.docs_dir / "cdktf" / "python" / "r",
            "cdk_ts_short": self.docs_dir / "cdktf" / "typescript" / "r",
        }
        docs = [k for k, v in possible_resources.items() if v.exists()]
        if not docs:
            # Giving up for now. In theory provider can have 0 resources and some data sources, or even just functions, but let's not worry about it for now
            return
        docs_format = docs[0]
        data_sources_subdir_name = "data-sources" if "long" in docs_format else "d"
        self.resources_dir = possible_resources[docs_format]
        self.data_sources_dir = self.resources_dir.parent / data_sources_subdir_name
        if not self.data_sources_dir.exists():
            self.data_sources_dir = None

    def _extract_docs(self):
        for f in self.docs_dir.iterdir():
            if "index" in f.name:
                _, self.index = header_markdown_split(f.read_text())
        resource_types = {
            "resource": {
                "dir": self.resources_dir,
                "target": self.resources,
            },
            "data_source": {
                "dir": self.data_sources_dir,
                "target": self.data_sources,
            },
        }
        for resource_type, info in resource_types.items():
            if info["dir"] is None:
                continue
            for file in info["dir"].iterdir():
                if file.suffix not in [".md", ".markdown"]:
                    continue
                contents = file.read_text()
                header, markdown_content = header_markdown_split(contents)
                real_stem = file.stem.replace(".html", "")
                info["target"][real_stem] = Resource(
                    provider=self,
                    name=real_stem,
                    description=header.get("description", ""),
                    type=resource_type,
                    content=markdown_content,
                )


def populate_providers(registry_dir) -> Dict[str, Provider]:
    providers = {}

    providers_dir = registry_dir / "providers"
    if not providers_dir.exists():
        return providers

    for first_level_dir in providers_dir.iterdir():
        for organization in first_level_dir.iterdir():
            for provider_file in organization.iterdir():
                if provider_file.is_dir():
                    # Fuck them, okay?
                    continue
                name = provider_file.name.replace(".json", "")
                full_name = f"{organization.stem}/{name}"

                with open(provider_file, "r") as f:
                    versions_data = json.load(f)

                repo_url = versions_data["versions"][0]["shasums_url"].split(
                    "releases"
                )[0]

                providers[full_name] = Provider(
                    organization=organization.stem,
                    name=name,
                    resources={},
                    data_sources={},
                    # Let's assume they are ordered for now
                    version=versions_data["versions"][0]["version"],
                    ready=False,
                    repository_url=repo_url,
                )

    return providers
