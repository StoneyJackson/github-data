"""
GitHub service layer.

Provides business logic and data conversion on top of the GitHub API boundary.
This is the main interface that application code should use.
"""

from typing import List

from .boundary import GitHubApiBoundary
from .converters import convert_to_label, convert_to_issue, convert_to_comment
from ..models import Label, Issue, Comment


class GitHubService:
    """GitHub service providing business logic and data conversion."""

    def __init__(self, token: str):
        """Initialize GitHub service with authentication token."""
        self._boundary = GitHubApiBoundary(token)

    def get_repository_labels(self, repo_name: str) -> List[Label]:
        """Get all labels from the specified repository."""
        raw_labels = self._boundary.get_repository_labels(repo_name)
        return self._convert_labels(raw_labels)

    def get_repository_issues(self, repo_name: str) -> List[Issue]:
        """Get all issues from the specified repository."""
        raw_issues = self._boundary.get_repository_issues(repo_name)
        return self._convert_issues(raw_issues)

    def get_issue_comments(self, repo_name: str, issue_number: int) -> List[Comment]:
        """Get all comments for a specific issue."""
        raw_comments = self._boundary.get_issue_comments(repo_name, issue_number)
        return self._convert_comments(raw_comments)

    def get_all_issue_comments(self, repo_name: str) -> List[Comment]:
        """Get all comments from all issues in the repository."""
        raw_comments = self._boundary.get_all_issue_comments(repo_name)
        return self._convert_comments(raw_comments)

    def create_label(self, repo_name: str, label: Label) -> Label:
        """Create a new label in the repository."""
        raw_label = self._boundary.create_label(
            repo_name=repo_name,
            name=label.name,
            color=label.color,
            description=label.description or "",
        )
        return convert_to_label(raw_label)

    def create_issue(self, repo_name: str, issue: Issue) -> Issue:
        """Create a new issue in the repository."""
        label_names = self._extract_label_names(issue.labels)

        raw_issue = self._boundary.create_issue(
            repo_name=repo_name,
            title=issue.title,
            body=issue.body or "",
            labels=label_names,
        )
        return convert_to_issue(raw_issue)

    def delete_label(self, repo_name: str, label_name: str) -> None:
        """Delete a label from the repository."""
        self._boundary.delete_label(repo_name, label_name)

    def update_label(self, repo_name: str, old_name: str, label: Label) -> Label:
        """Update an existing label in the repository."""
        raw_label = self._boundary.update_label(
            repo_name=repo_name,
            old_name=old_name,
            name=label.name,
            color=label.color,
            description=label.description or "",
        )
        return convert_to_label(raw_label)

    def _convert_labels(self, raw_labels: List[dict]) -> List[Label]:
        """Convert list of raw label data to Label models."""
        return [convert_to_label(raw_label) for raw_label in raw_labels]

    def _convert_issues(self, raw_issues: List[dict]) -> List[Issue]:
        """Convert list of raw issue data to Issue models."""
        return [convert_to_issue(raw_issue) for raw_issue in raw_issues]

    def _convert_comments(self, raw_comments: List[dict]) -> List[Comment]:
        """Convert list of raw comment data to Comment models."""
        return [convert_to_comment(raw_comment) for raw_comment in raw_comments]

    def _extract_label_names(self, labels: List[Label]) -> List[str]:
        """Extract label names for GitHub API calls."""
        return [label.name for label in labels]
