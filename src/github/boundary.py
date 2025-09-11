"""
GitHub API boundary layer.

Ultra-thin wrapper around PyGithub that returns raw JSON data.
This creates a true API boundary that's not coupled to PyGithub types.
Focused solely on API access - no rate limiting, caching, or retry logic.
"""

from typing import Dict, List, Any, Optional
from github import Github, Auth
from github.Repository import Repository
from github.PaginatedList import PaginatedList


class GitHubApiBoundary:
    """
    Ultra-thin boundary around PyGithub that returns raw JSON data.

    Provides direct access to GitHub API operations without any
    rate limiting, caching, or retry logic. Pure API access layer.
    """

    def __init__(self, token: str):
        """
        Initialize GitHub API client with authentication.

        Args:
            token: GitHub authentication token
        """
        self._github = Github(auth=Auth.Token(token))

    # Public API - Repository Data Operations

    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all labels from repository as raw JSON data."""
        repo = self._get_repository(repo_name)
        labels = repo.get_labels()
        return self._extract_raw_data_list(labels)

    def get_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issues from repository as raw JSON data, excluding pull requests."""
        repo = self._get_repository(repo_name)
        issues = repo.get_issues(state="all")
        all_issues_data = self._extract_raw_data_list(issues)
        return self._filter_out_pull_requests(all_issues_data)

    def get_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific issue as raw JSON data."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)
        comments = issue.get_comments()
        return self._extract_raw_data_list(comments)

    def get_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all comments from all issues as raw JSON data, excluding PR comments."""
        repo = self._get_repository(repo_name)
        issues = repo.get_issues(state="all")

        all_comments = []
        for issue in issues:
            if self._should_include_issue_comments(issue):
                comments = issue.get_comments()
                comment_data = self._extract_raw_data_list(comments)
                all_comments.extend(comment_data)

        return all_comments

    # Public API - Repository Modification Operations

    def create_label(
        self, repo_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Create a new label and return raw JSON data."""
        repo = self._get_repository(repo_name)
        created_label = repo.create_label(
            name=name, color=color, description=description
        )
        return self._extract_raw_data(created_label)

    def delete_label(self, repo_name: str, label_name: str) -> None:
        """Delete a label from the repository."""
        repo = self._get_repository(repo_name)
        label = repo.get_label(label_name)
        label.delete()

    def update_label(
        self, repo_name: str, old_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Update an existing label and return raw JSON data."""
        repo = self._get_repository(repo_name)
        label = repo.get_label(old_name)
        label.edit(name=name, color=color, description=description)
        return self._extract_raw_data(label)

    def create_issue(
        self, repo_name: str, title: str, body: str, labels: List[str]
    ) -> Dict[str, Any]:
        """Create a new issue and return raw JSON data."""
        repo = self._get_repository(repo_name)
        created_issue = repo.create_issue(title=title, body=body, labels=labels)
        return self._extract_raw_data(created_issue)

    def create_issue_comment(
        self, repo_name: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment on an issue and return raw JSON data."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)
        created_comment = issue.create_comment(body)
        return self._extract_raw_data(created_comment)

    def close_issue(
        self, repo_name: str, issue_number: int, state_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close an issue with optional state reason and return raw JSON data."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)

        if state_reason:
            issue.edit(state="closed", state_reason=state_reason)
        else:
            issue.edit(state="closed")

        return self._extract_raw_data(issue)

    # Public API - Rate Limit Monitoring

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status from GitHub API."""
        rate_limit = self._github.get_rate_limit()
        return self._build_rate_limit_response(rate_limit)

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
