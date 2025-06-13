import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from platformdirs import user_cache_path

KIND_TYPE = Literal["resources", "providers"]


@dataclass
class Bookmarks:
    saved: dict[KIND_TYPE, list[str]] | None = None
    folder_path: Path = field(default_factory=lambda: user_cache_path("tofuref", ensure_exists=True))
    filename: str = "bookmarks.json"

    def __post_init__(self):
        self.load_from_disk()

    @property
    def path(self) -> Path:
        return self.folder_path / self.filename

    def check(self, kind: KIND_TYPE, identifier: str) -> bool:
        return identifier in self.saved[kind]

    def add(self, kind: KIND_TYPE, identifier: str):
        if not self.check(kind, identifier):
            self.saved[kind].append(identifier)
            self.save_to_disk()

    def remove(self, kind: KIND_TYPE, identifier: str):
        if self.check(kind, identifier):
            self.saved[kind].remove(identifier)
            self.save_to_disk()

    def save_to_disk(self):
        self.path.write_text(json.dumps(self.saved))

    def load_from_disk(self):
        if not self.path.exists():
            self.saved = {
                "providers": [],
                "resources": [],
            }
        else:
            self.saved = json.loads(self.path.read_text())
