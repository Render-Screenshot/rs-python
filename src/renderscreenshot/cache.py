"""Cache management for the RenderScreenshot SDK."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol

from .types import PurgeResult

if TYPE_CHECKING:
    pass


class ClientProtocol(Protocol):
    """Protocol for the Client interface to avoid circular imports."""

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        response_type: str = "json",
    ) -> Any: ...


class CacheManager:
    """Cache management methods for RenderScreenshot.

    This class provides methods to retrieve, delete, and purge cached screenshots.
    Access it via the `cache` attribute on the Client instance.

    Example:
        >>> client = Client("rs_live_xxxxx")
        >>> # Get a cached screenshot
        >>> image = client.cache.get("cache_xyz789")
        >>> # Delete a cache entry
        >>> deleted = client.cache.delete("cache_xyz789")
        >>> # Bulk purge
        >>> result = client.cache.purge(["cache_abc", "cache_def"])
    """

    def __init__(self, client: ClientProtocol) -> None:
        """Create a new CacheManager.

        Args:
            client: The parent Client instance.
        """
        self._client = client

    def get(self, key: str) -> Optional[bytes]:
        """Get a cached screenshot by its cache key.

        Args:
            key: The cache key returned in X-Cache-Key header or response.

        Returns:
            Bytes containing the screenshot, or None if not found.

        Example:
            >>> image = client.cache.get("cache_xyz789")
            >>> if image:
            ...     with open("cached.png", "wb") as f:
            ...         f.write(image)
        """
        try:
            return self._client._request("GET", f"/cache/{key}", response_type="buffer")
        except Exception as e:
            # Return None for 404 errors
            if hasattr(e, "http_status") and e.http_status == 404:  # type: ignore
                return None
            raise

    def delete(self, key: str) -> bool:
        """Delete a single cache entry.

        Args:
            key: The cache key to delete.

        Returns:
            True if deleted, False if not found.

        Example:
            >>> deleted = client.cache.delete("cache_xyz789")
            >>> print(f"Deleted: {deleted}")
        """
        response: Dict[str, bool] = self._client._request("DELETE", f"/cache/{key}")
        return response.get("deleted", False)

    def purge(self, keys: List[str]) -> PurgeResult:
        """Bulk purge cache entries by keys.

        Args:
            keys: List of cache keys to purge.

        Returns:
            Purge result with count and keys.

        Example:
            >>> result = client.cache.purge(["cache_abc", "cache_def"])
            >>> print(f"Purged {result['purged']} entries")
        """
        return self._client._request("POST", "/cache/purge", body={"keys": keys})

    def purge_url(self, pattern: str) -> PurgeResult:
        """Purge cache entries matching a URL pattern.

        Args:
            pattern: Glob pattern to match source URLs.

        Returns:
            Purge result with count.

        Example:
            >>> result = client.cache.purge_url("https://mysite.com/blog/*")
            >>> print(f"Purged {result['purged']} entries")
        """
        return self._client._request("POST", "/cache/purge", body={"url": pattern})

    def purge_before(self, date: datetime) -> PurgeResult:
        """Purge cache entries created before a specific date.

        Args:
            date: Purge entries created before this date.

        Returns:
            Purge result with count.

        Example:
            >>> from datetime import datetime
            >>> result = client.cache.purge_before(datetime(2024, 1, 1))
            >>> print(f"Purged {result['purged']} entries")
        """
        return self._client._request("POST", "/cache/purge", body={"before": date.isoformat()})

    def purge_pattern(self, pattern: str) -> PurgeResult:
        """Purge cache entries matching a storage path pattern.

        Args:
            pattern: Glob pattern for storage paths.

        Returns:
            Purge result with count.

        Example:
            >>> result = client.cache.purge_pattern("screenshots/2024/*")
            >>> print(f"Purged {result['purged']} entries")
        """
        return self._client._request("POST", "/cache/purge", body={"pattern": pattern})
