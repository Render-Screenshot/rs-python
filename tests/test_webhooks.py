"""Tests for webhook verification and parsing."""

import hashlib
import hmac
import json
import time

from renderscreenshot.webhooks import (
    extract_webhook_headers,
    parse_webhook,
    verify_webhook,
)


class TestVerifyWebhook:
    """Tests for verify_webhook function."""

    def _create_signature(self, payload: str, timestamp: str, secret: str) -> str:
        """Helper to create a valid signature."""
        message = f"{timestamp}.{payload}"
        return (
            "sha256="
            + hmac.new(
                secret.encode("utf-8"),
                message.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
        )

    def test_valid_signature(self):
        """Test verification with valid signature."""
        secret = "whsec_test123"
        payload = '{"event":"screenshot.completed"}'
        timestamp = str(int(time.time()))
        signature = self._create_signature(payload, timestamp, secret)

        result = verify_webhook(payload, signature, timestamp, secret)

        assert result is True

    def test_invalid_signature(self):
        """Test verification with invalid signature."""
        secret = "whsec_test123"
        payload = '{"event":"screenshot.completed"}'
        timestamp = str(int(time.time()))
        signature = "sha256=invalid"

        result = verify_webhook(payload, signature, timestamp, secret)

        assert result is False

    def test_wrong_secret(self):
        """Test verification with wrong secret."""
        correct_secret = "whsec_test123"
        wrong_secret = "whsec_wrong"
        payload = '{"event":"screenshot.completed"}'
        timestamp = str(int(time.time()))
        signature = self._create_signature(payload, timestamp, correct_secret)

        result = verify_webhook(payload, signature, timestamp, wrong_secret)

        assert result is False

    def test_expired_timestamp(self):
        """Test verification with expired timestamp."""
        secret = "whsec_test123"
        payload = '{"event":"screenshot.completed"}'
        # Timestamp from 10 minutes ago
        timestamp = str(int(time.time()) - 600)
        signature = self._create_signature(payload, timestamp, secret)

        result = verify_webhook(payload, signature, timestamp, secret)

        assert result is False

    def test_future_timestamp(self):
        """Test verification with future timestamp."""
        secret = "whsec_test123"
        payload = '{"event":"screenshot.completed"}'
        # Timestamp 10 minutes in the future
        timestamp = str(int(time.time()) + 600)
        signature = self._create_signature(payload, timestamp, secret)

        result = verify_webhook(payload, signature, timestamp, secret)

        assert result is False

    def test_custom_tolerance(self):
        """Test verification with custom tolerance."""
        secret = "whsec_test123"
        payload = '{"event":"screenshot.completed"}'
        # Timestamp from 8 minutes ago
        timestamp = str(int(time.time()) - 480)
        signature = self._create_signature(payload, timestamp, secret)

        # Should fail with default 5 minute tolerance
        result_default = verify_webhook(payload, signature, timestamp, secret)
        assert result_default is False

        # Should pass with 10 minute tolerance
        result_custom = verify_webhook(payload, signature, timestamp, secret, tolerance=600)
        assert result_custom is True

    def test_empty_inputs(self):
        """Test verification with empty inputs."""
        assert verify_webhook("", "sig", "ts", "secret") is False
        assert verify_webhook("payload", "", "ts", "secret") is False
        assert verify_webhook("payload", "sig", "", "secret") is False
        assert verify_webhook("payload", "sig", "ts", "") is False

    def test_invalid_timestamp(self):
        """Test verification with invalid timestamp."""
        result = verify_webhook("payload", "sig", "not-a-number", "secret")
        assert result is False


class TestParseWebhook:
    """Tests for parse_webhook function."""

    def test_parse_screenshot_completed(self):
        """Test parsing screenshot.completed event."""
        payload = {
            "id": "evt_123",
            "event": "screenshot.completed",
            "timestamp": "2024-01-15T12:00:00Z",
            "data": {
                "url": "https://example.com",
                "screenshot_url": "https://cdn.example.com/shot.png",
                "width": 1200,
                "height": 630,
                "format": "png",
                "size": 12345,
                "cached": False,
            },
        }

        event = parse_webhook(payload)

        assert event["id"] == "evt_123"
        assert event["type"] == "screenshot.completed"
        assert event["data"]["url"] == "https://example.com"
        assert event["data"]["response"]["url"] == "https://cdn.example.com/shot.png"
        assert event["data"]["response"]["width"] == 1200

    def test_parse_screenshot_failed(self):
        """Test parsing screenshot.failed event."""
        payload = {
            "id": "evt_456",
            "event": "screenshot.failed",
            "timestamp": "2024-01-15T12:00:00Z",
            "data": {
                "url": "https://example.com",
                "error": "Page timed out",
            },
        }

        event = parse_webhook(payload)

        assert event["id"] == "evt_456"
        assert event["type"] == "screenshot.failed"
        assert event["data"]["error"]["message"] == "Page timed out"
        assert event["data"]["error"]["code"] == "render_failed"

    def test_parse_batch_completed(self):
        """Test parsing batch.completed event."""
        payload = {
            "id": "batch_789",
            "event": "batch.completed",
            "timestamp": "2024-01-15T12:00:00Z",
            "data": {
                "summary": {"total": 10, "completed": 10, "failed": 0},
            },
        }

        event = parse_webhook(payload)

        assert event["type"] == "batch.completed"
        assert event["data"]["batch_id"] == "batch_789"

    def test_parse_batch_failed(self):
        """Test parsing batch.failed event."""
        payload = {
            "id": "batch_999",
            "event": "batch.failed",
            "timestamp": "2024-01-15T12:00:00Z",
            "data": {},
        }

        event = parse_webhook(payload)

        assert event["type"] == "batch.failed"
        assert event["data"]["batch_id"] == "batch_999"

    def test_parse_string_payload(self):
        """Test parsing string payload."""
        payload_str = json.dumps(
            {
                "id": "evt_123",
                "event": "screenshot.completed",
                "timestamp": "2024-01-15T12:00:00Z",
                "data": {
                    "screenshot_url": "https://cdn.example.com/shot.png",
                    "width": 1200,
                    "height": 630,
                    "format": "png",
                    "size": 12345,
                    "cached": False,
                },
            }
        )

        event = parse_webhook(payload_str)

        assert event["id"] == "evt_123"
        assert event["type"] == "screenshot.completed"


class TestExtractWebhookHeaders:
    """Tests for extract_webhook_headers function."""

    def test_extract_from_dict(self):
        """Test extracting headers from dictionary."""
        headers = {
            "X-Webhook-Signature": "sha256=abc123",
            "X-Webhook-Timestamp": "1234567890",
        }

        signature, timestamp = extract_webhook_headers(headers)

        assert signature == "sha256=abc123"
        assert timestamp == "1234567890"

    def test_extract_lowercase(self):
        """Test extracting headers with lowercase keys."""
        headers = {
            "x-webhook-signature": "sha256=abc123",
            "x-webhook-timestamp": "1234567890",
        }

        signature, timestamp = extract_webhook_headers(headers)

        assert signature == "sha256=abc123"
        assert timestamp == "1234567890"

    def test_extract_django_style(self):
        """Test extracting headers from Django-style META dict."""
        headers = {
            "HTTP_X_WEBHOOK_SIGNATURE": "sha256=abc123",
            "HTTP_X_WEBHOOK_TIMESTAMP": "1234567890",
        }

        signature, timestamp = extract_webhook_headers(headers)

        assert signature == "sha256=abc123"
        assert timestamp == "1234567890"

    def test_missing_headers(self):
        """Test with missing headers."""
        headers = {}

        signature, timestamp = extract_webhook_headers(headers)

        assert signature == ""
        assert timestamp == ""
