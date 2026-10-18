"""RenderScreenshot API client."""

from __future__ import annotations

import contextlib
import hashlib
import hmac
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, overload
from urllib.parse import quote_plus

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
SDK_VERSION = "1.0.1"


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
        signing_key: Optional[str] = None,
        public_key_id: Optional[str] = None,
    ) -> None:
        """Create a new RenderScreenshot client.

        Args:
            api_key: Your live API key (rs_live_*).
            base_url: Base URL for the API (optional, defaults to production).
            timeout: Request timeout in seconds (optional, defaults to 30).
            signing_key: Secret signing key (rs_secret_*) used by generate_url (optional).
            public_key_id: Public key ID (rs_pub_*) used by generate_url (optional).

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
            >>> # With signed URL credentials:
            >>> client = Client(
            ...     "rs_live_xxxxx",
            ...     signing_key="rs_secret_xxxxx",
            ...     public_key_id="rs_pub_xxxxx",
            ... )
        """
        if not api_key:
            raise ValueError("API key is required")

        self._api_key = api_key
        self._signing_key = signing_key
        self._public_key_id = public_key_id
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
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make an authenticated request to the API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.).
            path: API path (e.g., "/screenshot").
            body: Request body for POST/PUT requests.
            response_type: Expected response type ("json" or "buffer").
            headers: Extra request headers (optional).

        Returns:
            Parsed JSON response or bytes.

        Raises:
            RenderScreenshotError: If the API returns an error.
        """
        try:
            kwargs: Dict[str, Any] = {}
            if body is not None:
                kwargs["json"] = body
            if headers:
                kwargs["headers"] = headers

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
        expires_at: Union[datetime, int],
        *,
        signing_key: Optional[str] = None,
        public_key_id: Optional[str] = None,
    ) -> str:
        """Generate a signed URL for the GET screenshot endpoint.

        Signed URLs can be used in <img> tags or shared publicly. They don't
        need an API key, but they expire at the specified time (max 30 days).
        Signing needs your public key ID (rs_pub_*) and secret signing key
        (rs_secret_*), not your live API key. Pass them to ``Client()`` or
        directly to this method.

        Only options that ``GET /v1/screenshot`` supports are included (see
        ``TakeOptions.to_flat_params()``).

        Args:
            options: Screenshot options (TakeOptions instance or config dict).
            expires_at: Expiration time (datetime or Unix timestamp in seconds).
            signing_key: Override the client's signing key (rs_secret_*).
            public_key_id: Override the client's public key ID (rs_pub_*).

        Returns:
            Signed URL string.

        Raises:
            RenderScreenshotError: If signing_key or public_key_id is missing.

        Example:
            >>> from datetime import datetime, timedelta
            >>> client = Client(
            ...     "rs_live_xxxxx",
            ...     signing_key="rs_secret_xxxxx",
            ...     public_key_id="rs_pub_xxxxx",
            ... )
            >>> options = TakeOptions.url("https://example.com").preset("og_card")
            >>> url = client.generate_url(
            ...     options,
            ...     datetime.now() + timedelta(hours=24)
            ... )
            >>> # Use in HTML: <img src="{url}" />
        """
        secret = signing_key or self._signing_key
        key_id = public_key_id or self._public_key_id
        if not secret or not key_id:
            raise RenderScreenshotError.invalid_request(
                "Signed URLs require signing_key (rs_secret_*) and public_key_id (rs_pub_*). "
                "Pass them to Client() or to generate_url() directly."
            )

        take_options = (
            options if isinstance(options, TakeOptions) else TakeOptions.from_config(options)
        )
        expires = expires_at if isinstance(expires_at, int) else int(expires_at.timestamp())

        params = take_options.to_flat_params()
        params["expires"] = str(expires)
        params["key_id"] = key_id

        # Canonical query string: sorted keys, CGI.escape-style encoding
        # (matches Rails `request.query_parameters.except("signature").to_query`).
        query = "&".join(
            f"{quote_plus(key, safe='')}={quote_plus(params[key], safe='')}"
            for key in sorted(params)
        )

        signature = hmac.new(
            secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return f"{self._base_url}/{API_VERSION}/screenshot?{query}&signature={signature}"

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
            >>> print(f"Screenshot URL: {response['image']['url']}")
            >>> print(f"Size: {response['image']['width']}x{response['image']['height']}")
            >>> print(f"Cache hit: {response.get('cache', {}).get('hit')}")
        """
        params = (
            options.to_params()
            if isinstance(options, TakeOptions)
            else TakeOptions.from_config(options).to_params()
        )
        return self._request(
            "POST",
            "/screenshot",
            body=params,
            headers={"Accept": "application/json"},
        )

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
                # The target URLs come from `urls`; drop any placeholder target.
                opts.pop("url", None)
                opts.pop("html", None)
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
