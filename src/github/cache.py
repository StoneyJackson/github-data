"""
Caching service for GitHub API responses.

Provides ETag-based conditional requests and response caching
to reduce redundant API calls and improve performance.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, TypeVar

import requests_cache

T = TypeVar("T")

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for GitHub API caching."""

    cache_name: str = "github_api_cache"
    expire_after: int = 3600  # 1 hour default
    backend: str = "sqlite"  # sqlite, redis, memory, etc.
    allowable_codes: List[int] = field(default_factory=lambda: [200, 404])
    stale_if_error: bool = True


class CacheService:
    """
    Service for caching GitHub API responses with ETag support.

    Uses requests-cache to provide automatic ETag handling,
    conditional requests, and response caching.
    """

    def __init__(self, config: CacheConfig):
        """
        Initialize cache service with configuration.

        Args:
            config: Cache configuration settings
        """
        self._config = config
        self._session = self._create_cached_session()

    def get_or_fetch(self, key: str, fetch_fn: Callable[[], T]) -> T:
        """
        Get data from cache or fetch from API if not cached.

        Args:
            key: Cache key for the data
            fetch_fn: Function to fetch data if not in cache

        Returns:
            Cached or freshly fetched data
        """
        # For now, we'll implement a simple wrapper
        # In the future, we can enhance this with more sophisticated
        # ETag handling specific to GitHub API responses
        try:
            return fetch_fn()
        except Exception as e:
            logger.error(f"Failed to fetch data for key {key}: {e}")
            raise

    def clear_cache(self) -> None:
        """Clear all cached data."""
        if hasattr(self._session, "cache"):
            self._session.cache.clear()

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cache state."""
        if hasattr(self._session, "cache"):
            cache = self._session.cache
            return {
                "backend": str(type(cache)),
                "size": len(cache) if hasattr(cache, "__len__") else "unknown",
            }
        return {"backend": "none", "size": 0}

    def _create_cached_session(self) -> requests_cache.CachedSession:
        """Create a cached session with configuration."""
        return requests_cache.CachedSession(
            cache_name=self._config.cache_name,
            expire_after=self._config.expire_after,
            backend=self._config.backend,
            allowable_codes=self._config.allowable_codes,
            stale_if_error=self._config.stale_if_error,
        )
