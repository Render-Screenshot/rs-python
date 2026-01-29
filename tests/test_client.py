"""Tests for the Client class."""

from datetime import datetime, timedelta

import pytest

from renderscreenshot import Client, TakeOptions
from renderscreenshot.errors import RenderScreenshotError


class TestClientInitialization:
    """Tests for Client initialization."""

    def test_requires_api_key(self):
        """Test that API key is required."""
        with pytest.raises(ValueError, match="API key is required"):
            Client("")

    def test_accepts_api_key(self):
        """Test that client accepts API key."""
        client = Client("rs_live_test123")
        assert client is not None
        client.close()

    def test_custom_base_url(self):
        """Test custom base URL."""
        client = Client("rs_live_test123", base_url="https://api.staging.example.com")
        assert client._base_url == "https://api.staging.example.com"
        client.close()

    def test_custom_timeout(self):
        """Test custom timeout."""
        client = Client("rs_live_test123", timeout=60.0)
        assert client._timeout == 60.0
        client.close()

    def test_context_manager(self):
        """Test client as context manager."""
        with Client("rs_live_test123") as client:
            assert client is not None


class TestClientGenerateUrl:
    """Tests for generate_url method."""

    def test_generate_url_basic(self):
        """Test basic signed URL generation."""
        client = Client("rs_live_test123")
        options = TakeOptions.url("https://example.com")
        expires = datetime.now() + timedelta(hours=1)

        url = client.generate_url(options, expires)

        assert "https://api.renderscreenshot.com" in url
        assert "url=https" in url
        assert "expires=" in url
        assert "signature=" in url
        client.close()

    def test_generate_url_with_options(self):
        """Test signed URL with multiple options."""
        client = Client("rs_live_test123")
        options = (
            TakeOptions.url("https://example.com")
            .width(1200)
            .height(630)
            .preset("og_card")
            .block_ads()
        )
        expires = datetime.now() + timedelta(hours=24)

        url = client.generate_url(options, expires)

        assert "width=1200" in url
        assert "height=630" in url
        assert "preset=og_card" in url
        assert "block_ads=true" in url
        client.close()

    def test_generate_url_with_dict(self):
        """Test signed URL generation with dict config."""
        client = Client("rs_live_test123")
        config = {"url": "https://example.com", "width": 1200}
        expires = datetime.now() + timedelta(hours=1)

        url = client.generate_url(config, expires)

        assert "url=https" in url
        assert "width=1200" in url
        client.close()

    def test_generate_url_sorted_params(self):
        """Test that URL parameters are sorted alphabetically."""
        client = Client("rs_live_test123")
        options = TakeOptions.url("https://example.com").width(1200).block_ads()
        expires = datetime.now() + timedelta(hours=1)

        url = client.generate_url(options, expires)

        # block_ads should come before url, width
        block_idx = url.index("block_ads")
        url_idx = url.index("url=")
        width_idx = url.index("width=")

        assert block_idx < url_idx < width_idx
        client.close()


class TestClientTake:
    """Tests for take method with mocked HTTP."""

    def test_take_converts_options_to_params(self, httpx_mock):
        """Test that take converts TakeOptions to params."""
        httpx_mock.add_response(content=b"fake image data")

        client = Client("rs_live_test123")
        options = TakeOptions.url("https://example.com").width(1200)

        result = client.take(options)

        assert result == b"fake image data"
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert "/screenshot" in str(request.url)
        client.close()

    def test_take_accepts_dict(self, httpx_mock):
        """Test that take accepts dict config."""
        httpx_mock.add_response(content=b"fake image data")

        client = Client("rs_live_test123")
        config = {"url": "https://example.com", "width": 1200}

        result = client.take(config)

        assert result == b"fake image data"
        client.close()


class TestClientTakeJson:
    """Tests for take_json method with mocked HTTP."""

    def test_take_json_returns_metadata(self, httpx_mock):
        """Test that take_json returns metadata."""
        response_data = {
            "url": "https://cdn.example.com/screenshot.png",
            "width": 1200,
            "height": 630,
            "format": "png",
            "size": 12345,
            "cached": False,
        }
        httpx_mock.add_response(json=response_data)

        client = Client("rs_live_test123")
        options = TakeOptions.url("https://example.com").preset("og_card")

        result = client.take_json(options)

        assert result["url"] == "https://cdn.example.com/screenshot.png"
        assert result["width"] == 1200
        assert result["height"] == 630
        client.close()


