"""
GitHub service layer that coordinates API access with cross-cutting concerns.

Provides business logic operations with rate limiting, caching, and retry logic.
Maintains clean separation from the ultra-thin boundary layer.
"""

import logging
from typing import Dict, List, Any, Optional, Callable, cast
from .protocols import RepositoryService
from .boundary import GitHubApiBoundary
from github_data_core.github.rate_limiter import RateLimitHandler
from github_data_core.github.cache import setup_global_cache, clear_cache, CacheConfig
from .operation_registry import GitHubOperationRegistry, Operation

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

        # Initialize operation registry
        self._operation_registry = GitHubOperationRegistry()

        logger.info(
            f"GitHubService initialized with "
            f"{len(self._operation_registry.list_operations())} registered operations"
        )

    # Public API - Repository Data Operations

    def get_repository_metadata(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """Get repository metadata with rate limiting.

        Args:
            repo_name: Repository name in format "owner/repo"

        Returns:
            Dictionary containing repository metadata, or None if not found
        """
        from github import UnknownObjectException

        try:
            return cast(
                Dict[str, Any],
                self._execute_with_cross_cutting_concerns(
                    cache_key=None,  # Don't cache metadata checks
                    operation=lambda: self._boundary.get_repository_metadata(repo_name),
                ),
            )
        except UnknownObjectException as e:
            # Repository doesn't exist
            logger.debug(f"Repository {repo_name} not found: {e}")
            return None

    # NOTE: create_repository method moved to github-repo-manager package
    # for focused repository lifecycle management

    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all labels from repository with rate limiting and caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"labels:{repo_name}",
                operation=lambda: self._boundary.get_repository_labels(repo_name),
            ),
        )

    def get_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issues from repository with rate limiting and caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"issues:{repo_name}",
                operation=lambda: self._boundary.get_repository_issues(repo_name),
            ),
        )

    def get_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific issue with rate limiting and caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"comments:{repo_name}:{issue_number}",
                operation=lambda: self._boundary.get_issue_comments(
                    repo_name, issue_number
                ),
            ),
        )

    def get_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issue comments with rate limiting and caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"all_comments:{repo_name}",
                operation=lambda: self._boundary.get_all_issue_comments(repo_name),
            ),
        )

    def get_repository_pull_requests(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull requests from repository with rate limiting and caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"pull_requests:{repo_name}",
                operation=lambda: self._boundary.get_repository_pull_requests(
                    repo_name
                ),
            ),
        )

    def get_pull_request_comments(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request with rate limiting and caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"pr_comments:{repo_name}:{pr_number}",
                operation=lambda: self._boundary.get_pull_request_comments(
                    repo_name, pr_number
                ),
            ),
        )

    def get_all_pull_request_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull request comments with rate limiting and caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"all_pr_comments:{repo_name}",
                operation=lambda: self._boundary.get_all_pull_request_comments(
                    repo_name
                ),
            ),
        )

    def get_pull_request_reviews(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get reviews for specific pull request with rate limiting and caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"pr_reviews:{repo_name}:{pr_number}",
                operation=lambda: self._boundary.get_pull_request_reviews(
                    repo_name, pr_number
                ),
            ),
        )

    def get_all_pull_request_reviews(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull request reviews with rate limiting and caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"all_pr_reviews:{repo_name}",
                operation=lambda: self._boundary.get_all_pull_request_reviews(
                    repo_name
                ),
            ),
        )

    def get_pull_request_review_comments(
        self, repo_name: str, review_id: str
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request review with rate limiting."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"pr_review_comments:{repo_name}:{review_id}",
                operation=lambda: self._boundary.get_pull_request_review_comments(
                    repo_name, review_id
                ),
            ),
        )

    def get_all_pull_request_review_comments(
        self, repo_name: str
    ) -> List[Dict[str, Any]]:
        """Get all pull request review comments with rate limiting and caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"all_pr_review_comments:{repo_name}",
                operation=lambda: self._boundary.get_all_pull_request_review_comments(
                    repo_name
                ),
            ),
        )

    def get_repository_sub_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get sub-issue relationships from repository with caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"sub_issues:{repo_name}",
                operation=lambda: self._boundary.get_repository_sub_issues(repo_name),
            ),
        )

    def get_repository_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get milestones via GraphQL with caching and rate limiting."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"milestones:{repo_name}",
                operation=lambda: self._boundary.get_repository_milestones(repo_name),
            ),
        )

    def get_repository_releases(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get releases via REST API with caching and rate limiting."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"releases:{repo_name}",
                operation=lambda: self._boundary.get_repository_releases(repo_name),
            ),
        )

    def get_issue_sub_issues(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get sub-issues for specific issue with rate limiting and caching."""
        return cast(
            List[Dict[str, Any]],
            self._execute_with_cross_cutting_concerns(
                cache_key=f"issue_sub_issues:{repo_name}:{issue_number}",
                operation=lambda: self._boundary.get_issue_sub_issues_graphql(
                    repo_name, issue_number
                ),
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

    def __getattr__(self, method_name: str) -> Callable[..., Any]:
        """
        Dynamically generate methods from operation registry.

        This is called only when an attribute isn't found explicitly on the class.
        Explicit methods (escape hatch) take precedence automatically.

        Args:
            method_name: Name of method being accessed

        Returns:
            Dynamically generated method

        Raises:
            AttributeError: If method not found in registry
        """
        operation = self._operation_registry.get_operation(method_name)

        if not operation:
            raise AttributeError(
                f"GitHubService has no method '{method_name}'. "
                f"Available operations: {self._operation_registry.list_operations()}"
            )

        # Create dynamic method
        def dynamic_method(**kwargs: Any) -> Any:
            return self._execute_operation(operation, **kwargs)

        # Make it debuggable
        dynamic_method.__name__ = method_name
        dynamic_method.__doc__ = (
            f"Dynamically generated method from {operation.entity_name} entity."
        )

        return dynamic_method

    def _execute_operation(self, operation: Operation, **kwargs: Any) -> Any:
        """
        Execute a registered operation with cross-cutting concerns.

        Args:
            operation: Operation instance from registry
            **kwargs: Method parameters

        Returns:
            Operation result (raw or converted)

        Raises:
            Exception: Enhanced with entity/spec context
        """
        try:
            # Apply caching if appropriate
            if operation.should_cache() and self._caching_enabled:
                cache_key = operation.get_cache_key(**kwargs)
                return self._execute_with_cross_cutting_concerns(
                    cache_key=cache_key,
                    operation=lambda: self._call_boundary(operation, **kwargs),
                )
            else:
                # No caching for write operations
                return self._execute_with_cross_cutting_concerns(
                    cache_key=None,
                    operation=lambda: self._call_boundary(operation, **kwargs),
                )
        except Exception as e:
            # Enhanced error context for debugging
            raise type(e)(
                f"Operation '{operation.method_name}' failed "
                f"(entity={operation.entity_name}, spec={operation.spec}): {e}"
            ) from e

    def _call_boundary(self, operation: Operation, **kwargs: Any) -> Any:
        """
        Call boundary method and apply converter if specified.

        Args:
            operation: Operation instance
            **kwargs: Method parameters

        Returns:
            Raw or converted result
        """
        logger.debug(
            f"Executing {operation.method_name} "
            f"[entity={operation.entity_name}, args={kwargs}]"
        )

        # Call the boundary method
        boundary_method = getattr(self._boundary, operation.boundary_method)
        raw_result = boundary_method(**kwargs)

        # Apply converter if specified
        if operation.converter_name:
            converter = self._get_converter(operation.converter_name)

            # Handle list results vs single results
            if isinstance(raw_result, list):
                result = [converter(item) for item in raw_result]
            else:
                result = converter(raw_result)

            logger.debug(
                f"Converted {operation.method_name} results "
                f"using {operation.converter_name}"
            )
            return result

        return raw_result

    def _get_converter(self, converter_name: str) -> Callable[..., Any]:
        """
        Get converter function by name.

        Args:
            converter_name: Name of converter function

        Returns:
            Converter function
        """
        from github_data_tools.github.converter_registry import get_converter

        return get_converter(converter_name)

    def _execute_with_cross_cutting_concerns(
        self, cache_key: Optional[str], operation: Callable[[], Any]
    ) -> Any:
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
