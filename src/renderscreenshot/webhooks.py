"""Webhook verification and parsing for the RenderScreenshot SDK."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Any, Dict, Mapping, Tuple, Union

from .types import (
    ScreenshotResponse,
    WebhookEvent,
    WebhookEventData,
    WebhookEventType,
)


def verify_webhook(
    payload: str,
    signature: str,
    timestamp: str,
    secret: str,
    *,
    tolerance: int = 300,
) -> bool:
    """Verify a webhook signature.

    Webhooks are signed using HMAC-SHA256 with the format:
    `sha256=hmac(secret, "{timestamp}.{payload}")`

    Args:
        payload: The raw request body as a string.
        signature: The X-Webhook-Signature header value.
        timestamp: The X-Webhook-Timestamp header value.
        secret: Your webhook signing secret from the dashboard.
        tolerance: Maximum age of webhook in seconds (default: 300 = 5 minutes).

    Returns:
        True if the signature is valid, False otherwise.

    Example:
        >>> # In your webhook handler (Flask example)
        >>> @app.route("/webhook", methods=["POST"])
        >>> def webhook():
        ...     signature = request.headers.get("X-Webhook-Signature", "")
        ...     timestamp = request.headers.get("X-Webhook-Timestamp", "")
        ...     payload = request.get_data(as_text=True)
        ...
        ...     if not verify_webhook(payload, signature, timestamp, WEBHOOK_SECRET):
        ...         return "Invalid signature", 401
        ...
        ...     event = parse_webhook(payload)
        ...     # Process event...
        ...     return "OK", 200
    """
    # Validate inputs
    if not payload or not signature or not timestamp or not secret:
        return False

    # Check timestamp to prevent replay attacks
    try:
        timestamp_num = int(timestamp)
    except ValueError:
        return False

    now = int(time.time())
    if abs(now - timestamp_num) > tolerance:
        return False

    # Compute expected signature
    message = f"{timestamp}.{payload}"
    expected = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
    )

    # Use timing-safe comparison to prevent timing attacks
    return hmac.compare_digest(expected, signature)


def parse_webhook(payload: Union[str, Dict[str, Any]]) -> WebhookEvent:
    """Parse a webhook payload into a typed event object.

    Args:
        payload: The raw request body (string or parsed dict).

    Returns:
        Typed webhook event.

    Example:
        >>> event = parse_webhook(request.json)
        >>> if event["type"] == "screenshot.completed":
        ...     response = event["data"].get("response")
        ...     if response:
        ...         print(f"Screenshot ready: {response['url']}")
    """
    raw: Dict[str, Any]
    if isinstance(payload, str):
        raw = json.loads(payload)
    else:
        raw = payload

    # Parse timestamp
    timestamp_str = raw.get("timestamp", "")
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        timestamp = datetime.now()

    event_type: WebhookEventType = raw.get("event", "screenshot.completed")
    event_data: WebhookEventData = {}

    # Parse based on event type
    data = raw.get("data", {})

    if event_type == "screenshot.completed":
        response: ScreenshotResponse = {
            "url": data.get("screenshot_url", ""),
            "width": data.get("width", 0),
            "height": data.get("height", 0),
            "format": data.get("format", "png"),
            "size": data.get("size", 0),
            "cached": data.get("cached", False),
        }
        event_data["response"] = response
        if "url" in data:
            event_data["url"] = data["url"]

    elif event_type == "screenshot.failed":
        event_data["error"] = {
            "code": "render_failed",
            "message": data.get("error", "Unknown error"),
        }
        if "url" in data:
            event_data["url"] = data["url"]

    elif event_type in ("batch.completed", "batch.failed"):
        event_data["batch_id"] = raw.get("id", "")

    event: WebhookEvent = {
        "id": raw.get("id", ""),
        "type": event_type,
        "timestamp": timestamp,
        "data": event_data,
    }

    return event


def extract_webhook_headers(
    headers: Union[Mapping[str, str], Mapping[str, Any]],
) -> Tuple[str, str]:
    """Extract webhook headers from a request-like object.

    This helper works with various HTTP frameworks (Flask, Django, FastAPI, etc.)
    to extract the signature and timestamp headers.

    Args:
        headers: Headers object or dictionary.

    Returns:
        Tuple of (signature, timestamp).

    Example:
        >>> # Flask
        >>> signature, timestamp = extract_webhook_headers(request.headers)
        >>>
        >>> # FastAPI
        >>> signature, timestamp = extract_webhook_headers(request.headers)
        >>>
        >>> # Django
        >>> signature, timestamp = extract_webhook_headers(request.META)
    """

    def get_header(name: str) -> str:
        # Try exact match
        value = headers.get(name)
        if value:
            return str(value)

        # Try lowercase
        value = headers.get(name.lower())
        if value:
            return str(value)

        # Try Django-style (HTTP_X_WEBHOOK_SIGNATURE)
        django_name = "HTTP_" + name.upper().replace("-", "_")
        value = headers.get(django_name)
        if value:
            return str(value)

        return ""

    signature = get_header("X-Webhook-Signature")
    timestamp = get_header("X-Webhook-Timestamp")

    return signature, timestamp
