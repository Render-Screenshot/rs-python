"""Tests that match exactly the documentation examples.

These tests verify that all code examples in the documentation work correctly.
"""

from datetime import datetime, timedelta

from renderscreenshot import Client, TakeOptions


class TestQuickStartDocs:
    """Tests matching quick-start.html.markerb examples."""

    def test_make_first_request(self, httpx_mock):
        """Test the Python example from 'Make your first request' section."""
        httpx_mock.add_response(content=b"screenshot data")

        # From docs: quick-start.html.markerb
        client = Client("rs_live_xxxxx")

        image = client.take(TakeOptions.url("https://example.com").preset("og_card"))

        # with open('screenshot.png', 'wb') as f:
        #     f.write(image)

        assert isinstance(image, bytes)
        assert len(image) > 0
        client.close()


class TestPostScreenshotDocs:
    """Tests matching post-screenshot.html.markerb examples."""

    def test_basic_screenshot(self, httpx_mock):
        """Test the basic screenshot example."""
        httpx_mock.add_response(content=b"screenshot data")

        # From docs: post-screenshot.html.markerb - Basic Screenshot
        client = Client("rs_live_xxxxx")

        image = client.take(TakeOptions.url("https://github.com").preset("og_card"))

        # with open('screenshot.png', 'wb') as f:
        #     f.write(image)

        assert isinstance(image, bytes)
        client.close()

    def test_generate_pdf(self, httpx_mock):
        """Test the PDF generation example."""
        httpx_mock.add_response(content=b"%PDF-1.4 fake pdf data")

        # From docs: post-screenshot.html.markerb - Generate PDF
        client = Client("rs_live_xxxxx")

        pdf = client.take(
            TakeOptions.url("https://example.com/report")
            .format("pdf")
            .pdf_paper_size("a4")
            .pdf_print_background()
            .pdf_margin("2cm")
        )

        # with open('report.pdf', 'wb') as f:
        #     f.write(pdf)

        assert isinstance(pdf, bytes)
        client.close()


class TestBatchDocs:
    """Tests matching batch.html.markerb examples."""

    def test_simple_batch(self, httpx_mock):
        """Test simple batch example."""
        httpx_mock.add_response(
            json={
                "id": "batch_123",
                "status": "completed",
                "total": 3,
                "completed": 2,
                "failed": 1,
                "results": [
                    {
                        "position": 0,
                        "url": "https://github.com",
                        "status": "completed",
                        "image": {
                            "image_url": "https://cdn.example.com/1.png",
                            "width": 1200,
                            "height": 630,
                        },
                        "error": None,
                    },
                    {
                        "position": 1,
                        "url": "https://stripe.com",
                        "status": "completed",
                        "image": {
                            "image_url": "https://cdn.example.com/2.png",
                            "width": 1200,
                            "height": 630,
                        },
                        "error": None,
                    },
                    {
                        "position": 2,
                        "url": "https://linear.app",
                        "status": "failed",
                        "image": None,
                        "error": "Page failed to load within 30 seconds",
                    },
                ],
            }
        )

        # From docs: batch.html.markerb - Simple Batch
        client = Client("rs_live_xxxxx")

        results = client.batch(
            ["https://github.com", "https://stripe.com", "https://linear.app"],
            TakeOptions.url("").preset("og_card"),
        )

        print(f"Completed: {results['completed']}/{results['total']}")
        urls = {}
        for item in results["results"]:
            url = item["image"]["image_url"] if item["status"] == "completed" else "failed"
            print(f"{item['url']}: {url}")
            urls[item["url"]] = url

        assert results["completed"] == 2
        assert urls == {
            "https://github.com": "https://cdn.example.com/1.png",
            "https://stripe.com": "https://cdn.example.com/2.png",
            "https://linear.app": "failed",
        }
        client.close()

    def test_advanced_batch(self, httpx_mock):
        """Test advanced batch with per-URL options."""
        httpx_mock.add_response(
            json={
                "id": "batch_456",
                "status": "completed",
                "total": 3,
                "completed": 3,
                "failed": 0,
                "results": [],
            }
        )

        # From docs: batch.html.markerb - Advanced Batch
        client = Client("rs_live_xxxxx")

        results = client.batch(
            [
                {"url": "https://github.com", "options": {"preset": "og_card"}},
                {"url": "https://stripe.com", "options": {"preset": "full_page"}},
                {"url": "https://linear.app", "options": {"width": 1920, "dark_mode": True}},
            ]
        )

        assert results["total"] == 3
        client.close()


