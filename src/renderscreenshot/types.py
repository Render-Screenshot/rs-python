"""Type definitions for the RenderScreenshot SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, TypedDict, Union

# Screenshot format options
ImageFormat = Literal["png", "jpeg", "webp", "pdf"]

# Wait condition types
WaitCondition = Literal["load", "networkidle", "domcontentloaded"]

# Resource types that can be blocked
BlockableResource = Literal["font", "media", "image", "script", "stylesheet"]

# Media type emulation
MediaType = Literal["screen", "print"]

# Storage ACL options
StorageAcl = Literal["public-read", "private"]

# Preset identifiers
Preset = Literal[
    "og_card",
    "twitter_card",
    "twitter_card_large",
    "full_page",
    "mobile",
    "mobile_landscape",
    "desktop_hd",
    "desktop_4k",
    "link_preview",
    "pdf_document",
]

# Device identifiers
Device = Literal[
    "iphone_14_pro",
    "iphone_14",
    "iphone_se",
    "pixel_7",
    "pixel_7_pro",
    "samsung_galaxy_s23",
    "ipad_pro_12",
    "ipad_air",
    "macbook_pro_16",
    "macbook_air_15",
    "imac_24",
    "desktop_1080p",
    "desktop_1440p",
    "desktop_4k",
    "surface_pro",
]

# PDF paper size options
PdfPaperSize = Literal["a0", "a1", "a2", "a3", "a4", "a5", "a6", "letter", "legal", "tabloid"]

# Cookie SameSite attribute
SameSite = Literal["Strict", "Lax", "None"]


class Cookie(TypedDict, total=False):
    """Cookie configuration."""

    name: str
    value: str
    domain: str
    path: str
    expires: int
    http_only: bool
    secure: bool
    same_site: SameSite


class Geolocation(TypedDict, total=False):
    """Geolocation configuration."""

    latitude: float
    longitude: float
    accuracy: float


class AuthBasic(TypedDict):
    """HTTP Basic authentication credentials."""

    username: str
    password: str


class TakeOptionsConfig(TypedDict, total=False):
    """Screenshot options configuration."""

    # Target
    url: str
    html: str

    # Viewport
    width: int
    height: int
    scale: float
    mobile: bool

    # Capture
    full_page: bool
    element: str
    format: ImageFormat
    quality: int

    # Wait
    wait_for: WaitCondition
    delay: int
    wait_for_selector: str
    wait_for_timeout: int

    # Presets
    preset: Preset
    device: Device

    # Blocking
    block_ads: bool
    block_trackers: bool
    block_cookie_banners: bool
    block_chat_widgets: bool
    block_urls: List[str]
    block_resources: List[BlockableResource]

    # Page manipulation
    inject_script: str
    inject_style: str
    click: str
    hide: List[str]
    remove: List[str]

    # Browser emulation
    dark_mode: bool
    reduced_motion: bool
    media_type: MediaType
    user_agent: str
    timezone: str
    locale: str
    geolocation: Geolocation

    # Network
    headers: Dict[str, str]
    cookies: List[Cookie]
    auth_basic: AuthBasic
    auth_bearer: str
    bypass_csp: bool

    # Cache
    cache_ttl: int
    cache_refresh: bool

    # PDF options
    pdf_paper_size: PdfPaperSize
    pdf_width: str
    pdf_height: str
    pdf_landscape: bool
    pdf_margin: str
    pdf_margin_top: str
    pdf_margin_right: str
    pdf_margin_bottom: str
    pdf_margin_left: str
    pdf_scale: float
    pdf_print_background: bool
    pdf_page_ranges: str
    pdf_header: str
    pdf_footer: str
    pdf_fit_one_page: bool
    pdf_prefer_css_page_size: bool

    # Storage (BYOS)
    storage_enabled: bool
    storage_path: str
    storage_acl: StorageAcl


class ScreenshotResponse(TypedDict, total=False):
    """Screenshot response from take_json."""

    url: str
    cache_url: str
    width: int
    height: int
    format: ImageFormat
    size: int
    cache_key: str
    ttl: int
    cached: bool
    storage_path: str


class BatchRequestItem(TypedDict, total=False):
    """Batch request item."""

    url: str
    options: TakeOptionsConfig


class BatchError(TypedDict):
    """Error in a batch response item."""

    code: str
    message: str


class BatchResponseItem(TypedDict, total=False):
    """Batch response item."""

    url: str
    success: bool
    response: ScreenshotResponse
    error: BatchError


# Batch status types
BatchStatus = Literal["pending", "processing", "completed", "failed"]


class BatchResponse(TypedDict):
    """Batch response."""

    id: str
    status: BatchStatus
    total: int
    completed: int
    failed: int
    results: List[BatchResponseItem]


class CacheEntry(TypedDict):
    """Cache entry metadata."""

    key: str
    url: str
    created_at: str
    expires_at: str
    size: int
    format: ImageFormat


class PurgeResult(TypedDict):
    """Purge operation result."""

    purged: int
    keys: List[str]


# Webhook event types
WebhookEventType = Literal[
    "screenshot.completed",
    "screenshot.failed",
    "batch.completed",
    "batch.failed",
]


class WebhookEventData(TypedDict, total=False):
    """Webhook event data."""

    url: str
    batch_id: str
    response: ScreenshotResponse
    error: BatchError


class WebhookEvent(TypedDict):
    """Webhook event payload."""

    id: str
    type: WebhookEventType
    timestamp: datetime
    data: WebhookEventData


class PresetInfo(TypedDict, total=False):
    """Preset metadata."""

    id: Preset
    name: str
    description: str
    width: int
    height: int
    scale: float
    format: ImageFormat


class DeviceInfo(TypedDict):
    """Device metadata."""

    id: Device
    name: str
    width: int
    height: int
    scale: float
    mobile: bool
    user_agent: str


# Type for options parameter (can be TakeOptions or dict)
OptionsLike = Union["TakeOptions", TakeOptionsConfig, Dict[str, Any]]

# Import TakeOptions at runtime to avoid circular import
if False:  # TYPE_CHECKING
    from .options import TakeOptions
