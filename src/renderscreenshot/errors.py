"""Error handling for the RenderScreenshot SDK."""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional, Set

# Error codes returned by the API
ErrorCode = Literal[
    "invalid_request",
    "invalid_url",
    "unauthorized",
    "forbidden",
    "not_found",
    "rate_limited",
    "timeout",
    "render_failed",
    "internal_error",
]

# Errors that can be retried
RETRYABLE_ERRORS: Set[ErrorCode] = {
    "rate_limited",
    "timeout",
    "render_failed",
    "internal_error",
}


class RenderScreenshotError(Exception):
    """Custom error class for RenderScreenshot API errors.

    Attributes:
        http_status: HTTP status code from the response.
        code: Error code from the API (e.g., "invalid_url", "rate_limited").
        message: Human-readable error message.
        retryable: Whether this error can be retried.
        retry_after: Seconds to wait before retrying (for rate limits).
        type: Error category from the API (e.g., "validation_error"), if given.
        param: Request parameter that caused the error (e.g., "url"), if given.
        request_id: API request ID to quote to support, if given.
        docs: Link to the documentation for this error code, if given.

    Example:
        >>> try:
        ...     image = client.take(options)
        ... except RenderScreenshotError as e:
        ...     if e.retryable and e.retry_after:
        ...         time.sleep(e.retry_after)
        ...         # Retry the request
        ...     else:
        ...         raise
    """

    def __init__(
        self,
        http_status: int,
        code: ErrorCode,
        message: str,
        retry_after: Optional[int] = None,
        *,
        error_type: Optional[str] = None,
        param: Optional[str] = None,
        request_id: Optional[str] = None,
        docs: Optional[str] = None,
    ) -> None:
        """Create a new RenderScreenshotError.

        Args:
            http_status: HTTP status code from the response.
            code: Error code from the API.
            message: Human-readable error message.
            retry_after: Seconds to wait before retrying (optional).
            error_type: Error category from the API (optional).
            param: Request parameter that caused the error (optional).
            request_id: API request ID (optional).
            docs: Documentation link for the error code (optional).
        """
        super().__init__(message)
        self.http_status = http_status
        self.code = code
        self.message = message
        self.retryable = code in RETRYABLE_ERRORS
        self.retry_after = retry_after
        self.type = error_type
        self.param = param
        self.request_id = request_id
        self.docs = docs

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [f"[{self.code}] {self.message}"]
        if self.retry_after is not None:
            parts.append(f" (retry after {self.retry_after}s)")
        return "".join(parts)

    def __repr__(self) -> str:
        """Return detailed representation of the error."""
        return (
            f"RenderScreenshotError(http_status={self.http_status}, "
            f"code={self.code!r}, message={self.message!r}, "
            f"retryable={self.retryable}, retry_after={self.retry_after})"
        )

    @classmethod
    def from_response(
        cls,
        http_status: int,
        body: Dict[str, Any],
        retry_after: Optional[int] = None,
    ) -> "RenderScreenshotError":
        """Create an error from an API response.

        The API returns ``{"error": {"type", "code", "message", "param", ...},
        "request_id": ...}``. Flat ``{"code", "message"}`` and
        ``{"error": "message"}`` bodies are also accepted.

        Args:
            http_status: HTTP status code from the response.
            body: Parsed JSON response body.
            retry_after: Value from Retry-After header (optional).

        Returns:
            A new RenderScreenshotError instance.
        """
        if not isinstance(body, dict):
            body = {}
        nested = body.get("error")
        source: Dict[str, Any] = nested if isinstance(nested, dict) else body

        def _str(data: Dict[str, Any], key: str) -> Optional[str]:
            value = data.get(key)
            return value if isinstance(value, str) else None

        code = _str(source, "code") or "internal_error"
        message = _str(source, "message") or _str(body, "error") or "An unknown error occurred"
        return cls(
            http_status,
            code,  # type: ignore[arg-type]
            message,
            retry_after,
            error_type=_str(source, "type"),
            param=_str(source, "param"),
            request_id=_str(body, "request_id") or _str(source, "request_id"),
            docs=_str(source, "docs"),
        )

    @classmethod
    def invalid_url(cls, url: str) -> "RenderScreenshotError":
        """Create an invalid URL error.

        Args:
            url: The invalid URL that was provided.

        Returns:
            A new RenderScreenshotError instance.
        """
        return cls(400, "invalid_url", f"Invalid URL provided: {url}")

    @classmethod
    def invalid_request(cls, message: str) -> "RenderScreenshotError":
        """Create an invalid request error.

        Args:
            message: Description of what was invalid.

        Returns:
            A new RenderScreenshotError instance.
        """
        return cls(400, "invalid_request", message)

    @classmethod
    def unauthorized(cls) -> "RenderScreenshotError":
        """Create an unauthorized error.

        Returns:
            A new RenderScreenshotError instance.
        """
        return cls(401, "unauthorized", "Invalid or missing API key")

    @classmethod
    def forbidden(cls, message: Optional[str] = None) -> "RenderScreenshotError":
        """Create a forbidden error.

        Args:
            message: Optional custom message.

        Returns:
            A new RenderScreenshotError instance.
        """
        return cls(403, "forbidden", message or "Access denied")

    @classmethod
    def not_found(cls, message: Optional[str] = None) -> "RenderScreenshotError":
        """Create a not found error.

        Args:
            message: Optional custom message.

        Returns:
            A new RenderScreenshotError instance.
        """
        return cls(404, "not_found", message or "Resource not found")

    @classmethod
    def rate_limited(cls, retry_after: Optional[int] = None) -> "RenderScreenshotError":
        """Create a rate limited error.

        Args:
            retry_after: Seconds to wait before retrying.

        Returns:
            A new RenderScreenshotError instance.
        """
        return cls(
            429,
            "rate_limited",
            "Rate limit exceeded. Please wait before making more requests.",
            retry_after,
        )

    @classmethod
    def timeout(cls) -> "RenderScreenshotError":
        """Create a timeout error.

        Returns:
            A new RenderScreenshotError instance.
        """
        return cls(408, "timeout", "Screenshot request timed out")

    @classmethod
    def render_failed(cls, message: Optional[str] = None) -> "RenderScreenshotError":
        """Create a render failed error.

        Args:
            message: Optional error details.

        Returns:
            A new RenderScreenshotError instance.
        """
        return cls(500, "render_failed", message or "Browser rendering failed")

    @classmethod
    def internal(cls, message: Optional[str] = None) -> "RenderScreenshotError":
        """Create an internal error.

        Args:
            message: Optional error details.

        Returns:
            A new RenderScreenshotError instance.
        """
        return cls(500, "internal_error", message or "An internal error occurred")
