from collections.abc import Iterable
from dataclasses import dataclass

from tofuref.data.providers import Provider


@dataclass
class StartupTarget:
    provider: str | None = None
    resource: str | None = None
    data: str | None = None


def find_best_provider(prefix: str, providers: Iterable[Provider]) -> Provider | None:
    prefix = prefix.lower()
    matches = [p for p in providers if prefix in p.name.lower()]
    if not matches:
        return None
    matches.sort(key=lambda x: (-x.bookmarked, -x.cached, -x.popularity))
    return matches[0]
