from tofuref.data.resources import ResourceType
from tofuref.main import TofuRefApp, _parse_lookup_resource
from tofuref.startup import StartupTarget


def test_parse_lookup_resource():
    assert _parse_lookup_resource("github_repository") == ("github", "repository")
    assert _parse_lookup_resource("aws_instance") == ("aws", "instance")
    assert _parse_lookup_resource("repository") == (None, "repository")
    assert _parse_lookup_resource("aws") == (None, "aws")


def test_parse_lookup_resource_single_underscore():
    result = _parse_lookup_resource("test_resource")
    assert result == ("test", "resource")


async def test_cli_resource_auto_lookup(mock_cache_path, mock_http_requests, patch_bookmarks):
    app = TofuRefApp(startup=StartupTarget(resource="github_repository"))
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.navigation_providers.highlighted is not None


async def test_cli_provider_and_resource(mock_cache_path, mock_http_requests, patch_bookmarks):
    app = TofuRefApp(startup=StartupTarget(provider="integrations/github", resource="repository"))
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.active_provider is not None


async def test_cli_data_auto_lookup(mock_cache_path, mock_http_requests, patch_bookmarks):
    app = TofuRefApp(startup=StartupTarget(data="github_actions_environment_secrets"))
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.navigation_providers.highlighted is not None
        assert app.active_resource is not None
        assert app.active_resource.name == "actions_environment_secrets"
        assert app.active_resource.type == ResourceType.DATASOURCE


async def test_cli_provider_and_data(mock_cache_path, mock_http_requests, patch_bookmarks):
    app = TofuRefApp(startup=StartupTarget(provider="integrations/github", data="actions_environment_secrets"))
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.active_provider is not None
