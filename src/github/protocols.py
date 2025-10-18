"""
Abstract protocols for GitHub service dependencies.

Defines explicit contracts for dependency inversion, enabling better testability
and architectural clarity through abstract interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable


class RepositoryService(ABC):
    """Abstract interface for repository data operations."""

    # Repository Data Operations (Read)

    @abstractmethod
    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all labels from repository."""
        pass

    @abstractmethod
    def get_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issues from repository."""
        pass

    @abstractmethod
    def get_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific issue."""
        pass

    @abstractmethod
    def get_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issue comments."""
        pass

    @abstractmethod
    def get_repository_pull_requests(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull requests from repository."""
        pass

    @abstractmethod
    def get_pull_request_comments(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request."""
        pass

    @abstractmethod
    def get_all_pull_request_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull request comments."""
        pass

    @abstractmethod
    def get_pull_request_reviews(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get reviews for specific pull request."""
        pass

    @abstractmethod
    def get_all_pull_request_reviews(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull request reviews."""
        pass

    @abstractmethod
    def get_pull_request_review_comments(
        self, repo_name: str, review_id: str
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request review."""
        pass

    @abstractmethod
    def get_all_pull_request_review_comments(
        self, repo_name: str
    ) -> List[Dict[str, Any]]:
        """Get all pull request review comments."""
        pass

    @abstractmethod
    def get_repository_sub_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get sub-issue relationships from repository."""
        pass

    @abstractmethod
    def get_issue_sub_issues(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get sub-issues for specific issue."""
        pass

    @abstractmethod
    def get_issue_parent(
        self, repo_name: str, issue_number: int
    ) -> Optional[Dict[str, Any]]:
        """Get parent issue if this issue is a sub-issue."""
        pass

    @abstractmethod
    def get_repository_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all milestones from the repository.

        Args:
            repo_name: The repository name in format 'owner/repo'

        Returns:
            List of milestone dictionaries from GitHub API
        """
        pass

    @abstractmethod
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        pass

    # Repository Modification Operations (Write)

    @abstractmethod
    def create_label(
        self, repo_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Create a new label."""
        pass

    @abstractmethod
    def delete_label(self, repo_name: str, label_name: str) -> None:
        """Delete a label."""
        pass

    @abstractmethod
    def update_label(
        self, repo_name: str, old_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Update an existing label."""
        pass

    @abstractmethod
    def create_issue(
        self,
        repo_name: str,
        title: str,
        body: str,
        labels: List[str],
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new issue."""
        pass

    @abstractmethod
    def create_issue_comment(
        self, repo_name: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment."""
        pass

    @abstractmethod
    def close_issue(
        self, repo_name: str, issue_number: int, state_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close an issue."""
        pass

    @abstractmethod
    def create_pull_request(
        self,
        repo_name: str,
        title: str,
        body: str,
        head: str,
        base: str,
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new pull request."""
        pass

    @abstractmethod
    def create_pull_request_comment(
        self, repo_name: str, pr_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new PR comment."""
        pass

    @abstractmethod
    def create_pull_request_review(
        self, repo_name: str, pr_number: int, body: str, state: str
    ) -> Dict[str, Any]:
        """Create a new pull request review."""
        pass

    @abstractmethod
    def create_pull_request_review_comment(
        self, repo_name: str, review_id: str, body: str
    ) -> Dict[str, Any]:
        """Create a new pull request review comment."""
        pass

    @abstractmethod
    def add_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> Dict[str, Any]:
        """Add existing issue as sub-issue."""
        pass

    @abstractmethod
    def remove_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> None:
        """Remove sub-issue relationship."""
        pass

    @abstractmethod
    def reprioritize_sub_issue(
        self,
        repo_name: str,
        parent_issue_number: int,
        sub_issue_number: int,
        position: int,
    ) -> Dict[str, Any]:
        """Change sub-issue order/position."""
        pass

    @abstractmethod
    def create_milestone(
        self,
        repo_name: str,
        title: str,
        description: Optional[str] = None,
        due_on: Optional[str] = None,
        state: str = "open",
    ) -> Dict[str, Any]:
        """Create a new milestone in the repository.

        Args:
            repo_name: The repository name in format 'owner/repo'
            title: Milestone title
            description: Optional milestone description
            due_on: Optional due date in ISO format
            state: Milestone state ("open" or "closed")

        Returns:
            Created milestone dictionary from GitHub API
        """
        pass


class RateLimitHandler(ABC):
    """Abstract interface for rate limiting operations."""

    @abstractmethod
    def execute_with_retry(
        self, operation: Callable[[], Any], github_client: Any
    ) -> Any:
        """Execute operation with rate limiting and retry logic."""
        pass


class GitHubApiBoundary(ABC):
    """Abstract interface for GitHub API boundary operations."""

    @abstractmethod
    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get labels from GitHub API."""
        pass

    @abstractmethod
    def get_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get issues from GitHub API."""
        pass

    @abstractmethod
    def get_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get issue comments from GitHub API."""
        pass

    @abstractmethod
    def get_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issue comments from GitHub API."""
        pass

    @abstractmethod
    def get_repository_pull_requests(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get pull requests from GitHub API."""
        pass

    @abstractmethod
    def get_pull_request_comments(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get PR comments from GitHub API."""
        pass

    @abstractmethod
    def get_all_pull_request_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all PR comments from GitHub API."""
        pass

    @abstractmethod
    def get_pull_request_reviews(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get reviews for specific pull request from GitHub API."""
        pass

    @abstractmethod
    def get_all_pull_request_reviews(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull request reviews from GitHub API."""
        pass

    @abstractmethod
    def get_pull_request_review_comments(
        self, repo_name: str, review_id: str
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request review from GitHub API."""
        pass

    @abstractmethod
    def get_all_pull_request_review_comments(
        self, repo_name: str
    ) -> List[Dict[str, Any]]:
        """Get all pull request review comments from GitHub API."""
        pass

    @abstractmethod
    def get_repository_sub_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get sub-issues from GitHub API."""
        pass

    @abstractmethod
    def get_issue_sub_issues_graphql(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get issue sub-issues from GitHub GraphQL API."""
        pass

    @abstractmethod
    def get_issue_parent(
        self, repo_name: str, issue_number: int
    ) -> Optional[Dict[str, Any]]:
        """Get issue parent from GitHub API."""
        pass

    @abstractmethod
    def get_repository_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get milestones via GraphQL with pagination."""
        pass

    @abstractmethod
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get rate limit status from GitHub API."""
        pass

    @abstractmethod
    def create_label(
        self, repo_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Create label via GitHub API."""
        pass

    @abstractmethod
    def delete_label(self, repo_name: str, label_name: str) -> None:
        """Delete label via GitHub API."""
        pass

    @abstractmethod
    def update_label(
        self, repo_name: str, old_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Update label via GitHub API."""
        pass

    @abstractmethod
    def create_issue(
        self,
        repo_name: str,
        title: str,
        body: str,
        labels: List[str],
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create issue via GitHub API."""
        pass

    @abstractmethod
    def create_issue_comment(
        self, repo_name: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Create issue comment via GitHub API."""
        pass

    @abstractmethod
    def close_issue(
        self, repo_name: str, issue_number: int, state_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close issue via GitHub API."""
        pass

    @abstractmethod
    def create_pull_request(
        self,
        repo_name: str,
        title: str,
        body: str,
        head: str,
        base: str,
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create pull request via GitHub API."""
        pass

    @abstractmethod
    def create_pull_request_comment(
        self, repo_name: str, pr_number: int, body: str
    ) -> Dict[str, Any]:
        """Create PR comment via GitHub API."""
        pass

    @abstractmethod
    def create_pull_request_review(
        self, repo_name: str, pr_number: int, body: str, state: str
    ) -> Dict[str, Any]:
        """Create pull request review via GitHub API."""
        pass

    @abstractmethod
    def create_pull_request_review_comment(
        self, repo_name: str, review_id: str, body: str
    ) -> Dict[str, Any]:
        """Create pull request review comment via GitHub API."""
        pass

    @abstractmethod
    def add_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> Dict[str, Any]:
        """Add sub-issue via GitHub API."""
        pass

    @abstractmethod
    def remove_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> None:
        """Remove sub-issue via GitHub API."""
        pass

    @abstractmethod
    def reprioritize_sub_issue(
        self,
        repo_name: str,
        parent_issue_number: int,
        sub_issue_number: int,
        position: int,
    ) -> Dict[str, Any]:
        """Reprioritize sub-issue via GitHub API."""
        pass

    @abstractmethod
    def create_milestone(
        self,
        repo_name: str,
        title: str,
        description: Optional[str] = None,
        due_on: Optional[str] = None,
        state: str = "open",
    ) -> Dict[str, Any]:
        """Create milestone via REST API."""
        pass
