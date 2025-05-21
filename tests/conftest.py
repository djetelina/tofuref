from pathlib import Path

import pytest
import shutil

from tofuref.data.helpers import cached_file_path


@pytest.fixture(scope="session", autouse=True)
def clear_provider_index_cache():
    cached_file = cached_file_path("index.json")
    cached_file.parent.mkdir(parents=True, exist_ok=True)
    if cached_file.exists():
        cached_file.unlink()
    fallback_file = (
        Path(__file__).parent.parent / "tofuref" / "fallback" / "providers.json"
    )
    shutil.copy(str(fallback_file), str(cached_file))
    print(str(fallback_file))
    yield
    if cached_file.exists():
        cached_file.unlink()
