# RenderScreenshot Python SDK

Official Python SDK for [RenderScreenshot](https://renderscreenshot.com) - Screenshot API for developers.

[![PyPI version](https://badge.fury.io/py/renderscreenshot.svg)](https://pypi.org/project/renderscreenshot/)
[![Python versions](https://img.shields.io/pypi/pyversions/renderscreenshot.svg)](https://pypi.org/project/renderscreenshot/)
[![CI](https://github.com/renderscreenshot/rs-python/actions/workflows/ci.yml/badge.svg)](https://github.com/renderscreenshot/rs-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install renderscreenshot
```

## Quick Start

```python
from renderscreenshot import Client, TakeOptions

# Initialize client
client = Client("rs_live_xxxxx")

# Take a screenshot
options = (
    TakeOptions.url("https://example.com")
    .preset("og_card")
    .block_ads()
)
image = client.take(options)

# Save to file
with open("screenshot.png", "wb") as f:
    f.write(image)
```

## Features

- **Simple API** - Fluent builder pattern for easy configuration
- **Full Type Hints** - Complete type annotations for IDE support
- **Presets** - Built-in presets for common use cases (OG cards, Twitter cards, etc.)
- **Device Emulation** - Emulate iPhone, Pixel, iPad, and more
- **Content Blocking** - Block ads, trackers, cookie banners, and chat widgets
- **PDF Generation** - Convert pages to PDF with full customization
- **Batch Processing** - Process multiple URLs efficiently
- **Cache Management** - Control caching and purge cached screenshots
- **Webhook Support** - Verify and parse webhook payloads
- **Signed URLs** - Generate signed URLs for embedding

## Usage

### Basic Screenshot

```python
from renderscreenshot import Client, TakeOptions

client = Client("rs_live_xxxxx")

# Simple screenshot
image = client.take(TakeOptions.url("https://example.com"))

# With options
options = (
    TakeOptions.url("https://example.com")
    .width(1200)
    .height(630)
    .format("png")
)
image = client.take(options)
```

### Using Presets

```python
# OG Card (1200x630)
options = TakeOptions.url("https://example.com").preset("og_card")

# Twitter Card
options = TakeOptions.url("https://example.com").preset("twitter_card")

# Full Page Screenshot
options = TakeOptions.url("https://example.com").preset("full_page")
```

### Device Emulation

```python
# iPhone 14 Pro
options = TakeOptions.url("https://example.com").device("iphone_14_pro")

# Pixel 7
options = TakeOptions.url("https://example.com").device("pixel_7")

# iPad Pro
options = TakeOptions.url("https://example.com").device("ipad_pro_12")
```

### Content Blocking

```python
options = (
    TakeOptions.url("https://example.com")
    .block_ads()
    .block_trackers()
    .block_cookie_banners()
    .block_chat_widgets()
)
```

### Dark Mode

```python
options = (
    TakeOptions.url("https://example.com")
    .dark_mode()
    .preset("og_card")
)
```

### PDF Generation

```python
options = (
    TakeOptions.url("https://example.com")
    .format("pdf")
    .pdf_paper_size("a4")
    .pdf_margin("1in")
    .pdf_print_background()
)
pdf = client.take(options)
```

### JSON Response

```python
# Get metadata along with screenshot URL
response = client.take_json(
    TakeOptions.url("https://example.com").preset("og_card")
)
print(f"Screenshot URL: {response['url']}")
print(f"Size: {response['width']}x{response['height']}")
print(f"File size: {response['size']} bytes")
```

### Batch Processing

```python
# Multiple URLs with shared options
urls = ["https://example1.com", "https://example2.com", "https://example3.com"]
options = TakeOptions.url("").preset("og_card")
results = client.batch(urls, options)

# Per-URL options
requests = [
    {"url": "https://example1.com", "options": {"width": 1200}},
    {"url": "https://example2.com", "options": {"preset": "full_page"}},
]
results = client.batch(requests)

# Check batch status
status = client.get_batch("batch_123")
print(f"Completed: {status['completed']}/{status['total']}")
```

### Signed URLs

```python
from datetime import datetime, timedelta

# Generate a signed URL that expires in 24 hours
options = TakeOptions.url("https://example.com").preset("og_card")
signed_url = client.generate_url(
    options,
    datetime.now() + timedelta(hours=24)
)

# Use in HTML: <img src="{signed_url}" />
```

### Cache Management

```python
# Get cached screenshot
image = client.cache.get("cache_key")

# Delete cache entry
deleted = client.cache.delete("cache_key")

# Bulk purge
result = client.cache.purge(["key1", "key2", "key3"])

# Purge by URL pattern
result = client.cache.purge_url("https://mysite.com/blog/*")

# Purge by date
from datetime import datetime
result = client.cache.purge_before(datetime(2024, 1, 1))
```

### Webhook Verification

```python
from renderscreenshot import verify_webhook, parse_webhook

# In your webhook handler
def handle_webhook(request):
    signature = request.headers.get("X-Webhook-Signature")
    timestamp = request.headers.get("X-Webhook-Timestamp")
    payload = request.get_data(as_text=True)

    if not verify_webhook(payload, signature, timestamp, WEBHOOK_SECRET):
        return "Invalid signature", 401

    event = parse_webhook(payload)

    if event["type"] == "screenshot.completed":
        response = event["data"]["response"]
        print(f"Screenshot ready: {response['url']}")

    return "OK", 200
```

### Context Manager

```python
# Automatically closes the client when done
with Client("rs_live_xxxxx") as client:
    image = client.take(TakeOptions.url("https://example.com"))
```

## All Options

### Target
- `url(str)` - URL to capture
- `html(str)` - HTML content to render

### Viewport
- `width(int)` - Viewport width in pixels
- `height(int)` - Viewport height in pixels
- `scale(float)` - Device scale factor (1-3)
- `mobile(bool)` - Enable mobile emulation

### Capture
- `full_page(bool)` - Capture full scrollable page
- `element(str)` - CSS selector for element capture
- `format(str)` - Output format: `png`, `jpeg`, `webp`, `pdf`
- `quality(int)` - JPEG/WebP quality (1-100)

### Wait
- `wait_for(str)` - Wait condition: `load`, `networkidle`, `domcontentloaded`
- `delay(int)` - Additional delay in milliseconds
- `wait_for_selector(str)` - Wait for CSS selector to appear
- `wait_for_timeout(int)` - Maximum wait time in milliseconds

### Presets
- `preset(str)` - Use preset: `og_card`, `twitter_card`, `full_page`, etc.
- `device(str)` - Emulate device: `iphone_14_pro`, `pixel_7`, etc.

### Blocking
- `block_ads(bool)` - Block ad network domains
- `block_trackers(bool)` - Block analytics/tracking
- `block_cookie_banners(bool)` - Auto-dismiss cookie popups
- `block_chat_widgets(bool)` - Block chat widgets
- `block_urls(list)` - Block URLs matching patterns
- `block_resources(list)` - Block resource types: `font`, `media`, `image`, `script`, `stylesheet`

### Page Manipulation
- `inject_script(str)` - Inject JavaScript
- `inject_style(str)` - Inject CSS
- `click(str)` - Click element before capture
- `hide(list)` - Hide elements (visibility: hidden)
- `remove(list)` - Remove elements from DOM

### Browser
- `dark_mode(bool)` - Enable dark mode
- `reduced_motion(bool)` - Enable reduced motion
- `media_type(str)` - Media type: `screen`, `print`
- `user_agent(str)` - Custom user agent
- `timezone(str)` - IANA timezone
- `locale(str)` - BCP 47 locale
- `geolocation(lat, lng, accuracy)` - Spoof geolocation

### Network
- `headers(dict)` - Custom HTTP headers
- `cookies(list)` - Cookies to set
- `auth_basic(username, password)` - HTTP Basic auth
- `auth_bearer(token)` - Bearer token auth
- `bypass_csp(bool)` - Bypass Content Security Policy

### Cache
- `cache_ttl(int)` - Cache TTL in seconds
- `cache_refresh(bool)` - Force cache refresh

### PDF (when format is "pdf")
- `pdf_paper_size(str)` - Paper size: `a4`, `letter`, etc.
- `pdf_width(str)` - Custom width (CSS units)
- `pdf_height(str)` - Custom height
- `pdf_landscape(bool)` - Landscape orientation
- `pdf_margin(str)` - Uniform margin
- `pdf_margin_top/right/bottom/left(str)` - Individual margins
- `pdf_scale(float)` - Scale factor (0.1-2.0)
- `pdf_print_background(bool)` - Include backgrounds
- `pdf_page_ranges(str)` - Page ranges
- `pdf_header(str)` - Header HTML
- `pdf_footer(str)` - Footer HTML
- `pdf_fit_one_page(bool)` - Fit to single page
- `pdf_prefer_css_page_size(bool)` - Use CSS page size

### Storage (BYOS)
- `storage_enabled(bool)` - Enable custom storage
- `storage_path(str)` - Path template
- `storage_acl(str)` - ACL: `public-read`, `private`

## Error Handling

```python
from renderscreenshot import Client, TakeOptions, RenderScreenshotError

client = Client("rs_live_xxxxx")

try:
    image = client.take(TakeOptions.url("https://example.com"))
except RenderScreenshotError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.code}")
    print(f"HTTP Status: {e.http_status}")

    if e.retryable:
        if e.retry_after:
            print(f"Retry after {e.retry_after} seconds")
        # Implement retry logic
```

## Requirements

- Python 3.8+
- httpx

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [Documentation](https://renderscreenshot.com/docs)
- [API Reference](https://renderscreenshot.com/docs/api)
- [GitHub](https://github.com/renderscreenshot/rs-python)
- [PyPI](https://pypi.org/project/renderscreenshot/)
