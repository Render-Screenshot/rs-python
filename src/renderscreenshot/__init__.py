"""RenderScreenshot Python SDK.

Official Python SDK for RenderScreenshot - Screenshot API for developers.

Example:
    >>> from renderscreenshot import Client, TakeOptions
    >>>
    >>> # Initialize client
    >>> client = Client("rs_live_xxxxx")
    >>>
    >>> # Take a screenshot
    >>> options = (
    ...     TakeOptions.url("https://example.com")
    ...     .preset("og_card")
    ...     .block_ads()
    ... )
    >>> image = client.take(options)
    >>>
    >>> # Save to file
    >>> with open("screenshot.png", "wb") as f:
    ...     f.write(image)

For more information, visit: https://renderscreenshot.com/docs
"""

from .client import Client
from .errors import RenderScreenshotError
from .options import TakeOptions
from .types import (
    BatchRequestItem,
    BatchResponse,
    BatchResponseItem,
    BatchStatus,
    BlockableResource,
    Cookie,
    Device,
    DeviceInfo,
    Geolocation,
    ImageFormat,
    MediaType,
    PdfPaperSize,
    Preset,
    PresetInfo,
    PurgeResult,
    ScreenshotResponse,
    StorageAcl,
    TakeOptionsConfig,
    WaitCondition,
    WebhookEvent,
    WebhookEventType,
)
from .webhooks import extract_webhook_headers, parse_webhook, verify_webhook

__version__ = "1.0.0"

__all__ = [
    "BatchRequestItem",
    "BatchResponse",
    "BatchResponseItem",
    "BatchStatus",
    "BlockableResource",
    "Client",
    "Cookie",
    "Device",
    "DeviceInfo",
    "Geolocation",
    "ImageFormat",
    "MediaType",
    "PdfPaperSize",
    "Preset",
    "PresetInfo",
    "PurgeResult",
    "RenderScreenshotError",
    "ScreenshotResponse",
    "StorageAcl",
    "TakeOptions",
    "TakeOptionsConfig",
    "WaitCondition",
    "WebhookEvent",
    "WebhookEventType",
    "__version__",
    "extract_webhook_headers",
    "parse_webhook",
    "verify_webhook",
]
