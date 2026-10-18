"""Tests for the Client class."""

import json
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


SIGN_KEY = "rs_secret_vector456"
PUB_KEY = "rs_pub_vector123"
VECTOR_EXPIRES = 1893456000


def _signing_client():
    return Client("rs_live_test123", signing_key=SIGN_KEY, public_key_id=PUB_KEY)


class TestClientGenerateUrl:
    """Tests for generate_url method."""

    def test_cross_sdk_vector_v1(self):
        """Signed URL matches the Rails/rs-ruby reference vector V1 exactly."""
        client = _signing_client()
        options = (
            TakeOptions.url("https://example.com/path?a=1&b=two words")
            .width(1200)
            .height(630)
            .format("png")
            .full_page()
        )

        url = client.generate_url(options, VECTOR_EXPIRES)

        assert url == (
            "https://api.renderscreenshot.com/v1/screenshot?expires=1893456000&format=png"
            "&full_page=true&height=630&key_id=rs_pub_vector123"
            "&url=https%3A%2F%2Fexample.com%2Fpath%3Fa%3D1%26b%3Dtwo+words&width=1200"
            "&signature=ff30f019a228e751b71f4bdca8c5341c33eaac0985a18426882525de00ba329a"
        )
        client.close()

    def test_cross_sdk_vector_v2(self):
        """Signed URL matches the Rails/rs-ruby reference vector V2 exactly."""
        client = _signing_client()
        options = TakeOptions.url("https://example.com/caf\u00e9?q=a b&x=~*()!'").width(1200)

        url = client.generate_url(options, VECTOR_EXPIRES)

        assert url == (
            "https://api.renderscreenshot.com/v1/screenshot?expires=1893456000"
            "&key_id=rs_pub_vector123"
            "&url=https%3A%2F%2Fexample.com%2Fcaf%C3%A9%3Fq%3Da+b%26x%3D~%2A%28%29%21%27"
            "&width=1200"
            "&signature=8c53d62d192cd5423ea612eb08bbe2df25e22ee89b8f52634be4b8f0812a0e14"
        )
        client.close()

    def test_accepts_datetime_expiry(self):
        """A datetime expiry becomes its Unix timestamp."""
        client = _signing_client()
        expires = datetime.fromtimestamp(VECTOR_EXPIRES)

        url = client.generate_url(TakeOptions.url("https://example.com"), expires)

        assert "expires=1893456000" in url
        client.close()

    def test_per_call_credentials_override(self):
        """Signing credentials passed to generate_url override the client's."""
        client = Client("rs_live_test123")
        options = (
            TakeOptions.url("https://example.com/path?a=1&b=two words")
            .width(1200)
            .height(630)
            .format("png")
            .full_page()
        )

        url = client.generate_url(
            options, VECTOR_EXPIRES, signing_key=SIGN_KEY, public_key_id=PUB_KEY
        )

        assert url.endswith(
            "signature=ff30f019a228e751b71f4bdca8c5341c33eaac0985a18426882525de00ba329a"
        )
        client.close()

    def test_requires_signing_credentials(self):
        """generate_url raises a validation error without rs_secret_/rs_pub_ keys."""
        client = Client("rs_live_test123")
        with pytest.raises(RenderScreenshotError) as exc:
            client.generate_url(TakeOptions.url("https://example.com"), VECTOR_EXPIRES)
        assert exc.value.code == "invalid_request"

        only_secret = Client("rs_live_test123", signing_key=SIGN_KEY)
        with pytest.raises(RenderScreenshotError):
            only_secret.generate_url(TakeOptions.url("https://example.com"), VECTOR_EXPIRES)
        client.close()
        only_secret.close()

    def test_does_not_sign_with_api_key(self):
        """The live API key never appears in the signed URL."""
        client = _signing_client()
        url = client.generate_url(TakeOptions.url("https://example.com"), VECTOR_EXPIRES)
        assert "rs_live_" not in url
        assert "rs_secret_" not in url
        client.close()

    def test_generate_url_with_options(self):
        """Test signed URL with multiple options uses GET query names."""
        client = _signing_client()
        options = (
            TakeOptions.url("https://example.com")
            .width(1200)
            .height(630)
            .preset("og_card")
            .block_ads()
            .block_cookie_banners()
            .element("#main")
        )
        expires = datetime.now() + timedelta(hours=24)

        url = client.generate_url(options, expires)

        assert "width=1200" in url
        assert "height=630" in url
        assert "preset=og_card" in url
        assert "block_ads=true" in url
        assert "block_cookies=true" in url
        assert "selector=%23main" in url
        client.close()

    def test_generate_url_with_dict(self):
        """Test signed URL generation with dict config."""
        client = _signing_client()
        config = {"url": "https://example.com", "width": 1200}

        url = client.generate_url(config, VECTOR_EXPIRES)

        assert "url=https" in url
        assert "width=1200" in url
        client.close()

    def test_generate_url_sorted_params(self):
        """Test that URL parameters are sorted alphabetically."""
        client = _signing_client()
        options = TakeOptions.url("https://example.com").width(1200).block_ads()

        url = client.generate_url(options, VECTOR_EXPIRES)

        query = url.split("?", 1)[1].rsplit("&signature=", 1)[0]
        keys = [pair.split("=", 1)[0] for pair in query.split("&")]
        assert keys == sorted(keys)
        assert keys == ["block_ads", "expires", "key_id", "url", "width"]
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

    def test_take_sends_nested_json(self, httpx_mock):
        """take() POSTs the nested JSON shape the API expects."""
        httpx_mock.add_response(content=b"img")

        client = Client("rs_live_test123")
        options = (
            TakeOptions.url("https://example.com")
            .width(1200)
            .height(630)
            .full_page()
            .element("#main")
            .format("jpeg")
            .quality(85)
            .wait_for_selector("#ready")
            .block_ads()
            .dark_mode()
        )
        client.take(options)

        request = httpx_mock.get_request()
        assert json.loads(request.content) == {
            "url": "https://example.com",
            "viewport": {"width": 1200, "height": 630},
            "capture": {"mode": "full_page", "selector": "#main"},
            "output": {"format": "jpeg", "quality": 85},
            "wait": {"for_selector": "#ready"},
            "block": {"ads": True},
            "browser": {"dark_mode": True},
        }
        assert request.headers["Authorization"] == "Bearer rs_live_test123"
        assert request.headers.get("Accept") != "application/json"
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
        # Real body built by ApiResponseBuilder.success_response
        response_data = json.loads(
            """
            {
              "id": "req_ab12cd34ef56ab78",
              "status": "completed",
              "image": {"url": "https://cdn.example.com/screenshot.png", "width": 1200,
                        "height": 630, "size": 12345, "format": "png"},
              "metadata": {"title": "Screenshot"},
              "cache": {"hit": true, "key": "screenshots/abc.png",
                        "url": "https://cdn.example.com/screenshot.png",
                        "expires_at": "2026-10-19T12:00:00Z"},
              "usage": {"credits": 1, "remaining": 99}
            }
            """
        )
        httpx_mock.add_response(json=response_data)

        client = Client("rs_live_test123")
        options = TakeOptions.url("https://example.com").preset("og_card")

        result = client.take_json(options)

        assert result["id"] == "req_ab12cd34ef56ab78"
        assert result["status"] == "completed"
        assert result["image"] == {
            "url": "https://cdn.example.com/screenshot.png",
            "width": 1200,
            "height": 630,
            "size": 12345,
            "format": "png",
        }
        assert result["cache"]["hit"] is True
        assert result["cache"]["key"] == "screenshots/abc.png"
        assert result["cache"]["url"] == "https://cdn.example.com/screenshot.png"
        assert result["cache"]["expires_at"] == "2026-10-19T12:00:00Z"
        assert result["usage"] == {"credits": 1, "remaining": 99}
        client.close()

    def test_take_json_webhook_accepted(self, httpx_mock):
        """A webhook request returns 202 with a job id and processing status."""
        httpx_mock.add_response(
            status_code=202,
            json={
                "id": "job_123",
                "status": "processing",
                "webhook": {"url": "https://hooks.example.com/rs"},
            },
        )

        client = Client("rs_live_test123")
        result = client.take_json(TakeOptions.url("https://example.com"))

        assert result["id"] == "job_123"
        assert result["status"] == "processing"
        assert "image" not in result
        client.close()

    def test_take_json_sends_accept_header(self, httpx_mock):
        """take_json() asks for JSON with the Accept header and nested body."""
        httpx_mock.add_response(json={"url": "https://cdn.example.com/x.png"})

        client = Client("rs_live_test123")
        client.take_json(TakeOptions.url("https://example.com").width(800).format("png"))

        request = httpx_mock.get_request()
        assert request.headers["Accept"] == "application/json"
        assert json.loads(request.content) == {
            "url": "https://example.com",
            "viewport": {"width": 800},
            "output": {"format": "png"},
        }
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

        result = client.batch(urls, options.width(1200).full_page())

        assert result["id"] == "batch_123"
        body = json.loads(httpx_mock.get_request().content)
        assert body == {
            "urls": urls,
            "options": {
                "preset": "og_card",
                "viewport": {"width": 1200},
                "capture": {"mode": "full_page"},
            },
        }
        client.close()

    def test_batch_with_request_items_sends_nested_options(self, httpx_mock):
        """Per-URL batch requests use the nested option shape."""
        httpx_mock.add_response(json={"id": "batch_9", "status": "processing"})

        client = Client("rs_live_test123")
        client.batch(
            [
                {"url": "https://a.com", "options": {"width": 1200, "format": "webp"}},
                {"url": "https://b.com", "options": {"preset": "full_page"}},
            ]
        )

        body = json.loads(httpx_mock.get_request().content)
        assert body == {
            "requests": [
                {"url": "https://a.com", "viewport": {"width": 1200}, "output": {"format": "webp"}},
                {"url": "https://b.com", "preset": "full_page"},
            ]
        }
        client.close()

    def test_batch_parses_completed_and_failed_items(self, httpx_mock):
        """Test batch results use the API's status/image/error item shape."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.renderscreenshot.com/v1/batch",
            json={
                "id": "batch_123",
                "status": "completed",
                "total": 2,
                "completed": 1,
                "failed": 1,
                "results": [
                    {
                        "position": 0,
                        "url": "https://example1.com",
                        "status": "completed",
                        "image": {
                            "image_url": "https://cdn.example.com/1.png",
                            "width": 1200,
                            "height": 630,
                        },
                        "error": None,
                    },
                    {
                        "position": 1,
                        "url": "https://broken.example",
                        "status": "failed",
                        "image": None,
                        "error": "Page failed to load",
                    },
                ],
                "usage": {"credits": 1, "remaining": 99},
            },
        )

        client = Client("rs_live_test123")
        result = client.batch(["https://example1.com", "https://broken.example"])

        ok, bad = result["results"]
        assert ok["status"] == "completed"
        assert ok["image"]["image_url"] == "https://cdn.example.com/1.png"
        assert ok["error"] is None
        assert bad["status"] == "failed"
        assert bad["image"] is None
        assert bad["error"] == "Page failed to load"
        assert result["completed"] == 1
        assert result["failed"] == 1
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
                {
                    "url": "https://example1.com",
                    "status": "completed",
                    "image": {"image_url": "https://cdn.example.com/a.png"},
                    "error": None,
                },
                {
                    "url": "https://example2.com",
                    "status": "completed",
                    "image": {"image_url": "https://cdn.example.com/a.png"},
                    "error": None,
                },
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

    def test_handles_nested_api_error_body(self, httpx_mock):
        """Test that the real nested API error body is parsed."""
        httpx_mock.add_response(
            status_code=400,
            json={
                "error": {
                    "type": "validation_error",
                    "code": "invalid_url",
                    "message": "The URL is not valid",
                    "param": "url",
                    "retryable": False,
                    "docs": "https://docs.renderscreenshot.com/errors/invalid_url",
                },
                "request_id": "req_abc123",
            },
        )

        client = Client("rs_live_test123")

        with pytest.raises(RenderScreenshotError) as exc_info:
            client.take(TakeOptions.url("notaurl"))

        error = exc_info.value
        assert error.http_status == 400
        assert error.code == "invalid_url"
        assert error.message == "The URL is not valid"
        assert error.type == "validation_error"
        assert error.param == "url"
        assert error.request_id == "req_abc123"
        assert error.retryable is False
        client.close()
