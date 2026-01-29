# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
