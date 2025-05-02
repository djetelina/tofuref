from dataclasses import dataclass, field
from typing import Dict, Optional, List
from rich.json import JSON as RICH_JSON
import json

from tofuref.data.resources import Resource, ResourceType
from tofuref.data.helpers import (
    get_registry_api,
    header_markdown_split,
)


@dataclass
class Provider:
    organization: str
    name: str
    description: str
    fork_count: int
    blocked: bool
    popularity: int
    _overview: Optional[str] = None
    _active_version: Optional[str] = None
    versions: List[Dict[str, str]] = field(default_factory=list)
    fork_of: Optional[str] = None
    raw_json: Optional[dict] = None
    resources: List[Resource] = field(default_factory=list)
    datasources: List[Resource] = field(default_factory=list)
    functions: List[Resource] = field(default_factory=list)
    guides: List[Resource] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict) -> "Provider":
        return cls(
            organization=data["addr"]["namespace"],
            name=data["addr"]["name"],
            description=data["description"],
            fork_count=data["fork_count"],
            blocked=data["is_blocked"],
            popularity=data["popularity"],
            versions=data["versions"],
            fork_of=data.get("fork_of", {}).get("display"),
            raw_json=data,
        )

    @property
    def display_name(self) -> str:
        return f"{self.organization}/{self.name}"

    @property
    def active_version(self):
        if self._active_version is None:
            self._active_version = self.versions[0]["id"]
        return self._active_version

    @active_version.setter
    def active_version(self, value):
        self._active_version = value
        self.resources = []
        self._overview = None

    @property
    def _endpoint(self) -> str:
        return f"{self.organization}/{self.name}/{self.active_version}"

    async def overview(self):
        if self._overview is None:
            self._overview = await get_registry_api(
                f"{self._endpoint}/index.md", json=False
            )
            _, self._overview = header_markdown_split(self._overview)
        return self._overview

    async def load_resources(self):
        if self.resources:
            return
        resource_data = await get_registry_api(
            f"{self.organization}/{self.name}/{self.active_version}/index.json"
        )
        for g in sorted(resource_data["docs"]["guides"], key=lambda x: x["name"]):
            self.resources.append(Resource(g["name"], self, type=ResourceType.GUIDE))

        for r in sorted(resource_data["docs"]["resources"], key=lambda x: x["name"]):
            self.resources.append(Resource(r["name"], self, type=ResourceType.RESOURCE))
        for d in sorted(resource_data["docs"]["datasources"], key=lambda x: x["name"]):
            self.resources.append(
                Resource(d["name"], self, type=ResourceType.DATASOURCE)
            )
        for f in sorted(resource_data["docs"]["functions"], key=lambda x: x["name"]):
            self.resources.append(Resource(f["name"], self, type=ResourceType.FUNCTION))

    def __rich__(self):
        return RICH_JSON(
            json.dumps(
                {
                    k: v
                    for k, v in self.__dict__.items()
                    if k not in ["raw_json", "versions"]
                }
            )
        )


async def populate_providers() -> Dict[str, Provider]:
    providers = {}

    data = await get_registry_api("index.json")

    for provider_json in data["providers"]:
        provider = Provider.from_json(provider_json)
        filter_in = (
            provider.versions,
            not provider.blocked,
            (not provider.fork_of or provider.organization == "opentofu"),
            provider.organization not in ["terraform-providers"],
        )
        if all(filter_in):
            providers[provider.display_name] = provider

    providers = {
        k: v
        for k, v in sorted(
            providers.items(), key=lambda p: p[1].popularity, reverse=True
        )
    }

    return providers
