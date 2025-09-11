"""
GitHub service layer that coordinates API access with cross-cutting concerns.

Provides business logic operations with rate limiting, caching, and retry logic.
Maintains clean separation from the ultra-thin boundary layer.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from .boundary import GitHubApiBoundary
from .rate_limiter import RateLimitHandler
from .cache import CacheService, CacheConfig

logger = logging.getLogger(__name__)


class GitHubService:
    """
    Service layer for GitHub API operations.

    Coordinates boundary layer API access with cross-cutting concerns
    like rate limiting, caching, and retry logic.
    """

    def __init__(
        self,
        boundary: GitHubApiBoundary,
        rate_limiter: Optional[RateLimitHandler] = None,
        cache_service: Optional[CacheService] = None,
    ):
        """
        Initialize GitHub service with dependencies.

        Args:
            boundary: Ultra-thin API boundary layer
            rate_limiter: Optional rate limiting handler
            cache_service: Optional caching service
        """
        self._boundary = boundary
        self._rate_limiter = rate_limiter or RateLimitHandler()
        self._cache_service = cache_service

    # Public API - Repository Data Operations

    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all labels from repository with rate limiting and caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"labels:{repo_name}",
            operation=lambda: self._boundary.get_repository_labels(repo_name),
        )

    def get_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issues from repository with rate limiting and caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"issues:{repo_name}",
            operation=lambda: self._boundary.get_repository_issues(repo_name),
        )

    def get_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific issue with rate limiting and caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"comments:{repo_name}:{issue_number}",
            operation=lambda: self._boundary.get_issue_comments(
                repo_name, issue_number
            ),
        )

    def get_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issue comments with rate limiting and caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"all_comments:{repo_name}",
            operation=lambda: self._boundary.get_all_issue_comments(repo_name),
        )

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        # Rate limit status should not be cached
        return self._rate_limiter.execute_with_retry(
            lambda: self._boundary.get_rate_limit_status(), self._boundary._github
        )

    # Public API - Repository Modification Operations

    def create_label(
        self, repo_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Create a new label with rate limiting."""
        # Modifications should not be cached and should clear related caches
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.create_label(repo_name, name, color, description),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "labels")
        return result

    def delete_label(self, repo_name: str, label_name: str) -> None:
        """Delete a label with rate limiting."""
        self._rate_limiter.execute_with_retry(
            lambda: self._boundary.delete_label(repo_name, label_name),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "labels")

    def update_label(
        self, repo_name: str, old_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Update an existing label with rate limiting."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.update_label(
                repo_name, old_name, name, color, description
            ),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "labels")
        return result

    def create_issue(
        self, repo_name: str, title: str, body: str, labels: List[str]
    ) -> Dict[str, Any]:
        """Create a new issue with rate limiting."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.create_issue(repo_name, title, body, labels),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "issues")
        return result

    def create_issue_comment(
        self, repo_name: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment with rate limiting."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.create_issue_comment(repo_name, issue_number, body),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "comments")
        return result

    def close_issue(
        self, repo_name: str, issue_number: int, state_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close an issue with rate limiting."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.close_issue(repo_name, issue_number, state_reason),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "issues")
        return result

    # Cross-cutting Concern Coordination

    def _execute_with_cross_cutting_concerns(
        self, cache_key: str, operation: Callable[[], List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Execute operation with rate limiting and caching."""
        if self._cache_service:
            return self._cache_service.get_or_fetch(
                key=cache_key,
                fetch_fn=lambda: self._rate_limiter.execute_with_retry(
                    operation, self._boundary._github
                ),
            )
        else:
            return self._rate_limiter.execute_with_retry(
                operation, self._boundary._github
            )

    def _invalidate_cache_for_repository(self, repo_name: str, data_type: str) -> None:
        """Invalidate cached data for repository after modifications."""
        if self._cache_service:
            # For now, we'll clear all cache
            # In the future, we can implement more granular invalidation
            logger.info(f"Clearing cache after {data_type} modification in {repo_name}")
            self._cache_service.clear_cache()


def create_github_service(
    token: str,
    enable_rate_limiting: bool = True,
    enable_caching: bool = True,
    cache_config: Optional[CacheConfig] = None,
) -> GitHubService:
    """
    Factory function to create a configured GitHub service.

    Args:
        token: GitHub authentication token
        enable_rate_limiting: Whether to enable rate limiting
        enable_caching: Whether to enable caching
        cache_config: Optional cache configuration

    Returns:
        Configured GitHubService instance
    """
    boundary = GitHubApiBoundary(token)

    rate_limiter = RateLimitHandler() if enable_rate_limiting else None

    cache_service = None
    if enable_caching:
        config = cache_config or CacheConfig()
        cache_service = CacheService(config)

    return GitHubService(boundary, rate_limiter, cache_service)
