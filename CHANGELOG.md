# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-10-18

### Added

- `cache_available()` option. It sends `cache.available: true` in POST bodies and
  `cache_available=true` in GET / signed URLs, so the API can reuse an identical cached
  render inside the cache TTL. Without it every request renders a fresh screenshot.

## [1.0.1] - 2026-10-18

### Fixed

- `take()`, `take_json()` and `batch()` now send the nested JSON body that the API expects
  (`viewport.width`, `capture.mode`, `capture.selector`, `output.format`, `wait.until`,
  `wait.for_selector`, `block.*`, `page.*`, `browser.*`, `network.*`, `cache.*`, `pdf.*`,
  `storage.*`). Before this fix, most options were sent as flat keys and the API ignored them.
- `take_json()` now sends `Accept: application/json`, so the API returns JSON metadata
  instead of image bytes.
- `generate_url()` now produces URLs that the API accepts: it adds `key_id` (`rs_pub_...`)
  and `expires`, uses the GET endpoint parameter names, encodes values like Rails `to_query`,
  and signs with the `rs_secret_...` signing key instead of the live API key.
- `ScreenshotResponse` (the `take_json()` return type) now matches the real API response:
  `id`, `status`, `image` (`url`, `width`, `height`, `size`, `format`), `metadata`,
  `cache` (`hit`, `key`, `url`, `expires_at`) and `usage` (`credits`, `remaining`).
  The old flat keys (`url`, `width`, `height`, `cached`, ...) were never in the response.
- `parse_webhook()` now takes the error code of a `screenshot.failed` event from
  `data.error_code` (it was always `render_failed`), and keeps `summary` and `results_url`
  for batch events.
- `TakeOptions.to_query_string()` now uses the parameter names that `GET /v1/screenshot` reads
  (for example `selector`, `block_cookies`, `timeout`, `pdf_paper`).

### Added

- `Client(..., signing_key=..., public_key_id=...)` and per-call `signing_key` /
  `public_key_id` overrides on `generate_url()`. `generate_url()` raises
  `RenderScreenshotError` (`invalid_request`) when either value is missing.
- `generate_url()` accepts a Unix timestamp (`int`) as well as a `datetime`.
- `TakeOptions.to_flat_params()` returns the flat GET query parameters as a dict.
- New types `ScreenshotImage`, `ScreenshotMetadata`, `ScreenshotCache`, `ScreenshotUsage`,
  `WebhookScreenshot` and `WebhookBatchSummary`. Webhook event data also carries the original
  `data` object as `raw`.

### Changed

- `pdf_paper_size()` is sent as `pdf.paper` (the API field name).
- Docstrings now say that only live keys (`rs_live_...`) authenticate API requests.

## [1.0.0] - 2025-01-28

### Added

- Initial release of the RenderScreenshot Python SDK
- `Client` class for API interactions
- `TakeOptions` fluent builder with 60+ configuration methods
- Screenshot capture methods: `take()` and `take_json()`
- Signed URL generation with `generate_url()`
- Batch processing with `batch()` and `get_batch()`
- Cache management: `cache.get()`, `cache.delete()`, `cache.purge()`, etc.
- Webhook verification with `verify_webhook()` and `parse_webhook()`
- Preset and device listing with `presets()` and `devices()`
- Full type hints for IDE support
- Comprehensive test suite
- GitHub Actions CI pipeline
