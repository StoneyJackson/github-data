"""
Global caching setup for GitHub API responses.

Provides ETag-based conditional requests and response caching
to reduce redundant API calls and improve performance.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

import requests_cache

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for GitHub API caching."""

    cache_name: str = "github_api_cache"
    expire_after: int = 3600  # 1 hour default
    backend: str = "sqlite"  # sqlite, redis, memory, etc.
    allowable_codes: List[int] = field(default_factory=lambda: [200, 404])
    stale_if_error: bool = True


def setup_global_cache(config: Optional[CacheConfig] = None) -> None:
    """
    Install global caching for all HTTP requests.

    Args:
        config: Optional cache configuration, uses defaults if None
    """
    if config is None:
        config = CacheConfig()

    requests_cache.install_cache(
        cache_name=config.cache_name,
        expire_after=config.expire_after,
        backend=config.backend,
        allowable_codes=config.allowable_codes,
        stale_if_error=config.stale_if_error,
    )
    logger.info(f"Global cache installed: {config.cache_name}")


def clear_cache() -> None:
    """Clear all cached data."""
    requests_cache.clear()


def get_cache_info() -> Dict[str, Any]:
    """Get information about cache state."""
    if requests_cache.is_installed():
        # Get the current cache backend
        try:
            cache = requests_cache.get_cache()
            if cache is not None:
                return {
                    "backend": str(type(cache)),
                    "size": len(cache) if hasattr(cache, "__len__") else "unknown",
                    "installed": True,
                }
            else:
                return {"backend": "unknown", "size": "unknown", "installed": True}
        except Exception:
            return {"backend": "unknown", "size": "unknown", "installed": True}
    return {"backend": "none", "size": 0, "installed": False}
