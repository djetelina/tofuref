import json
from dataclasses import dataclass, field
from typing import Literal

from anyio import Path
from platformdirs import user_cache_path

KIND_TYPE = Literal["resources", "providers"]


@dataclass
class Bookmarks:
    saved: dict[KIND_TYPE, list[str]] | None = None
    folder_path: Path = field(default_factory=lambda: Path(user_cache_path("tofuref", ensure_exists=True)))
    filename: str = "bookmarks.json"

    async def async_post_init(self):
        await self.load_from_disk()

    @property
    def path(self) -> Path:
        return self.folder_path / self.filename

    def check(self, kind: KIND_TYPE, identifier: str) -> bool:
        return identifier in self.saved[kind]

    async def add(self, kind: KIND_TYPE, identifier: str):
        if not self.check(kind, identifier):
            self.saved[kind].append(identifier)
            await self.save_to_disk()

    async def remove(self, kind: KIND_TYPE, identifier: str):
        if self.check(kind, identifier):
            self.saved[kind].remove(identifier)
            await self.save_to_disk()

    async def save_to_disk(self):
        await self.path.write_text(json.dumps(self.saved))

    async def load_from_disk(self):
        if not await self.path.exists():
            self.saved = {
                "providers": [],
                "resources": [],
            }
        else:
            self.saved = json.loads(await self.path.read_text())
