"""Tests for quick start documentation examples."""

from renderscreenshot import Client, TakeOptions


class TestQuickStartExamples:
    """Tests mirroring quick start documentation."""

    def test_basic_screenshot(self, httpx_mock):
        """Test basic screenshot example from docs."""
        httpx_mock.add_response(content=b"image data")

        # Example: Basic screenshot
        client = Client("rs_live_xxxxx")
        options = TakeOptions.url("https://example.com")
        image = client.take(options)

        assert isinstance(image, bytes)
        assert len(image) > 0
        client.close()

    def test_screenshot_with_options(self, httpx_mock):
        """Test screenshot with options example from docs."""
        httpx_mock.add_response(content=b"image data")

        # Example: Screenshot with options
        client = Client("rs_live_xxxxx")
        options = (
            TakeOptions.url("https://example.com").width(1200).height(630).format("png").block_ads()
        )
        image = client.take(options)

        assert isinstance(image, bytes)
        client.close()

    def test_og_card_preset(self, httpx_mock):
        """Test OG card preset example from docs."""
        httpx_mock.add_response(content=b"image data")

        # Example: Using preset
        client = Client("rs_live_xxxxx")
        options = TakeOptions.url("https://example.com").preset("og_card")
        image = client.take(options)

        assert isinstance(image, bytes)
        client.close()

    def test_json_response(self, httpx_mock):
        """Test JSON response example from docs."""
        httpx_mock.add_response(
            json={
                "url": "https://cdn.renderscreenshot.com/abc.png",
                "width": 1200,
                "height": 630,
                "format": "png",
                "size": 12345,
                "cached": False,
            }
        )

        # Example: Get JSON response with metadata
        client = Client("rs_live_xxxxx")
        options = TakeOptions.url("https://example.com").preset("og_card")
        response = client.take_json(options)

        assert "url" in response
        assert response["width"] == 1200
        assert response["height"] == 630
        client.close()

    def test_client_context_manager(self, httpx_mock):
        """Test client as context manager example from docs."""
        httpx_mock.add_response(content=b"image data")

        # Example: Using context manager
        with Client("rs_live_xxxxx") as client:
            options = TakeOptions.url("https://example.com")
            image = client.take(options)
            assert isinstance(image, bytes)
