"""
GitHub service layer that coordinates API access with cross-cutting concerns.

Provides business logic operations with rate limiting, caching, and retry logic.
Maintains clean separation from the ultra-thin boundary layer.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from .protocols import RepositoryService
from .boundary import GitHubApiBoundary
from .rate_limiter import RateLimitHandler
from .cache import setup_global_cache, clear_cache, CacheConfig

logger = logging.getLogger(__name__)


class GitHubService(RepositoryService):
    """
    Service layer for GitHub API operations.

    Coordinates boundary layer API access with cross-cutting concerns
    like rate limiting, caching, and retry logic.
    """

    def __init__(
        self,
        boundary: GitHubApiBoundary,
        rate_limiter: Optional[RateLimitHandler] = None,
        caching_enabled: bool = True,
    ):
        """
        Initialize GitHub service with dependencies.

        Args:
            boundary: Ultra-thin API boundary layer
            rate_limiter: Optional rate limiting handler
            caching_enabled: Whether caching is enabled globally
        """
        self._boundary = boundary
        self._rate_limiter = rate_limiter or RateLimitHandler()
        self._caching_enabled = caching_enabled

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

    def get_repository_pull_requests(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull requests from repository with rate limiting and caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"pull_requests:{repo_name}",
            operation=lambda: self._boundary.get_repository_pull_requests(repo_name),
        )

    def get_pull_request_comments(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request with rate limiting and caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"pr_comments:{repo_name}:{pr_number}",
            operation=lambda: self._boundary.get_pull_request_comments(
                repo_name, pr_number
            ),
        )

    def get_all_pull_request_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull request comments with rate limiting and caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"all_pr_comments:{repo_name}",
            operation=lambda: self._boundary.get_all_pull_request_comments(repo_name),
        )

    def get_pull_request_reviews(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get reviews for specific pull request with rate limiting and caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"pr_reviews:{repo_name}:{pr_number}",
            operation=lambda: self._boundary.get_pull_request_reviews(
                repo_name, pr_number
            ),
        )

    def get_all_pull_request_reviews(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull request reviews with rate limiting and caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"all_pr_reviews:{repo_name}",
            operation=lambda: self._boundary.get_all_pull_request_reviews(repo_name),
        )

    def get_pull_request_review_comments(
        self, repo_name: str, review_id: str
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request review with rate limiting."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"pr_review_comments:{repo_name}:{review_id}",
            operation=lambda: self._boundary.get_pull_request_review_comments(
                repo_name, review_id
            ),
        )

    def get_all_pull_request_review_comments(
        self, repo_name: str
    ) -> List[Dict[str, Any]]:
        """Get all pull request review comments with rate limiting and caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"all_pr_review_comments:{repo_name}",
            operation=lambda: self._boundary.get_all_pull_request_review_comments(
                repo_name
            ),
        )

    def get_repository_sub_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get sub-issue relationships from repository with caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"sub_issues:{repo_name}",
            operation=lambda: self._boundary.get_repository_sub_issues(repo_name),
        )

    def get_repository_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get milestones via GraphQL with caching and rate limiting."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"milestones:{repo_name}",
            operation=lambda: self._boundary.get_repository_milestones(repo_name),
        )

    def get_repository_releases(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get releases via REST API with caching and rate limiting."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"releases:{repo_name}",
            operation=lambda: self._boundary.get_repository_releases(repo_name),
        )

    def get_issue_sub_issues(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get sub-issues for specific issue with rate limiting and caching."""
        return self._execute_with_cross_cutting_concerns(
            cache_key=f"issue_sub_issues:{repo_name}:{issue_number}",
            operation=lambda: self._boundary.get_issue_sub_issues_graphql(
                repo_name, issue_number
            ),
        )

    def get_issue_parent(
        self, repo_name: str, issue_number: int
    ) -> Optional[Dict[str, Any]]:
        """Get parent issue if this issue is a sub-issue with caching."""
        # Note: This method returns a single item, not a list like other methods
        return self._rate_limiter.execute_with_retry(
            lambda: self._boundary.get_issue_parent(repo_name, issue_number),
            self._boundary._github,
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
        self,
        repo_name: str,
        title: str,
        body: str,
        labels: List[str],
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new issue with rate limiting."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.create_issue(
                repo_name, title, body, labels, milestone=milestone
            ),
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

    def create_pull_request(
        self,
        repo_name: str,
        title: str,
        body: str,
        head: str,
        base: str,
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new pull request with rate limiting."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.create_pull_request(
                repo_name, title, body, head, base, milestone=milestone
            ),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "pull_requests")
        return result

    def create_pull_request_comment(
        self, repo_name: str, pr_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new PR comment with rate limiting."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.create_pull_request_comment(
                repo_name, pr_number, body
            ),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "pr_comments")
        return result

    def add_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> Dict[str, Any]:
        """Add existing issue as sub-issue with rate limiting."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.add_sub_issue(
                repo_name, parent_issue_number, sub_issue_number
            ),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "sub_issues")
        return result

    def remove_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> None:
        """Remove sub-issue relationship with rate limiting."""
        self._rate_limiter.execute_with_retry(
            lambda: self._boundary.remove_sub_issue(
                repo_name, parent_issue_number, sub_issue_number
            ),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "sub_issues")

    def reprioritize_sub_issue(
        self,
        repo_name: str,
        parent_issue_number: int,
        sub_issue_number: int,
        position: int,
    ) -> Dict[str, Any]:
        """Change sub-issue order/position with rate limiting."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.reprioritize_sub_issue(
                repo_name, parent_issue_number, sub_issue_number, position
            ),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "sub_issues")
        return result

    # Cross-cutting Concern Coordination

    def _execute_with_cross_cutting_concerns(
        self, cache_key: str, operation: Callable[[], List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Execute operation with rate limiting and caching."""
        # With global caching, requests are automatically cached
        # We just need to execute with rate limiting
        return self._rate_limiter.execute_with_retry(operation, self._boundary._github)

    def _invalidate_cache_for_repository(self, repo_name: str, data_type: str) -> None:
        """Invalidate cached data for repository after modifications."""
        if self._caching_enabled:
            # For now, we'll clear all cache
            # In the future, we can implement more granular invalidation
            logger.info(f"Clearing cache after {data_type} modification in {repo_name}")
            clear_cache()

    def create_pull_request_review(
        self, repo_name: str, pr_number: int, body: str, state: str
    ) -> Dict[str, Any]:
        """Create a new pull request review with rate limiting."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.create_pull_request_review(
                repo_name, pr_number, body, state
            ),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "pr_reviews")
        return result

    def create_pull_request_review_comment(
        self, repo_name: str, review_id: str, body: str
    ) -> Dict[str, Any]:
        """Create a new pull request review comment with rate limiting."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.create_pull_request_review_comment(
                repo_name, review_id, body
            ),
            self._boundary._github,
        )
        self._invalidate_cache_for_repository(repo_name, "pr_review_comments")
        return result

    def create_milestone(
        self,
        repo_name: str,
        title: str,
        description: Optional[str] = None,
        due_on: Optional[str] = None,
        state: str = "open",
    ) -> Dict[str, Any]:
        """Create milestone via REST API with cache invalidation."""
        result = self._rate_limiter.execute_with_retry(
            lambda: self._boundary.create_milestone(
                repo_name, title, description, due_on, state
            ),
            self._boundary._github,
        )

        # Invalidate relevant caches
        self._invalidate_cache_for_repository(repo_name, "milestones")

        return result

    def create_release(
        self,
        repo_name: str,
        tag_name: str,
        target_commitish: str,
        name: Optional[str] = None,
        body: Optional[str] = None,
        draft: bool = False,
        prerelease: bool = False,
    ) -> Dict[str, Any]:
        """Create release via REST API with rate limiting."""
        return self._rate_limiter.execute_with_retry(
            lambda: self._boundary.create_release(
                repo_name=repo_name,
                tag_name=tag_name,
                target_commitish=target_commitish,
                name=name,
                body=body,
                draft=draft,
                prerelease=prerelease,
            ),
            self._boundary._github,
        )


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

    if enable_caching:
        config = cache_config or CacheConfig()
        setup_global_cache(config)

    return GitHubService(boundary, rate_limiter, enable_caching)
