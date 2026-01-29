"""RenderScreenshot API client."""

from __future__ import annotations

import contextlib
import hashlib
import hmac
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, overload

import httpx

from .cache import CacheManager
from .errors import RenderScreenshotError
from .options import TakeOptions
from .types import (
    BatchRequestItem,
    BatchResponse,
    DeviceInfo,
    PresetInfo,
    ScreenshotResponse,
    TakeOptionsConfig,
)

DEFAULT_BASE_URL = "https://api.renderscreenshot.com"
DEFAULT_TIMEOUT = 30.0
API_VERSION = "v1"
SDK_VERSION = "1.0.0"


class Client:
    """RenderScreenshot API client.

    Use this client to take screenshots, generate signed URLs, and manage cache.

    Example:
        >>> from renderscreenshot import Client, TakeOptions
        >>>
        >>> client = Client("rs_live_xxxxx")
        >>> options = TakeOptions.url("https://example.com").preset("og_card")
        >>> image = client.take(options)

    Attributes:
        cache: Cache management methods.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """Create a new RenderScreenshot client.

        Args:
            api_key: Your API key (rs_live_* or rs_test_*).
            base_url: Base URL for the API (optional, defaults to production).
            timeout: Request timeout in seconds (optional, defaults to 30).

        Raises:
            ValueError: If API key is empty.

        Example:
            >>> client = Client("rs_live_xxxxx")
            >>> # Or with custom settings:
            >>> client = Client(
            ...     "rs_live_xxxxx",
            ...     base_url="https://api.staging.renderscreenshot.com",
            ...     timeout=60.0,
            ... )
        """
        if not api_key:
            raise ValueError("API key is required")

        self._api_key = api_key
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout or DEFAULT_TIMEOUT
        self._http_client: Optional[httpx.Client] = None

        # Cache management
        self.cache = CacheManager(self)

    @property
    def _client(self) -> httpx.Client:
        """Lazily create the HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.Client(
                base_url=f"{self._base_url}/{API_VERSION}",
                timeout=self._timeout,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "User-Agent": f"renderscreenshot-python/{SDK_VERSION}",
                },
            )
        return self._http_client

    def close(self) -> None:
        """Close the HTTP client and release resources.

        Call this method when you're done using the client to free up
        connections. Alternatively, use the client as a context manager.

        Example:
            >>> client = Client("rs_live_xxxxx")
            >>> try:
            ...     image = client.take(options)
            ... finally:
            ...     client.close()
        """
        if self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def __enter__(self) -> "Client":
        """Enter context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager and close client."""
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        response_type: str = "json",
    ) -> Any:
        """Make an authenticated request to the API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.).
            path: API path (e.g., "/screenshot").
            body: Request body for POST/PUT requests.
            response_type: Expected response type ("json" or "buffer").

        Returns:
            Parsed JSON response or bytes.

        Raises:
            RenderScreenshotError: If the API returns an error.
        """
        try:
            kwargs: Dict[str, Any] = {}
            if body is not None:
                kwargs["json"] = body

            response = self._client.request(method, path, **kwargs)

            # Handle errors
            if response.status_code >= 400:
                self._handle_error(response)

            # Return appropriate type
            if response_type == "buffer":
                return response.content
            return response.json()

        except httpx.TimeoutException as e:
            raise RenderScreenshotError.timeout() from e
        except httpx.RequestError as e:
            raise RenderScreenshotError.internal(str(e)) from e

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle API error responses.

        Args:
            response: The HTTP response.

        Raises:
            RenderScreenshotError: Always raised with error details.
        """
        retry_after: Optional[int] = None
        if "retry-after" in response.headers:
            with contextlib.suppress(ValueError):
                retry_after = int(response.headers["retry-after"])

        try:
            body = response.json()
        except Exception:
            body = {"message": response.text or "Unknown error"}

        raise RenderScreenshotError.from_response(response.status_code, body, retry_after)

    def generate_url(
        self,
        options: Union[TakeOptions, TakeOptionsConfig],
        expires_at: datetime,
    ) -> str:
        """Generate a signed URL for embedding screenshots.

        Signed URLs can be used in <img> tags or shared publicly.
        They don't require API key authentication but expire at the specified time.

        Args:
            options: Screenshot options (TakeOptions instance or config dict).
            expires_at: Expiration time for the signed URL (max 30 days).

        Returns:
            Signed URL string.

        Example:
            >>> from datetime import datetime, timedelta
            >>> options = TakeOptions.url("https://example.com").preset("og_card")
            >>> url = client.generate_url(
            ...     options,
            ...     datetime.now() + timedelta(hours=24)
            ... )
            >>> # Use in HTML: <img src="{url}" />
        """
        config = options.to_config() if isinstance(options, TakeOptions) else options

        # Build query params from config
        params: Dict[str, str] = {}

        if "url" in config:
            params["url"] = str(config["url"])
        if "width" in config:
            params["width"] = str(config["width"])
        if "height" in config:
            params["height"] = str(config["height"])
        if "scale" in config:
            params["scale"] = str(config["scale"])
        if "mobile" in config:
            params["mobile"] = str(config["mobile"]).lower()
        if "full_page" in config:
            params["full_page"] = str(config["full_page"]).lower()
        if "element" in config:
            params["element"] = str(config["element"])
        if "format" in config:
            params["format"] = str(config["format"])
        if "quality" in config:
            params["quality"] = str(config["quality"])
        if "preset" in config:
            params["preset"] = str(config["preset"])
        if "device" in config:
            params["device"] = str(config["device"])
        if "wait_for" in config:
            params["wait_for"] = str(config["wait_for"])
        if "delay" in config:
            params["delay"] = str(config["delay"])
        if "block_ads" in config:
            params["block_ads"] = str(config["block_ads"]).lower()
        if "block_trackers" in config:
            params["block_trackers"] = str(config["block_trackers"]).lower()
        if "block_cookie_banners" in config:
            params["block_cookie_banners"] = str(config["block_cookie_banners"]).lower()
        if "block_chat_widgets" in config:
            params["block_chat_widgets"] = str(config["block_chat_widgets"]).lower()
        if "dark_mode" in config:
            params["dark_mode"] = str(config["dark_mode"]).lower()
        if "cache_ttl" in config:
            params["cache_ttl"] = str(config["cache_ttl"])

        # Sort params alphabetically and create canonical string
        sorted_keys = sorted(params.keys())
        canonical = "&".join(f"{k}={params[k]}" for k in sorted_keys)

        # Add expiration
        expires = int(expires_at.timestamp())
        message = f"{canonical}&expires={expires}"

        # Generate signature
        signature = hmac.new(
            self._api_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return f"{self._base_url}/{API_VERSION}/screenshot?{message}&signature={signature}"

    def take(self, options: Union[TakeOptions, TakeOptionsConfig]) -> bytes:
        """Take a screenshot and return the binary data.

        Args:
            options: Screenshot options (TakeOptions instance or config dict).

        Returns:
            Bytes containing the screenshot image or PDF.

        Raises:
            RenderScreenshotError: If the screenshot fails.

        Example:
            >>> options = TakeOptions.url("https://example.com").preset("og_card")
            >>> image = client.take(options)
            >>> with open("screenshot.png", "wb") as f:
            ...     f.write(image)
        """
        params = (
            options.to_params()
            if isinstance(options, TakeOptions)
            else TakeOptions.from_config(options).to_params()
        )
        return self._request("POST", "/screenshot", body=params, response_type="buffer")

    def take_json(self, options: Union[TakeOptions, TakeOptionsConfig]) -> ScreenshotResponse:
        """Take a screenshot and return JSON metadata with URLs.

        Args:
            options: Screenshot options (TakeOptions instance or config dict).

        Returns:
            Screenshot response with metadata and URLs.

        Raises:
            RenderScreenshotError: If the screenshot fails.

        Example:
            >>> options = TakeOptions.url("https://example.com").preset("og_card")
            >>> response = client.take_json(options)
            >>> print(f"Screenshot URL: {response['url']}")
            >>> print(f"Size: {response['width']}x{response['height']}")
        """
        params = (
            options.to_params()
            if isinstance(options, TakeOptions)
            else TakeOptions.from_config(options).to_params()
        )
        params["response_type"] = "json"
        return self._request("POST", "/screenshot", body=params)

    @overload
    def batch(
        self,
        urls_or_requests: List[str],
        options: Optional[Union[TakeOptions, TakeOptionsConfig]] = ...,
    ) -> BatchResponse: ...

    @overload
    def batch(
        self,
        urls_or_requests: List[BatchRequestItem],
        options: None = ...,
    ) -> BatchResponse: ...

    def batch(
        self,
        urls_or_requests: Union[List[str], List[BatchRequestItem]],
        options: Optional[Union[TakeOptions, TakeOptionsConfig]] = None,
    ) -> BatchResponse:
        """Process multiple screenshots in a batch.

        This method has two call signatures:

        1. With a list of URLs and shared options:
           >>> results = client.batch(
           ...     ["https://example1.com", "https://example2.com"],
           ...     TakeOptions.url("").preset("og_card")
           ... )

        2. With a list of request items (per-URL options):
           >>> results = client.batch([
           ...     {"url": "https://example1.com", "options": {"width": 1200}},
           ...     {"url": "https://example2.com", "options": {"preset": "full_page"}}
           ... ])

        Args:
            urls_or_requests: List of URLs or list of BatchRequestItem dicts.
            options: Shared options for all URLs (only for URL list mode).

        Returns:
            Batch response with results for each URL.

        Raises:
            RenderScreenshotError: If the batch request fails.
        """
        body: Dict[str, Any]

        # Check if it's a list of strings (URLs)
        if urls_or_requests and isinstance(urls_or_requests[0], str):
            url_list: List[str] = urls_or_requests  # type: ignore[assignment]
            opts: Dict[str, Any] = {}
            if options is not None:
                opts = (
                    options.to_params()
                    if isinstance(options, TakeOptions)
                    else TakeOptions.from_config(options).to_params()
                )
            body = {"urls": url_list, "options": opts}
        else:
            # List of request items
            request_list: List[BatchRequestItem] = urls_or_requests  # type: ignore[assignment]
            body = {
                "requests": [
                    {
                        "url": req["url"],
                        **TakeOptions.from_config(req.get("options", {})).to_params(),
                    }
                    for req in request_list
                ]
            }

        return self._request("POST", "/batch", body=body)

    def get_batch(self, batch_id: str) -> BatchResponse:
        """Get the status of a batch job.

        Args:
            batch_id: The batch job ID.

        Returns:
            Batch status and results.

        Raises:
            RenderScreenshotError: If the batch is not found.

        Example:
            >>> response = client.get_batch("batch_abc123")
            >>> print(f"Status: {response['status']}")
            >>> print(f"Completed: {response['completed']}/{response['total']}")
        """
        return self._request("GET", f"/batch/{batch_id}")

    def presets(self) -> List[PresetInfo]:
        """List all available presets.

        Returns:
            List of preset configurations.

        Example:
            >>> for preset in client.presets():
            ...     print(f"{preset['id']}: {preset['description']}")
        """
        return self._request("GET", "/presets")

    def preset(self, preset_id: str) -> PresetInfo:
        """Get a single preset by ID.

        Args:
            preset_id: Preset identifier (e.g., "og_card").

        Returns:
            Preset configuration.

        Raises:
            RenderScreenshotError: If the preset is not found.

        Example:
            >>> preset = client.preset("og_card")
            >>> print(f"Size: {preset['width']}x{preset['height']}")
        """
        return self._request("GET", f"/presets/{preset_id}")

    def devices(self) -> List[DeviceInfo]:
        """List all available device presets.

        Returns:
            List of device configurations.

        Example:
            >>> for device in client.devices():
            ...     print(f"{device['id']}: {device['name']}")
        """
        return self._request("GET", "/devices")