class TestCacheManagementDocs:
    """Tests matching cache-management.html.markerb examples."""

    def test_get_cached_screenshot(self, httpx_mock):
        """Test get cached screenshot example."""
        httpx_mock.add_response(content=b"cached image data")

        # From docs: cache-management.html.markerb - Get Cached Screenshot
        client = Client("rs_live_xxxxx")

        image = client.cache.get("cache_xyz789")
        if image:
            # with open('screenshot.png', 'wb') as f:
            #     f.write(image)
            pass

        assert image is not None
        assert isinstance(image, bytes)
        client.close()

    def test_delete_cache_entry(self, httpx_mock):
        """Test delete cache entry example."""
        httpx_mock.add_response(json={"deleted": True, "key": "cache_xyz789"})

        # From docs: cache-management.html.markerb - Delete Cache Entry
        client = Client("rs_live_xxxxx")

        deleted = client.cache.delete("cache_xyz789")
        print("Deleted" if deleted else "Not found")

        assert deleted is True
        client.close()

    def test_purge_by_keys(self, httpx_mock):
        """Test purge by keys example."""
        httpx_mock.add_response(json={"purged": 2, "keys": ["cache_abc123", "cache_def456"]})

        # From docs: cache-management.html.markerb - Purge by Keys
        client = Client("rs_live_xxxxx")

        result = client.cache.purge(["cache_abc123", "cache_def456"])
        print(f"Purged {result['purged']} entries")

        assert result["purged"] == 2
        client.close()

    def test_purge_by_url_pattern(self, httpx_mock):
        """Test purge by URL pattern example."""
        httpx_mock.add_response(json={"purged": 10, "url": "https://mysite.com/blog/*"})

        # From docs: cache-management.html.markerb - Purge by URL Pattern
        client = Client("rs_live_xxxxx")

        result = client.cache.purge_url("https://mysite.com/blog/*")
        print(f"Purged {result['purged']} entries")

        assert result["purged"] == 10
        client.close()

    def test_purge_by_date(self, httpx_mock):
        """Test purge by date example."""
        httpx_mock.add_response(json={"purged": 42, "before": "2024-01-01T00:00:00Z"})

        # From docs: cache-management.html.markerb - Purge by Date
        client = Client("rs_live_xxxxx")

        result = client.cache.purge_before(datetime(2024, 1, 1))
        print(f"Purged {result['purged']} entries")

        assert result["purged"] == 42
        client.close()


class TestBlockingDocs:
    """Tests matching blocking.html.markerb examples."""

    def test_clean_ecommerce_screenshot(self, httpx_mock):
        """Test clean e-commerce screenshot example."""
        httpx_mock.add_response(content=b"product image data")

        # From docs: blocking.html.markerb - Clean E-commerce Screenshot
        client = Client("rs_live_xxxxx")

        image = client.take(
            TakeOptions.url("https://store.example.com/product")
            .block_ads()
            .block_cookie_banners()
            .block_chat_widgets()
        )

        assert isinstance(image, bytes)
        client.close()

    def test_documentation_screenshot(self, httpx_mock):
        """Test documentation screenshot example."""
        httpx_mock.add_response(content=b"docs image data")

        # From docs: blocking.html.markerb - Documentation Screenshot
        client = Client("rs_live_xxxxx")

        image = client.take(
            TakeOptions.url("https://docs.example.com").block_urls(
                ["*feedback-widget*", "*announcement-banner*"]
            )
        )

        assert isinstance(image, bytes)
        client.close()


