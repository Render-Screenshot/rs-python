"""Tests for batch processing documentation examples."""

from renderscreenshot import Client, TakeOptions


class TestBatchExamples:
    """Tests mirroring batch processing documentation."""

    def test_simple_batch(self, httpx_mock):
        """Test simple batch example from docs."""
        httpx_mock.add_response(
            json={
                "id": "batch_123",
                "status": "completed",
                "total": 3,
                "completed": 3,
                "failed": 0,
                "results": [
                    {"url": "https://example1.com", "success": True},
                    {"url": "https://example2.com", "success": True},
                    {"url": "https://example3.com", "success": True},
                ],
            }
        )

        # Example: Simple batch with shared options
        client = Client("rs_live_xxxxx")
        urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com",
        ]
        options = TakeOptions.url("").preset("og_card")

        results = client.batch(urls, options)

        assert results["status"] == "completed"
        assert results["total"] == 3
        assert results["completed"] == 3
        client.close()

    def test_batch_with_per_url_options(self, httpx_mock):
        """Test batch with per-URL options example from docs."""
        httpx_mock.add_response(
            json={
                "id": "batch_456",
                "status": "completed",
                "total": 2,
                "completed": 2,
                "failed": 0,
                "results": [],
            }
        )

        # Example: Batch with per-URL options
        client = Client("rs_live_xxxxx")
        requests = [
            {"url": "https://example1.com", "options": {"width": 1200}},
            {"url": "https://example2.com", "options": {"preset": "full_page"}},
        ]

        results = client.batch(requests)

        assert results["status"] == "completed"
        client.close()

    def test_get_batch_status(self, httpx_mock):
        """Test getting batch status example from docs."""
        httpx_mock.add_response(
            json={
                "id": "batch_789",
                "status": "processing",
                "total": 10,
                "completed": 5,
                "failed": 0,
                "results": [],
            }
        )

        # Example: Get batch status
        client = Client("rs_live_xxxxx")
        response = client.get_batch("batch_789")

        assert response["status"] == "processing"
        assert response["completed"] == 5
        client.close()
