"""
GitHub API boundary layer.

Ultra-thin wrapper around PyGithub that returns raw JSON data.
This creates a true API boundary that's not coupled to PyGithub types.
"""

import time
import random
import logging
from typing import Dict, List, Any, Optional, Callable, TypeVar
from github import Github, Auth
from github.Repository import Repository
from github.PaginatedList import PaginatedList
from github.GithubException import RateLimitExceededException, GithubException

logger = logging.getLogger(__name__)

T = TypeVar("T")


class GitHubApiBoundary:
    """
    Thin boundary around PyGithub that returns raw JSON data.

    Provides rate-limited access to GitHub API operations with automatic
    retry logic and comprehensive error handling.
    """

    def __init__(
        self,
        token: str,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
    ):
        """
        Initialize GitHub API client with authentication and rate limiting config.

        Args:
            token: GitHub authentication token
            max_retries: Maximum number of retries on rate limit errors
            base_delay: Base delay in seconds for exponential backoff
            max_delay: Maximum delay in seconds between retries
            jitter: Whether to add random jitter to delays
        """
        self._github = Github(auth=Auth.Token(token))
        self._rate_limiter = RateLimitHandler(
            max_retries, base_delay, max_delay, jitter
        )

    # Public API - Repository Data Operations

    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all labels from repository as raw JSON data."""
        return self._execute_with_retry(
            lambda: self._fetch_repository_labels(repo_name)
        )

    def get_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issues from repository as raw JSON data, excluding pull requests."""
        return self._execute_with_retry(
            lambda: self._fetch_repository_issues(repo_name)
        )

    def get_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific issue as raw JSON data."""
        return self._execute_with_retry(
            lambda: self._fetch_issue_comments(repo_name, issue_number)
        )

    def get_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all comments from all issues as raw JSON data, excluding PR comments."""
        return self._execute_with_retry(
            lambda: self._fetch_all_issue_comments(repo_name)
        )

    # Public API - Repository Modification Operations

    def create_label(
        self, repo_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Create a new label and return raw JSON data."""
        return self._execute_with_retry(
            lambda: self._perform_create_label(repo_name, name, color, description)
        )

    def delete_label(self, repo_name: str, label_name: str) -> None:
        """Delete a label from the repository."""
        self._execute_with_retry(
            lambda: self._perform_delete_label(repo_name, label_name)
        )

    def update_label(
        self, repo_name: str, old_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Update an existing label and return raw JSON data."""
        return self._execute_with_retry(
            lambda: self._perform_update_label(
                repo_name, old_name, name, color, description
            )
        )

    def create_issue(
        self, repo_name: str, title: str, body: str, labels: List[str]
    ) -> Dict[str, Any]:
        """Create a new issue and return raw JSON data."""
        return self._execute_with_retry(
            lambda: self._perform_create_issue(repo_name, title, body, labels)
        )

    def create_issue_comment(
        self, repo_name: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment on an issue and return raw JSON data."""
        return self._execute_with_retry(
            lambda: self._perform_create_comment(repo_name, issue_number, body)
        )

    def close_issue(
        self, repo_name: str, issue_number: int, state_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close an issue with optional state reason and return raw JSON data."""
        return self._execute_with_retry(
            lambda: self._perform_close_issue(repo_name, issue_number, state_reason)
        )

    # Public API - Rate Limit Monitoring

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status from GitHub API."""
        return self._execute_with_retry(lambda: self._fetch_rate_limit_status())

    # Rate Limiting Operations

    def _execute_with_retry(self, operation: Callable[[], T]) -> T:
        """Execute operation with rate limit retry logic."""
        return self._rate_limiter.execute_with_retry(operation, self._github)

    # Repository Access Operations

    def _fetch_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Fetch all labels from repository."""
        repo = self._get_repository(repo_name)
        labels = repo.get_labels()
        return self._extract_raw_data_list(labels)

    def _fetch_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Fetch all issues from repository, excluding pull requests."""
        repo = self._get_repository(repo_name)
        issues = repo.get_issues(state="all")
        all_issues_data = self._extract_raw_data_list(issues)
        return self._filter_out_pull_requests(all_issues_data)

    def _fetch_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Fetch comments for specific issue."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)
        comments = issue.get_comments()
        return self._extract_raw_data_list(comments)

    def _fetch_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Fetch all comments from all issues, excluding PR comments."""
        repo = self._get_repository(repo_name)
        issues = repo.get_issues(state="all")

        all_comments = []
        for issue in issues:
            if self._should_include_issue_comments(issue):
                comments = issue.get_comments()
                comment_data = self._extract_raw_data_list(comments)
                all_comments.extend(comment_data)

        return all_comments

    def _fetch_rate_limit_status(self) -> Dict[str, Any]:
        """Fetch current rate limit status."""
        rate_limit = self._github.get_rate_limit()
        return self._build_rate_limit_response(rate_limit)

    # Repository Modification Operations

    def _perform_create_label(
        self, repo_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Create a new label in the repository."""
        repo = self._get_repository(repo_name)
        created_label = repo.create_label(
            name=name, color=color, description=description
        )
        return self._extract_raw_data(created_label)

    def _perform_delete_label(self, repo_name: str, label_name: str) -> None:
        """Delete a label from the repository."""
        repo = self._get_repository(repo_name)
        label = repo.get_label(label_name)
        label.delete()

    def _perform_update_label(
        self, repo_name: str, old_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Update an existing label in the repository."""
        repo = self._get_repository(repo_name)
        label = repo.get_label(old_name)
        label.edit(name=name, color=color, description=description)
        return self._extract_raw_data(label)

    def _perform_create_issue(
        self, repo_name: str, title: str, body: str, labels: List[str]
    ) -> Dict[str, Any]:
        """Create a new issue in the repository."""
        repo = self._get_repository(repo_name)
        created_issue = repo.create_issue(title=title, body=body, labels=labels)
        return self._extract_raw_data(created_issue)

    def _perform_create_comment(
        self, repo_name: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment on an issue."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)
        created_comment = issue.create_comment(body)
        return self._extract_raw_data(created_comment)

    def _perform_close_issue(
        self, repo_name: str, issue_number: int, state_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close an issue with optional state reason."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)

        if state_reason:
            issue.edit(state="closed", state_reason=state_reason)
        else:
            issue.edit(state="closed")

        return self._extract_raw_data(issue)

    # Low-level Repository Operations

    def _get_repository(self, repo_name: str) -> Repository:
        """Get repository object from GitHub API."""
        return self._github.get_repo(repo_name)

    # Data Processing Utilities

    def _should_include_issue_comments(self, issue: Any) -> bool:
        """Check if issue comments should be included (not PR, has comments)."""
        return not self._is_pull_request(issue) and self._issue_has_comments(issue)

    def _issue_has_comments(self, issue: Any) -> bool:
        """Check if issue has comments without triggering extra API calls."""
        issue_data = self._extract_raw_data(issue)
        return bool(issue_data.get("comments", 0) > 0)

    def _is_pull_request(self, issue: Any) -> bool:
        """Check if an issue is actually a pull request."""
        issue_data = self._extract_raw_data(issue)
        return "pull_request" in issue_data and issue_data["pull_request"] is not None

    def _filter_out_pull_requests(
        self, issues_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter out pull requests from a list of issue data."""
        return [
            issue_data
            for issue_data in issues_data
            if not self._is_pull_request_data(issue_data)
        ]

    def _is_pull_request_data(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue data represents a pull request."""
        return "pull_request" in issue_data and issue_data["pull_request"] is not None

    def _build_rate_limit_response(self, rate_limit: Any) -> Dict[str, Any]:
        """Build rate limit response from API data."""
        core = getattr(rate_limit, "core", None)
        search = getattr(rate_limit, "search", None)

        result = {}
        if core:
            result["core"] = self._build_rate_limit_section(core)
        if search:
            result["search"] = self._build_rate_limit_section(search)

        return result

    def _build_rate_limit_section(self, section: Any) -> Dict[str, Any]:
        """Build rate limit section data."""
        return {
            "limit": getattr(section, "limit", None),
            "remaining": getattr(section, "remaining", None),
            "reset": self._format_reset_time(section),
        }

    def _format_reset_time(self, section: Any) -> Optional[str]:
        """Format reset time from rate limit section."""
        if hasattr(section, "reset") and section.reset:
            return str(section.reset.isoformat())
        return None

    # Raw Data Extraction Utilities

    def _extract_raw_data_list(
        self, pygithub_objects: PaginatedList[Any]
    ) -> List[Dict[str, Any]]:
        """Extract raw JSON data from a list of PyGithub objects."""
        return [self._extract_raw_data(obj) for obj in pygithub_objects]

    def _extract_raw_data(self, pygithub_obj: Any) -> Dict[str, Any]:
        """
        Extract raw JSON data from PyGithub objects.

        Uses _rawData to avoid additional API calls where possible.
        Can be switched to raw_data if we need complete data.

        Args:
            pygithub_obj: PyGithub object to extract data from

        Returns:
            Raw JSON data as dictionary

        Raises:
            ValueError: If object doesn't have raw data attributes
        """
        if hasattr(pygithub_obj, "_rawData"):
            return dict(pygithub_obj._rawData)
        elif hasattr(pygithub_obj, "raw_data"):
            return dict(pygithub_obj.raw_data)
        else:
            raise ValueError(
                f"Cannot extract raw data from {type(pygithub_obj).__name__}: "
                f"object has no '_rawData' or 'raw_data' attribute"
            )


class RateLimitHandler:
    """
    Handles rate limiting logic for GitHub API operations.

    Implements exponential backoff with jitter and comprehensive monitoring.
    """

    def __init__(
        self, max_retries: int, base_delay: float, max_delay: float, jitter: bool
    ):
        """
        Initialize rate limit handler.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff
            max_delay: Maximum delay between retries
            jitter: Whether to add random jitter to delays
        """
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._jitter = jitter

    def execute_with_retry(self, operation: Callable[[], T], github_client: Any) -> T:
        """
        Execute operation with rate limit retry logic.

        Args:
            operation: Function to execute with retry logic
            github_client: GitHub client for rate limit monitoring

        Returns:
            Result of the operation

        Raises:
            RateLimitExceededException: If max retries exceeded
            GithubException: For other GitHub API errors
        """
        last_exception = None

        for attempt in range(self._max_retries + 1):
            try:
                result = operation()
                self._monitor_rate_limit_status(github_client)
                return result

            except RateLimitExceededException as e:
                last_exception = e
                if self._should_retry(attempt):
                    self._handle_rate_limit_retry(attempt)
                else:
                    self._handle_max_retries_reached()
                    raise

            except GithubException as e:
                self._handle_github_api_error(e)
                raise

        # Safety fallback - should never be reached
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected end of retry loop")

    def _should_retry(self, attempt: int) -> bool:
        """Check if we should retry the operation."""
        return attempt < self._max_retries

    def _handle_rate_limit_retry(self, attempt: int) -> None:
        """Handle rate limit retry with delay."""
        delay = self._calculate_retry_delay(attempt)
        logger.warning(
            f"GitHub API rate limit exceeded. Retrying in {delay:.1f}s "
            f"(attempt {attempt + 1}/{self._max_retries + 1})"
        )
        time.sleep(delay)

    def _handle_max_retries_reached(self) -> None:
        """Handle max retries reached scenario."""
        logger.error(
            f"GitHub API rate limit exceeded. "
            f"Max retries ({self._max_retries}) reached."
        )

    def _handle_github_api_error(self, error: GithubException) -> None:
        """Handle general GitHub API errors."""
        logger.error(f"GitHub API error: {error.status} - {error.data}")

    def _monitor_rate_limit_status(self, github_client: Any) -> None:
        """Monitor rate limit status and log warnings if low."""
        try:
            rate_limit = github_client.get_rate_limit()
            core_limit = getattr(rate_limit, "core", None)

            if self._is_rate_limit_low(core_limit):
                self._log_low_rate_limit_warning(core_limit)

        except (AttributeError, GithubException, TypeError):
            # Skip rate limit monitoring if it fails (e.g., in tests)
            pass

    def _is_rate_limit_low(self, core_limit: Any) -> bool:
        """Check if rate limit is low (below threshold)."""
        if not core_limit or not hasattr(core_limit, "remaining"):
            return False

        remaining_count = getattr(core_limit, "remaining", None)
        return (
            remaining_count is not None
            and isinstance(remaining_count, int)
            and remaining_count < 100
        )

    def _log_low_rate_limit_warning(self, core_limit: Any) -> None:
        """Log warning about low rate limit."""
        remaining_count = getattr(core_limit, "remaining", 0)
        reset_time = getattr(core_limit, "reset", None)
        logger.warning(
            f"GitHub API rate limit low: {remaining_count} "
            f"requests remaining, resets at {reset_time}"
        )

    def _calculate_retry_delay(self, attempt: int) -> float:
        """
        Calculate retry delay with exponential backoff and optional jitter.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Delay in seconds
        """
        delay = min(self._base_delay * (2**attempt), self._max_delay)

        if self._jitter:
            delay = self._add_jitter_to_delay(delay)

        return float(max(delay, 0.1))  # Ensure minimum delay

    def _add_jitter_to_delay(self, delay: float) -> float:
        """Add random jitter to delay to prevent thundering herd."""
        jitter_range = delay * 0.25  # Up to 25% jitter
        return delay + random.uniform(-jitter_range, jitter_range)
