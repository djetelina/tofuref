import pytest

from tofuref.data.helpers import cached_file_path


@pytest.fixture(scope="session", autouse=True)
def clear_provider_index_cache():
    if cached_file_path('index.json').exists():
        cached_file_path('index.json').unlink()
