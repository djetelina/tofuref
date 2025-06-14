import os
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import Response
from platformdirs import user_config_path

from tofuref.data.bookmarks import Bookmarks
from tofuref.data.cache import cached_file_path


@pytest.fixture(scope="session", autouse=True)
def clear_provider_index_cache(mock_cache_path: Path):
    cached_file = cached_file_path("index.json")
    cached_file.parent.mkdir(parents=True, exist_ok=True)
    if cached_file.exists():
        cached_file.unlink()
    fallback_file = Path(__file__).parent.parent / "tofuref" / "fallback" / "providers.json"
    shutil.copy(str(fallback_file), str(cached_file))
    print(str(fallback_file))
    yield
    if cached_file.exists():
        cached_file.unlink()


@pytest.fixture(scope="session", autouse=True)
def config_file():
    """Yeah, let's add argparse for an alternative config file later, please"""
    config_file = user_config_path("tofuref") / "config.toml"
    backup_config_file = user_config_path("tofuref") / "config.toml.bak"
    moved = False
    if config_file.exists():
        moved = True
        shutil.move(str(config_file), str(backup_config_file))
    yield
    if moved:
        shutil.move(str(backup_config_file), str(config_file))


@pytest.fixture(scope="session")
def mock_cache_path():
    cache_dir = Path("__tests_cache__")

    def mock_user_cache_path(app_name, ensure_exists=False):
        if ensure_exists:
            cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    with patch("tofuref.data.cache.user_cache_path", side_effect=mock_user_cache_path):
        yield cache_dir
    for file in cache_dir.glob("*"):
        file.unlink()
    cache_dir.rmdir()


@pytest.fixture
def clear_mock_cache(mock_cache_path: Path):
    for file in mock_cache_path.glob("*"):
        if file.name != "index.json":
            file.unlink()


@pytest.fixture(autouse=True)
def mock_http_requests():
    async def http_get(url, **kwargs):
        responses_dir = Path(__file__).parent / "responses"
        endpoint_map = {
            "https://pypi.org/pypi/tofuref/json": responses_dir / "pypi_tofuref.json",
            "https://api.opentofu.org/registry/docs/providers/hashicorp/aws/v6.0.0-beta1/index.json": responses_dir / "aws_600beta1_index.json",
            "https://api.opentofu.org/registry/docs/providers/hashicorp/aws/v6.0.0-beta1/index.md": responses_dir / "aws_600beta1_index.md",
            "https://api.opentofu.org/registry/docs/providers/integrations/github/v6.6.0/index.json": responses_dir / "github_660_index.json",
            "https://api.opentofu.org/registry/docs/providers/integrations/github/v6.6.0/index.md": responses_dir / "github_660_index.md",
            "https://api.opentofu.org/registry/docs/providers/integrations/github/v6.5.0/index.json": responses_dir / "github_650_index.json",
            "https://api.opentofu.org/registry/docs/providers/integrations/github/v6.5.0/index.md": responses_dir / "github_650_index.md",
            "https://api.opentofu.org/registry/docs/providers/integrations/github/v6.6.0/resources/actions_environment_secret.md": responses_dir
            / "github_action_env_secret.md",
            "https://api.opentofu.org/registry/docs/providers/integrations/github/v6.6.0/resources/membership.md": responses_dir
            / "github_membership.md",
            "https://api.github.com/repos/hashicorp/terraform-provider-aws": responses_dir / "github_repo_provider_aws.json",
        }

        return Response(200, content=endpoint_map[url].read_bytes())

    with patch("httpx.AsyncClient.get", side_effect=http_get) as mock_get:
        yield


@pytest.fixture(scope="session", autouse=True)
def disable_emoji():
    """Disabling emojis for tests, because they might look different depending on the OS, terminal etc."""
    os.environ["TOFUREF_THEME_EMOJI"] = "false"
    yield
    os.environ.pop("TOFUREF_THEME_EMOJI")


@pytest.fixture(scope="session", autouse=True)
def patch_bookmarks():
    class PatchedBookmarks(Bookmarks):
        def save_to_disk(self):
            pass

        def load_from_disk(self):
            self.saved = {"providers": [], "resources": []}

    with patch("tofuref.data.bookmarks.Bookmarks", PatchedBookmarks) as patched:
        yield patched
