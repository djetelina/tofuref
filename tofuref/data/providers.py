from dataclasses import dataclass, field
from typing import Any

from textual.content import Content

from tofuref.config import config
from tofuref.data.helpers import (
    cached_file_path,
    get_registry_api,
    header_markdown_split,
)
from tofuref.data.resources import Resource, ResourceType


@dataclass
class Provider:
    organization: str
    name: str
    description: str
    fork_count: int
    blocked: bool
    popularity: int
    _overview: str | None = None
    _active_version: str | None = None
    versions: list[dict[str, str]] = field(default_factory=list)
    fork_of: str | None = None
    raw_json: dict | None = None
    resources: list[Resource] = field(default_factory=list)
    datasources: list[Resource] = field(default_factory=list)
    functions: list[Resource] = field(default_factory=list)
    guides: list[Resource] = field(default_factory=list)
    log_widget: Any | None = None
    _cached: bool | None = None

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
    def active_version(self) -> str:
        if self._active_version is None:
            self._active_version = self.versions[0]["id"]
        return self._active_version

    @active_version.setter
    def active_version(self, value: str) -> None:
        self._active_version = value
        self.resources = []
        self._overview = None

    @property
    def endpoint(self) -> str:
        return f"{self.organization}/{self.name}/{self.active_version}/index.md"

    @property
    def cached(self) -> bool:
        if self._cached is None:
            return cached_file_path(self.endpoint.replace(self.active_version, "*"), glob=True).exists()
        return self._cached

    @property
    def use_configuration(self) -> str:
        return f"""    {self.name} = {{
      source  = "{self.organization}/{self.name}"
      version = "{self.active_version.lstrip("v")}"
    }}"""

    async def overview(self) -> str:
        if self._overview is None:
            self._overview = await get_registry_api(self.endpoint, json=False, log_widget=self.log_widget)
            _, self._overview = header_markdown_split(self._overview)
            self._cached = True
        return self._overview

    async def load_resources(self) -> None:
        if self.resources:
            return
        await self.reload_resources()

        self.sort_resources()

    async def reload_resources(self) -> None:
        self.resources = []
        resource_data = await get_registry_api(
            f"{self.organization}/{self.name}/{self.active_version}/index.json",
            log_widget=self.log_widget,
        )
        for g in sorted(resource_data["docs"]["guides"], key=lambda x: x["name"]):
            self.resources.append(Resource(g["name"], self, type=ResourceType.GUIDE))
        for r in sorted(resource_data["docs"]["resources"], key=lambda x: x["name"]):
            self.resources.append(Resource(r["name"], self, type=ResourceType.RESOURCE))
        for d in sorted(resource_data["docs"]["datasources"], key=lambda x: x["name"]):
            self.resources.append(Resource(d["name"], self, type=ResourceType.DATASOURCE))
        for f in sorted(resource_data["docs"]["functions"], key=lambda x: x["name"]):
            self.resources.append(Resource(f["name"], self, type=ResourceType.FUNCTION))

        self.sort_resources()

    def sort_resources(self):
        type_order = {ResourceType.GUIDE: 0, ResourceType.RESOURCE: 1, ResourceType.DATASOURCE: 2, ResourceType.FUNCTION: 3}

        self.resources.sort(key=lambda x: (-x.cached, type_order[x.type], x.name))

    def visualize(self):
        cached_icon = "🕓 " if config.theme.emoji else "[$success]C[/] "
        return Content.from_markup(f"{cached_icon if self.cached else ''}[dim italic]{self.organization}[/]/{self.name}")
