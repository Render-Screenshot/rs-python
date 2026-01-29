"""Tests for the CacheManager class."""

from datetime import datetime

from renderscreenshot import Client


class TestCacheGet:
    """Tests for cache.get method."""

    def test_get_cached_screenshot(self, httpx_mock):
        """Test getting a cached screenshot."""
        image_data = b"cached image data"
        httpx_mock.add_response(content=image_data)

        client = Client("rs_live_test123")
        result = client.cache.get("cache_xyz789")

        assert result == image_data
        request = httpx_mock.get_request()
        assert request.method == "GET"
        assert "/cache/cache_xyz789" in str(request.url)
        client.close()

    def test_get_returns_none_for_404(self, httpx_mock):
        """Test that get returns None for 404."""
        httpx_mock.add_response(
            status_code=404,
            json={"code": "not_found", "message": "Cache entry not found"},
        )

        client = Client("rs_live_test123")
        result = client.cache.get("cache_nonexistent")

        assert result is None
        client.close()


class TestCacheDelete:
    """Tests for cache.delete method."""

    def test_delete_cache_entry(self, httpx_mock):
        """Test deleting a cache entry."""
        httpx_mock.add_response(json={"deleted": True})

        client = Client("rs_live_test123")
        result = client.cache.delete("cache_xyz789")

        assert result is True
        request = httpx_mock.get_request()
        assert request.method == "DELETE"
        assert "/cache/cache_xyz789" in str(request.url)
        client.close()

    def test_delete_nonexistent_entry(self, httpx_mock):
        """Test deleting a nonexistent entry."""
        httpx_mock.add_response(json={"deleted": False})

        client = Client("rs_live_test123")
        result = client.cache.delete("cache_nonexistent")

        assert result is False
        client.close()


class TestCachePurge:
    """Tests for cache.purge method."""

    def test_purge_by_keys(self, httpx_mock):
        """Test purging by keys."""
        httpx_mock.add_response(json={"purged": 3, "keys": ["key1", "key2", "key3"]})

        client = Client("rs_live_test123")
        keys = ["key1", "key2", "key3"]
        result = client.cache.purge(keys)

        assert result["purged"] == 3
        assert len(result["keys"]) == 3
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert "/cache/purge" in str(request.url)
        client.close()


class TestCachePurgeUrl:
    """Tests for cache.purge_url method."""

    def test_purge_by_url_pattern(self, httpx_mock):
        """Test purging by URL pattern."""
        httpx_mock.add_response(json={"purged": 5, "keys": []})

        client = Client("rs_live_test123")
        result = client.cache.purge_url("https://mysite.com/blog/*")

        assert result["purged"] == 5
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert "/cache/purge" in str(request.url)
        client.close()


class TestCachePurgeBefore:
    """Tests for cache.purge_before method."""

    def test_purge_before_date(self, httpx_mock):
        """Test purging before a date."""
        httpx_mock.add_response(json={"purged": 100, "keys": []})

        client = Client("rs_live_test123")
        date = datetime(2024, 1, 1)
        result = client.cache.purge_before(date)

        assert result["purged"] == 100
        request = httpx_mock.get_request()
        assert request.method == "POST"
        client.close()


class TestCachePurgePattern:
    """Tests for cache.purge_pattern method."""

    def test_purge_by_storage_pattern(self, httpx_mock):
        """Test purging by storage path pattern."""
        httpx_mock.add_response(json={"purged": 50, "keys": []})

        client = Client("rs_live_test123")
        result = client.cache.purge_pattern("screenshots/2024/*")

        assert result["purged"] == 50
        request = httpx_mock.get_request()
        assert request.method == "POST"
        client.close()
