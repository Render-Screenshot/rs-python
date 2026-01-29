"""Tests for error handling."""

import pytest

from renderscreenshot.errors import RETRYABLE_ERRORS, RenderScreenshotError


class TestRenderScreenshotError:
    """Tests for the RenderScreenshotError class."""

    def test_basic_error_creation(self):
        """Test creating a basic error."""
        error = RenderScreenshotError(400, "invalid_url", "Invalid URL provided")

        assert error.http_status == 400
        assert error.code == "invalid_url"
        assert error.message == "Invalid URL provided"
        assert error.retryable is False
        assert error.retry_after is None

    def test_retryable_error(self):
        """Test that retryable errors are marked correctly."""
        error = RenderScreenshotError(429, "rate_limited", "Rate limit exceeded", 60)

        assert error.http_status == 429
        assert error.code == "rate_limited"
        assert error.retryable is True
        assert error.retry_after == 60

    def test_non_retryable_error(self):
        """Test that non-retryable errors are marked correctly."""
        error = RenderScreenshotError(401, "unauthorized", "Invalid API key")

        assert error.retryable is False

    def test_str_representation(self):
        """Test string representation."""
        error = RenderScreenshotError(400, "invalid_url", "Invalid URL")
        assert str(error) == "[invalid_url] Invalid URL"

        error_with_retry = RenderScreenshotError(429, "rate_limited", "Rate limited", 30)
        assert str(error_with_retry) == "[rate_limited] Rate limited (retry after 30s)"

    def test_repr_representation(self):
        """Test repr representation."""
        error = RenderScreenshotError(400, "invalid_url", "Invalid URL")
        repr_str = repr(error)

        assert "RenderScreenshotError" in repr_str
        assert "http_status=400" in repr_str
        assert "code='invalid_url'" in repr_str
        assert "message='Invalid URL'" in repr_str

    def test_from_response(self):
        """Test creating error from API response."""
        body = {"code": "invalid_url", "message": "URL is not valid"}
        error = RenderScreenshotError.from_response(400, body)

        assert error.http_status == 400
        assert error.code == "invalid_url"
        assert error.message == "URL is not valid"

    def test_from_response_with_error_key(self):
        """Test creating error from API response with 'error' key."""
        body = {"code": "internal_error", "error": "Something went wrong"}
        error = RenderScreenshotError.from_response(500, body)

        assert error.message == "Something went wrong"

    def test_from_response_with_retry_after(self):
        """Test creating error with retry-after header."""
        body = {"code": "rate_limited", "message": "Too many requests"}
        error = RenderScreenshotError.from_response(429, body, retry_after=60)

        assert error.retry_after == 60
        assert error.retryable is True

    def test_from_response_missing_fields(self):
        """Test creating error with missing fields uses defaults."""
        error = RenderScreenshotError.from_response(500, {})

        assert error.code == "internal_error"
        assert error.message == "An unknown error occurred"

    def test_invalid_url_factory(self):
        """Test the invalid_url factory method."""
        error = RenderScreenshotError.invalid_url("not-a-url")

        assert error.http_status == 400
        assert error.code == "invalid_url"
        assert "not-a-url" in error.message
        assert error.retryable is False

    def test_invalid_request_factory(self):
        """Test the invalid_request factory method."""
        error = RenderScreenshotError.invalid_request("Missing required field")

        assert error.http_status == 400
        assert error.code == "invalid_request"
        assert error.message == "Missing required field"

    def test_unauthorized_factory(self):
        """Test the unauthorized factory method."""
        error = RenderScreenshotError.unauthorized()

        assert error.http_status == 401
        assert error.code == "unauthorized"
        assert "API key" in error.message

    def test_forbidden_factory(self):
        """Test the forbidden factory method."""
        error = RenderScreenshotError.forbidden()
        assert error.http_status == 403
        assert error.code == "forbidden"

        error_custom = RenderScreenshotError.forbidden("Custom message")
        assert error_custom.message == "Custom message"

    def test_not_found_factory(self):
        """Test the not_found factory method."""
        error = RenderScreenshotError.not_found()
        assert error.http_status == 404
        assert error.code == "not_found"

    def test_rate_limited_factory(self):
        """Test the rate_limited factory method."""
        error = RenderScreenshotError.rate_limited(120)

        assert error.http_status == 429
        assert error.code == "rate_limited"
        assert error.retry_after == 120
        assert error.retryable is True

    def test_timeout_factory(self):
        """Test the timeout factory method."""
        error = RenderScreenshotError.timeout()

        assert error.http_status == 408
        assert error.code == "timeout"
        assert error.retryable is True

    def test_render_failed_factory(self):
        """Test the render_failed factory method."""
        error = RenderScreenshotError.render_failed("Browser crashed")

        assert error.http_status == 500
        assert error.code == "render_failed"
        assert error.message == "Browser crashed"
        assert error.retryable is True

    def test_internal_factory(self):
        """Test the internal factory method."""
        error = RenderScreenshotError.internal()
        assert error.http_status == 500
        assert error.code == "internal_error"
        assert error.retryable is True

        error_custom = RenderScreenshotError.internal("Database error")
        assert error_custom.message == "Database error"

    def test_error_is_exception(self):
        """Test that RenderScreenshotError is an Exception."""
        error = RenderScreenshotError(400, "invalid_url", "Test error")

        assert isinstance(error, Exception)

        with pytest.raises(RenderScreenshotError):
            raise error

    def test_retryable_error_codes(self):
        """Test that the correct error codes are marked as retryable."""
        expected_retryable = {"rate_limited", "timeout", "render_failed", "internal_error"}
        assert expected_retryable == RETRYABLE_ERRORS