class TestSignedUrlsDocs:
    """Tests matching signed-urls.html.markerb examples."""

    def test_generate_signed_url_with_sdk(self):
        """Test signed URL generation with SDK example."""
        # From docs: signed-urls.html.markerb - Python (with SDK)
        client = Client("rs_live_xxxxx")

        # Generate a signed URL that expires in 24 hours
        signed_url = client.generate_url(
            TakeOptions.url("https://example.com").preset("og_card"),
            datetime.now() + timedelta(hours=24),
        )

        # Use in HTML: <img src="{signed_url}" />
        # Or in meta tags: <meta property="og:image" content="{signed_url}" />

        assert "https://api.renderscreenshot.com" in signed_url
        assert "signature=" in signed_url
        assert "expires=" in signed_url
        client.close()


class TestSdkIndexDocs:
    """Tests matching sdks/index.html.markerb quick example."""

    def test_quick_example(self, httpx_mock):
        """Test the quick example from SDK index page."""
        httpx_mock.add_response(content=b"screenshot data")

        # From docs: sdks/index.html.markerb - Quick Example - Python
        client = Client("rs_live_xxxxx")

        # Take a screenshot with chained options
        image = client.take(
            TakeOptions.url("https://example.com").preset("og_card").block_ads().dark_mode()
        )

        assert isinstance(image, bytes)
        client.close()


class TestPythonSdkDocs:
    """Tests matching sdks/python.html.markerb examples."""

    def test_quick_start(self, httpx_mock):
        """Test quick start example."""
        httpx_mock.add_response(content=b"screenshot data")

        # From docs: sdks/python.html.markerb - Quick Start
        client = Client("rs_live_xxxxx")

        # Take a screenshot
        image = client.take(TakeOptions.url("https://example.com").preset("og_card"))

        # Save to file
        # with open('screenshot.png', 'wb') as f:
        #     f.write(image)

        assert isinstance(image, bytes)
        client.close()

    def test_take_json(self, httpx_mock):
        """Test take_json example."""
        httpx_mock.add_response(
            json={
                "url": "https://cdn.example.com/screenshot.png",
                "width": 1200,
                "height": 630,
                "cached": False,
            }
        )

        # From docs: sdks/python.html.markerb - take_json
        client = Client("rs_live_xxxxx")

        response = client.take_json(TakeOptions.url("https://example.com").preset("og_card"))

        print(response["url"])  # CDN URL
        print(response["width"])  # 1200
        print(response["height"])  # 630
        print(response["cached"])  # True/False

        assert response["width"] == 1200
        client.close()

    def test_context_manager(self, httpx_mock):
        """Test context manager example."""
        httpx_mock.add_response(content=b"screenshot data")

        # From docs: sdks/python.html.markerb - Context Manager
        with Client("rs_live_xxxxx") as client:
            image = client.take(TakeOptions.url("https://example.com"))

        assert isinstance(image, bytes)

    def test_cache_management(self, httpx_mock):
        """Test cache management examples."""
        httpx_mock.add_response(content=b"cached data")

        # From docs: sdks/python.html.markerb - Cache Management
        client = Client("rs_live_xxxxx")

        # Get cached screenshot
        image = client.cache.get("cache_xyz789")

        assert image is not None
        client.close()

    def test_presets_and_devices(self, httpx_mock):
        """Test presets and devices examples."""
        httpx_mock.add_response(
            json=[
                {"id": "og_card", "name": "OG Card", "width": 1200, "height": 630},
            ]
        )

        # From docs: sdks/python.html.markerb - presets()/preset(id)
        client = Client("rs_live_xxxxx")

        presets = client.presets()

        assert len(presets) > 0
        client.close()
