"""
GitHub API boundary layer.

Ultra-thin wrapper around PyGithub that returns raw JSON data.
This creates a true API boundary that's not coupled to PyGithub types.
"""

from typing import Dict, List, Any
from github import Github, Auth
from github.Repository import Repository
from github.PaginatedList import PaginatedList


class GitHubApiBoundary:
    """Thin boundary around PyGithub that returns raw JSON data."""

    def __init__(self, token: str):
        """Initialize GitHub API client with authentication token."""
        self._github = Github(auth=Auth.Token(token))

    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all labels from repository as raw JSON data."""
        repo = self._get_repository(repo_name)
        labels = repo.get_labels()
        return self._extract_raw_data_list(labels)

    def get_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issues from repository as raw JSON data."""
        repo = self._get_repository(repo_name)
        issues = repo.get_issues(state="all")
        return self._extract_raw_data_list(issues)

    def get_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific issue as raw JSON data."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)
        comments = issue.get_comments()
        return self._extract_raw_data_list(comments)

    def get_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all comments from all issues as raw JSON data."""
        repo = self._get_repository(repo_name)
        issues = repo.get_issues(state="all")
        all_comments = []

        for issue in issues:
            if self._issue_has_comments(issue):
                comments = issue.get_comments()
                comment_data = self._extract_raw_data_list(comments)
                all_comments.extend(comment_data)

        return all_comments

    def create_label(
        self, repo_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Create a new label and return raw JSON data."""
        repo = self._get_repository(repo_name)
        created_label = repo.create_label(
            name=name, color=color, description=description
        )
        return self._extract_raw_data(created_label)

    def create_issue(
        self, repo_name: str, title: str, body: str, labels: List[str]
    ) -> Dict[str, Any]:
        """Create a new issue and return raw JSON data."""
        repo = self._get_repository(repo_name)
        created_issue = repo.create_issue(title=title, body=body, labels=labels)
        return self._extract_raw_data(created_issue)

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

    def create_issue_comment(
        self, repo_name: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment on an issue and return raw JSON data."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)
        created_comment = issue.create_comment(body)
        return self._extract_raw_data(created_comment)

    def _get_repository(self, repo_name: str) -> Repository:
        """Get repository object from GitHub API."""
        return self._github.get_repo(repo_name)

    def _issue_has_comments(self, issue: Any) -> bool:
        """Check if issue has comments without triggering extra API calls."""
        issue_data = self._extract_raw_data(issue)
        return bool(issue_data.get("comments", 0) > 0)

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