class TestClientBatch:
    """Tests for batch method with mocked HTTP."""

    def test_batch_with_urls(self, httpx_mock):
        """Test batch with list of URLs."""
        response_data = {
            "id": "batch_123",
            "status": "completed",
            "total": 2,
            "completed": 2,
            "failed": 0,
            "results": [],
        }
        httpx_mock.add_response(json=response_data)

        client = Client("rs_live_test123")
        urls = ["https://example1.com", "https://example2.com"]

        result = client.batch(urls)

        assert result["id"] == "batch_123"
        assert result["status"] == "completed"
        client.close()

    def test_batch_with_urls_and_options(self, httpx_mock):
        """Test batch with URLs and shared options."""
        response_data = {
            "id": "batch_123",
            "status": "processing",
            "total": 2,
            "completed": 0,
            "failed": 0,
            "results": [],
        }
        httpx_mock.add_response(json=response_data)

        client = Client("rs_live_test123")
        urls = ["https://example1.com", "https://example2.com"]
        options = TakeOptions.url("").preset("og_card")

        result = client.batch(urls, options)

        assert result["id"] == "batch_123"
        client.close()


class TestClientGetBatch:
    """Tests for get_batch method with mocked HTTP."""

    def test_get_batch(self, httpx_mock):
        """Test getting batch status."""
        response_data = {
            "id": "batch_123",
            "status": "completed",
            "total": 2,
            "completed": 2,
            "failed": 0,
            "results": [
                {"url": "https://example1.com", "success": True},
                {"url": "https://example2.com", "success": True},
            ],
        }
        httpx_mock.add_response(json=response_data)

        client = Client("rs_live_test123")

        result = client.get_batch("batch_123")

        assert result["id"] == "batch_123"
        assert result["status"] == "completed"
        assert len(result["results"]) == 2
        client.close()


class TestClientPresets:
    """Tests for preset methods with mocked HTTP."""

    def test_presets_list(self, httpx_mock):
        """Test listing presets."""
        response_data = [
            {"id": "og_card", "name": "OG Card", "width": 1200, "height": 630},
            {"id": "twitter_card", "name": "Twitter Card", "width": 1200, "height": 600},
        ]
        httpx_mock.add_response(json=response_data)

        client = Client("rs_live_test123")

        result = client.presets()

        assert len(result) == 2
        assert result[0]["id"] == "og_card"
        client.close()

    def test_preset_single(self, httpx_mock):
        """Test getting single preset."""
        response_data = {"id": "og_card", "name": "OG Card", "width": 1200, "height": 630}
        httpx_mock.add_response(json=response_data)

        client = Client("rs_live_test123")

        result = client.preset("og_card")

        assert result["id"] == "og_card"
        assert result["width"] == 1200
        client.close()


class TestClientDevices:
    """Tests for devices method with mocked HTTP."""

    def test_devices_list(self, httpx_mock):
        """Test listing devices."""
        response_data = [
            {
                "id": "iphone_14_pro",
                "name": "iPhone 14 Pro",
                "width": 393,
                "height": 852,
                "scale": 3,
                "mobile": True,
                "user_agent": "Mozilla/5.0...",
            },
        ]
        httpx_mock.add_response(json=response_data)

        client = Client("rs_live_test123")

        result = client.devices()

        assert len(result) == 1
        assert result[0]["id"] == "iphone_14_pro"
        assert result[0]["mobile"] is True
        client.close()


class TestClientErrorHandling:
    """Tests for error handling with mocked HTTP."""

    def test_handles_400_error(self, httpx_mock):
        """Test handling 400 errors."""
        httpx_mock.add_response(
            status_code=400,
            json={"code": "invalid_url", "message": "Invalid URL provided"},
        )

        client = Client("rs_live_test123")

        with pytest.raises(RenderScreenshotError) as exc_info:
            client.take(TakeOptions.url("not-a-url"))

        assert exc_info.value.http_status == 400
        assert exc_info.value.code == "invalid_url"
        client.close()

    def test_handles_401_error(self, httpx_mock):
        """Test handling 401 errors."""
        httpx_mock.add_response(
            status_code=401,
            json={"code": "unauthorized", "message": "Invalid API key"},
        )

        client = Client("rs_live_invalid")

        with pytest.raises(RenderScreenshotError) as exc_info:
            client.take(TakeOptions.url("https://example.com"))

        assert exc_info.value.http_status == 401
        assert exc_info.value.code == "unauthorized"
        client.close()

    def test_handles_429_error_with_retry_after(self, httpx_mock):
        """Test handling 429 errors with Retry-After header."""
        httpx_mock.add_response(
            status_code=429,
            json={"code": "rate_limited", "message": "Rate limit exceeded"},
            headers={"Retry-After": "60"},
        )

        client = Client("rs_live_test123")

        with pytest.raises(RenderScreenshotError) as exc_info:
            client.take(TakeOptions.url("https://example.com"))

        assert exc_info.value.http_status == 429
        assert exc_info.value.code == "rate_limited"
        assert exc_info.value.retry_after == 60
        assert exc_info.value.retryable is True
        client.close()

    def test_handles_500_error(self, httpx_mock):
        """Test handling 500 errors."""
        httpx_mock.add_response(
            status_code=500,
            json={"code": "internal_error", "message": "Internal server error"},
        )

        client = Client("rs_live_test123")

        with pytest.raises(RenderScreenshotError) as exc_info:
            client.take(TakeOptions.url("https://example.com"))

        assert exc_info.value.http_status == 500
        assert exc_info.value.retryable is True
        client.close()
