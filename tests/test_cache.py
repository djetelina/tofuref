from tofuref.data.cache import get_from_cache, save_to_cache


async def test_cache_the_same():
    await save_to_cache("test", "test")
    assert await get_from_cache("test") == "test"
