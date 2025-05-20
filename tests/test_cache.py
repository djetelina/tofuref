from tofuref.data.helpers import get_from_cache, save_to_cache


def test_cache_the_same():
    save_to_cache("test", "test")
    assert get_from_cache("test") == "test"
