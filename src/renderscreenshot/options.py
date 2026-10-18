"""Fluent builder for screenshot options."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from .types import (
    BlockableResource,
    Cookie,
    Device,
    Geolocation,
    ImageFormat,
    MediaType,
    PdfPaperSize,
    Preset,
    StorageAcl,
    TakeOptionsConfig,
    WaitCondition,
)


class TakeOptions:
    """Fluent builder for screenshot options.

    Use the static methods `url()` or `html()` to create a new instance,
    then chain method calls to configure the screenshot options.

    Example:
        >>> options = (
        ...     TakeOptions.url("https://example.com")
        ...     .width(1200)
        ...     .height(630)
        ...     .format("png")
        ...     .block_ads()
        ... )
        >>> image = client.take(options)
    """

    def __init__(self, config: Optional[TakeOptionsConfig] = None) -> None:
        """Create a new TakeOptions instance.

        Args:
            config: Initial configuration dictionary (optional).
        """
        self._config: TakeOptionsConfig = dict(config) if config else {}  # type: ignore

    @classmethod
    def url(cls, url: str) -> "TakeOptions":
        """Create options with a URL target.

        Args:
            url: The URL to capture.

        Returns:
            A new TakeOptions instance.

        Example:
            >>> options = TakeOptions.url("https://example.com")
        """
        return cls({"url": url})  # type: ignore

    @classmethod
    def html(cls, html: str) -> "TakeOptions":
        """Create options with HTML content.

        Args:
            html: The HTML content to render.

        Returns:
            A new TakeOptions instance.

        Example:
            >>> options = TakeOptions.html("<h1>Hello World</h1>")
        """
        return cls({"html": html})  # type: ignore

    @classmethod
    def from_config(cls, config: TakeOptionsConfig) -> "TakeOptions":
        """Create options from an existing config dictionary.

        Args:
            config: Configuration dictionary.

        Returns:
            A new TakeOptions instance.
        """
        return cls(config)

    def _copy_with(self, **kwargs: Any) -> "TakeOptions":
        """Create a copy with updated values (immutable pattern)."""
        new_config = dict(self._config)  # type: ignore
        new_config.update(kwargs)
        return TakeOptions(new_config)  # type: ignore

    # --- Viewport ---

    def width(self, value: int) -> "TakeOptions":
        """Set viewport width in pixels.

        Args:
            value: Width in pixels (e.g., 1200).

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(width=value)

    def height(self, value: int) -> "TakeOptions":
        """Set viewport height in pixels.

        Args:
            value: Height in pixels (e.g., 630).

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(height=value)

    def scale(self, value: float) -> "TakeOptions":
        """Set device scale factor (1-3).

        Args:
            value: Scale factor (e.g., 2 for retina).

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(scale=value)

    def mobile(self, value: bool = True) -> "TakeOptions":
        """Enable mobile emulation.

        Args:
            value: True to enable mobile mode.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(mobile=value)

    # --- Capture ---

    def full_page(self, value: bool = True) -> "TakeOptions":
        """Capture full scrollable page.

        Args:
            value: True to capture full page.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(full_page=value)

    def element(self, selector: str) -> "TakeOptions":
        """Capture specific element by CSS selector.

        Args:
            selector: CSS selector (e.g., "#main", ".content").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(element=selector)

    def format(self, value: ImageFormat) -> "TakeOptions":
        """Set output format.

        Args:
            value: Image format ("png", "jpeg", "webp", "pdf").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(format=value)

    def quality(self, value: int) -> "TakeOptions":
        """Set JPEG/WebP quality (1-100).

        Args:
            value: Quality percentage.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(quality=value)

    # --- Wait ---

    def wait_for(self, value: WaitCondition) -> "TakeOptions":
        """Set wait condition.

        Args:
            value: Wait condition ("load", "networkidle", "domcontentloaded").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(wait_for=value)

    def delay(self, value: int) -> "TakeOptions":
        """Add delay after page load (milliseconds).

        Args:
            value: Delay in milliseconds.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(delay=value)

    def wait_for_selector(self, selector: str) -> "TakeOptions":
        """Wait for CSS selector to appear.

        Args:
            selector: CSS selector to wait for.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(wait_for_selector=selector)

    def wait_for_timeout(self, value: int) -> "TakeOptions":
        """Maximum wait time in seconds.

        Args:
            value: Timeout in seconds (the API clamps it to 1-60).

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(wait_for_timeout=value)

    # --- Presets ---

    def preset(self, value: Preset) -> "TakeOptions":
        """Use a preset configuration.

        Args:
            value: Preset identifier (e.g., "og_card", "twitter_card").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(preset=value)

    def device(self, value: Device) -> "TakeOptions":
        """Emulate a specific device.

        Args:
            value: Device identifier (e.g., "iphone_14_pro", "pixel_7").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(device=value)

    # --- Blocking ---

    def block_ads(self, value: bool = True) -> "TakeOptions":
        """Block ad network domains.

        Args:
            value: True to block ads.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(block_ads=value)

    def block_trackers(self, value: bool = True) -> "TakeOptions":
        """Block analytics/tracking.

        Args:
            value: True to block trackers.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(block_trackers=value)

    def block_cookie_banners(self, value: bool = True) -> "TakeOptions":
        """Auto-dismiss cookie popups.

        Args:
            value: True to block cookie banners.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(block_cookie_banners=value)

    def block_chat_widgets(self, value: bool = True) -> "TakeOptions":
        """Block chat widgets.

        Args:
            value: True to block chat widgets.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(block_chat_widgets=value)

    def block_urls(self, patterns: List[str]) -> "TakeOptions":
        """Block URLs matching patterns (glob).

        Args:
            patterns: List of glob patterns to block.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(block_urls=patterns)

    def block_resources(self, types: List[BlockableResource]) -> "TakeOptions":
        """Block specific resource types.

        Args:
            types: List of resource types to block.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(block_resources=types)

    # --- Page manipulation ---

    def inject_script(self, script: str) -> "TakeOptions":
        """Inject JavaScript (inline or URL).

        Args:
            script: JavaScript code or URL to a script file.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(inject_script=script)

    def inject_style(self, style: str) -> "TakeOptions":
        """Inject CSS (inline or URL).

        Args:
            style: CSS code or URL to a stylesheet.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(inject_style=style)

    def click(self, selector: str) -> "TakeOptions":
        """Click element before capture.

        Args:
            selector: CSS selector of element to click.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(click=selector)

    def hide(self, selectors: List[str]) -> "TakeOptions":
        """Hide elements (visibility: hidden).

        Args:
            selectors: List of CSS selectors to hide.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(hide=selectors)

    def remove(self, selectors: List[str]) -> "TakeOptions":
        """Remove elements from DOM.

        Args:
            selectors: List of CSS selectors to remove.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(remove=selectors)

    # --- Browser emulation ---

    def dark_mode(self, value: bool = True) -> "TakeOptions":
        """Enable dark mode (prefers-color-scheme: dark).

        Args:
            value: True to enable dark mode.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(dark_mode=value)

    def reduced_motion(self, value: bool = True) -> "TakeOptions":
        """Enable reduced motion preference.

        Args:
            value: True to enable reduced motion.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(reduced_motion=value)

    def media_type(self, value: MediaType) -> "TakeOptions":
        """Set media type emulation.

        Args:
            value: Media type ("screen" or "print").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(media_type=value)

    def user_agent(self, value: str) -> "TakeOptions":
        """Set custom user agent.

        Args:
            value: User agent string.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(user_agent=value)

    def timezone(self, value: str) -> "TakeOptions":
        """Set timezone (IANA format).

        Args:
            value: Timezone identifier (e.g., "America/New_York").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(timezone=value)

    def locale(self, value: str) -> "TakeOptions":
        """Set locale (BCP 47 format).

        Args:
            value: Locale identifier (e.g., "en-US", "fr-FR").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(locale=value)

    def geolocation(
        self, latitude: float, longitude: float, accuracy: Optional[float] = None
    ) -> "TakeOptions":
        """Set geolocation coordinates.

        Args:
            latitude: Latitude coordinate.
            longitude: Longitude coordinate.
            accuracy: Accuracy in meters (optional).

        Returns:
            A new TakeOptions instance.
        """
        geo: Geolocation = {"latitude": latitude, "longitude": longitude}
        if accuracy is not None:
            geo["accuracy"] = accuracy
        return self._copy_with(geolocation=geo)

    # --- Network ---

    def headers(self, value: Dict[str, str]) -> "TakeOptions":
        """Set custom HTTP headers.

        Args:
            value: Dictionary of header name-value pairs.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(headers=value)

    def cookies(self, value: List[Cookie]) -> "TakeOptions":
        """Set cookies.

        Args:
            value: List of cookie dictionaries.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(cookies=value)

    def auth_basic(self, username: str, password: str) -> "TakeOptions":
        """Set HTTP Basic authentication.

        Args:
            username: Username for authentication.
            password: Password for authentication.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(auth_basic={"username": username, "password": password})

    def auth_bearer(self, token: str) -> "TakeOptions":
        """Set Bearer token authentication.

        Args:
            token: Bearer token.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(auth_bearer=token)

    def bypass_csp(self, value: bool = True) -> "TakeOptions":
        """Bypass Content Security Policy.

        Args:
            value: True to bypass CSP.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(bypass_csp=value)

    # --- Cache ---

    def cache_ttl(self, value: int) -> "TakeOptions":
        """Set cache TTL in seconds (3600-2592000).

        Args:
            value: TTL in seconds.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(cache_ttl=value)

    def cache_refresh(self, value: bool = True) -> "TakeOptions":
        """Force cache refresh.

        Args:
            value: True to force refresh.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(cache_refresh=value)

    def cache_available(self, value: bool = True) -> "TakeOptions":
        """Serve a previous screenshot with the same options when one exists.

        The API reuses a cached render (cache.available) only when this is set.

        Args:
            value: True to allow reuse of a cached render.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(cache_available=value)

    # --- PDF options ---

    def pdf_paper_size(self, value: PdfPaperSize) -> "TakeOptions":
        """Set PDF paper size.

        Args:
            value: Paper size (e.g., "a4", "letter").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_paper_size=value)

    def pdf_width(self, value: str) -> "TakeOptions":
        """Set custom PDF width (CSS units).

        Args:
            value: Width string (e.g., "8.5in").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_width=value)

    def pdf_height(self, value: str) -> "TakeOptions":
        """Set custom PDF height (CSS units).

        Args:
            value: Height string (e.g., "11in").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_height=value)

    def pdf_landscape(self, value: bool = True) -> "TakeOptions":
        """Set PDF landscape orientation.

        Args:
            value: True for landscape.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_landscape=value)

    def pdf_margin(self, value: str) -> "TakeOptions":
        """Set uniform PDF margin (CSS units).

        Args:
            value: Margin string (e.g., "1in", "20mm").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_margin=value)

    def pdf_margin_top(self, value: str) -> "TakeOptions":
        """Set PDF top margin.

        Args:
            value: Top margin string.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_margin_top=value)

    def pdf_margin_right(self, value: str) -> "TakeOptions":
        """Set PDF right margin.

        Args:
            value: Right margin string.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_margin_right=value)

    def pdf_margin_bottom(self, value: str) -> "TakeOptions":
        """Set PDF bottom margin.

        Args:
            value: Bottom margin string.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_margin_bottom=value)

    def pdf_margin_left(self, value: str) -> "TakeOptions":
        """Set PDF left margin.

        Args:
            value: Left margin string.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_margin_left=value)

    def pdf_scale(self, value: float) -> "TakeOptions":
        """Set PDF scale factor (0.1-2.0).

        Args:
            value: Scale factor.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_scale=value)

    def pdf_print_background(self, value: bool = True) -> "TakeOptions":
        """Include background graphics in PDF.

        Args:
            value: True to include backgrounds.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_print_background=value)

    def pdf_page_ranges(self, value: str) -> "TakeOptions":
        """Set PDF page ranges (e.g., "1-5, 8").

        Args:
            value: Page ranges string.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_page_ranges=value)

    def pdf_header(self, value: str) -> "TakeOptions":
        """Set PDF header HTML template.

        Args:
            value: HTML template for header.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_header=value)

    def pdf_footer(self, value: str) -> "TakeOptions":
        """Set PDF footer HTML template.

        Args:
            value: HTML template for footer.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_footer=value)

    def pdf_fit_one_page(self, value: bool = True) -> "TakeOptions":
        """Fit content to single PDF page.

        Args:
            value: True to fit to one page.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_fit_one_page=value)

    def pdf_prefer_css_page_size(self, value: bool = True) -> "TakeOptions":
        """Use CSS-defined page size for PDF.

        Args:
            value: True to use CSS page size.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(pdf_prefer_css_page_size=value)

    # --- Storage (BYOS) ---

    def storage_enabled(self, value: bool = True) -> "TakeOptions":
        """Enable custom storage upload.

        Args:
            value: True to enable storage.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(storage_enabled=value)

    def storage_path(self, value: str) -> "TakeOptions":
        """Set storage path template.

        Supports variables: {hash}, {ext}, {year}, {month}, {day},
        {timestamp}, {domain}, {uuid}

        Args:
            value: Path template string.

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(storage_path=value)

    def storage_acl(self, value: StorageAcl) -> "TakeOptions":
        """Set storage ACL.

        Args:
            value: ACL setting ("public-read" or "private").

        Returns:
            A new TakeOptions instance.
        """
        return self._copy_with(storage_acl=value)

    # --- Output ---

    def to_config(self) -> TakeOptionsConfig:
        """Get the raw configuration dictionary.

        Returns:
            Copy of the configuration dictionary.
        """
        return dict(self._config)  # type: ignore

    def to_params(self) -> Dict[str, Any]:
        """Convert to API request parameters (for POST body).

        This method converts the configuration to the nested JSON format
        expected by ``POST /v1/screenshot`` (for example ``viewport.width``,
        ``capture.mode``, ``output.format``, ``wait.for_selector``).

        Returns:
            Dictionary suitable for JSON POST body.
        """
        params: Dict[str, Any] = {}
        config: Dict[str, Any] = self._config  # type: ignore[assignment]

        # Top-level params
        for key in ("url", "html", "preset", "device"):
            if key in config:
                params[key] = config[key]

        # Viewport
        viewport: Dict[str, Any] = {}
        for key in ("width", "height", "scale", "mobile"):
            if key in config:
                viewport[key] = config[key]
        if viewport:
            params["viewport"] = viewport

        # Capture
        capture: Dict[str, Any] = {}
        if config.get("full_page"):
            capture["mode"] = "full_page"
        if config.get("element"):
            capture["selector"] = config["element"]
        if capture:
            params["capture"] = capture

        # Output
        output: Dict[str, Any] = {}
        if "format" in config:
            output["format"] = config["format"]
        if "quality" in config:
            output["quality"] = config["quality"]
        if output:
            params["output"] = output

        # Wait
        wait: Dict[str, Any] = {}
        if "wait_for" in config:
            wait["until"] = config["wait_for"]
        if "delay" in config:
            wait["delay"] = config["delay"]
        if "wait_for_selector" in config:
            wait["for_selector"] = config["wait_for_selector"]
        if "wait_for_timeout" in config:
            wait["timeout"] = config["wait_for_timeout"]
        if wait:
            params["wait"] = wait

        # Block
        block: Dict[str, Any] = {}
        if "block_ads" in config:
            block["ads"] = config["block_ads"]
        if "block_trackers" in config:
            block["trackers"] = config["block_trackers"]
        if "block_cookie_banners" in config:
            block["cookie_banners"] = config["block_cookie_banners"]
        if "block_chat_widgets" in config:
            block["chat_widgets"] = config["block_chat_widgets"]
        if "block_urls" in config:
            block["requests"] = config["block_urls"]
        if "block_resources" in config:
            block["resources"] = config["block_resources"]
        if block:
            params["block"] = block

        # Page
        page: Dict[str, Any] = {}
        if "inject_script" in config:
            page["scripts"] = [config["inject_script"]]
        if "inject_style" in config:
            page["styles"] = [config["inject_style"]]
        if "click" in config:
            page["click"] = config["click"]
        if "hide" in config:
            page["hide"] = config["hide"]
        if "remove" in config:
            page["remove"] = config["remove"]
        if page:
            params["page"] = page

        # Browser
        browser: Dict[str, Any] = {}
        if "dark_mode" in config:
            browser["dark_mode"] = config["dark_mode"]
        if "reduced_motion" in config:
            browser["reduced_motion"] = config["reduced_motion"]
        if "media_type" in config:
            browser["media"] = config["media_type"]
        if "user_agent" in config:
            browser["user_agent"] = config["user_agent"]
        if "timezone" in config:
            browser["timezone"] = config["timezone"]
        if "locale" in config:
            browser["locale"] = config["locale"]
        if "geolocation" in config:
            browser["geolocation"] = config["geolocation"]
        if browser:
            params["browser"] = browser

        # Network
        network: Dict[str, Any] = {}
        if "headers" in config:
            network["headers"] = config["headers"]
        if "cookies" in config:
            network["cookies"] = config["cookies"]
        if "bypass_csp" in config:
            network["bypass_csp"] = config["bypass_csp"]
        if "auth_basic" in config:
            network["auth"] = {"type": "basic", **config["auth_basic"]}
        elif "auth_bearer" in config:
            network["auth"] = {"type": "bearer", "token": config["auth_bearer"]}
        if network:
            params["network"] = network

        # Cache
        cache: Dict[str, Any] = {}
        if "cache_ttl" in config:
            cache["ttl"] = config["cache_ttl"]
        if "cache_refresh" in config:
            cache["refresh"] = config["cache_refresh"]
        if "cache_available" in config:
            cache["available"] = config["cache_available"]
        if cache:
            params["cache"] = cache

        # PDF
        pdf: Dict[str, Any] = {}
        pdf_mapping = (
            ("pdf_paper_size", "paper"),
            ("pdf_width", "width"),
            ("pdf_height", "height"),
            ("pdf_landscape", "landscape"),
            ("pdf_scale", "scale"),
            ("pdf_print_background", "print_background"),
            ("pdf_page_ranges", "page_ranges"),
            ("pdf_header", "header"),
            ("pdf_footer", "footer"),
            ("pdf_fit_one_page", "fit_one_page"),
            ("pdf_prefer_css_page_size", "prefer_css_page_size"),
            ("pdf_margin", "margin"),
            ("pdf_margin_top", "margin_top"),
            ("pdf_margin_right", "margin_right"),
            ("pdf_margin_bottom", "margin_bottom"),
            ("pdf_margin_left", "margin_left"),
        )
        for config_key, api_key in pdf_mapping:
            if config_key in config:
                pdf[api_key] = config[config_key]
        if pdf:
            params["pdf"] = pdf

        # Storage
        storage: Dict[str, Any] = {}
        if "storage_enabled" in config:
            storage["enabled"] = config["storage_enabled"]
        if "storage_path" in config:
            storage["path"] = config["storage_path"]
        if "storage_acl" in config:
            storage["acl"] = config["storage_acl"]
        if storage:
            params["storage"] = storage

        return params

    # Config key -> flat query parameter name read by GET /v1/screenshot.
    _QUERY_PARAM_NAMES = (
        ("url", "url"),
        ("html", "html"),
        ("preset", "preset"),
        ("device", "device"),
        ("width", "width"),
        ("height", "height"),
        ("scale", "scale"),
        ("full_page", "full_page"),
        ("element", "selector"),
        ("format", "format"),
        ("quality", "quality"),
        ("delay", "delay"),
        ("wait_for_timeout", "timeout"),
        ("click", "click"),
        ("hide", "hide"),
        ("remove", "remove"),
        ("block_ads", "block_ads"),
        ("block_cookie_banners", "block_cookies"),
        ("dark_mode", "dark_mode"),
        ("user_agent", "user_agent"),
        ("locale", "locale"),
        ("timezone", "timezone"),
        ("cache_ttl", "cache_ttl"),
        ("cache_refresh", "cache_refresh"),
        ("cache_available", "cache_available"),
        ("pdf_paper_size", "pdf_paper"),
        ("pdf_width", "pdf_width"),
        ("pdf_height", "pdf_height"),
        ("pdf_landscape", "pdf_landscape"),
        ("pdf_scale", "pdf_scale"),
        ("pdf_fit_one_page", "pdf_fit_one_page"),
        ("pdf_margin", "pdf_margin"),
        ("pdf_margin_top", "pdf_margin_top"),
        ("pdf_margin_right", "pdf_margin_right"),
        ("pdf_margin_bottom", "pdf_margin_bottom"),
        ("pdf_margin_left", "pdf_margin_left"),
        ("pdf_print_background", "pdf_print_background"),
        ("pdf_prefer_css_page_size", "pdf_prefer_css_page_size"),
        ("pdf_page_ranges", "pdf_page_ranges"),
        ("pdf_header", "pdf_header"),
        ("pdf_footer", "pdf_footer"),
    )

    def to_flat_params(self) -> Dict[str, str]:
        """Convert to flat query parameters (for GET requests and signed URLs).

        Only options that ``GET /v1/screenshot`` reads from the query string are
        included. Booleans become ``"true"``/``"false"`` and lists are joined with
        commas. Options that the GET endpoint does not support (for example
        ``mobile``, ``wait_for``, ``wait_for_selector``, ``block_trackers``,
        network, storage) are left out; use ``Client.take()`` (POST) for those.

        Returns:
            Dictionary of query parameter names to string values.
        """
        config: Dict[str, Any] = self._config  # type: ignore[assignment]
        params: Dict[str, str] = {}
        for config_key, param_name in self._QUERY_PARAM_NAMES:
            if config_key not in config or config[config_key] is None:
                continue
            params[param_name] = _flat_value(config[config_key])
        return params

    def to_query_string(self) -> str:
        """Convert to URL query string (for GET requests).

        This method converts the configuration to flat query parameters
        suitable for GET requests. Keys are sorted and values are encoded the
        same way as signed URLs (space becomes ``+``).

        Returns:
            URL-encoded query string.
        """
        params = self.to_flat_params()
        return "&".join(
            f"{quote_plus(key, safe='')}={quote_plus(params[key], safe='')}"
            for key in sorted(params)
        )


def _flat_value(value: Any) -> str:
    """Convert an option value to its flat query-string form."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ",".join(str(v) for v in value)
    return str(value)
