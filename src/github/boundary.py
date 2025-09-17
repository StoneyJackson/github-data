"""
GitHub API boundary layer.

Ultra-thin wrapper around PyGithub that returns raw JSON data.
This creates a true API boundary that's not coupled to PyGithub types.
Focused solely on API access - no rate limiting, caching, or retry logic.
"""

from typing import Dict, List, Any, Optional
from .protocols import GitHubApiBoundary as GitHubApiBoundaryProtocol
from .graphql_client import GitHubGraphQLClient
from .restapi_client import GitHubRestApiClient
from github import Github, Auth
from github.Repository import Repository


class GitHubApiBoundary(GitHubApiBoundaryProtocol):
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
        self._token = token
        self._graphql_client = GitHubGraphQLClient(token)
        self._rest_client = GitHubRestApiClient(token)

    # Public API - Repository Data Operations (GraphQL-enhanced)

    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all labels from repository using GraphQL for better performance."""
        return self._graphql_client.get_repository_labels(repo_name)

    def get_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issues from repository using GraphQL for better performance."""
        return self._graphql_client.get_repository_issues(repo_name)

    def get_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific issue as raw JSON data."""
        return self._rest_client.get_issue_comments(repo_name, issue_number)

    def get_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all comments from all issues using GraphQL for better performance."""
        return self._graphql_client.get_all_issue_comments(repo_name)

    # Public API - Repository Modification Operations

    def create_label(
        self, repo_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Create a new label and return raw JSON data."""
        return self._rest_client.create_label(repo_name, name, color, description)

    def delete_label(self, repo_name: str, label_name: str) -> None:
        """Delete a label from the repository."""
        self._rest_client.delete_label(repo_name, label_name)

    def update_label(
        self, repo_name: str, old_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Update an existing label and return raw JSON data."""
        return self._rest_client.update_label(
            repo_name, old_name, name, color, description
        )

    def create_issue(
        self, repo_name: str, title: str, body: str, labels: List[str]
    ) -> Dict[str, Any]:
        """Create a new issue and return raw JSON data."""
        return self._rest_client.create_issue(repo_name, title, body, labels)

    def create_issue_comment(
        self, repo_name: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment on an issue and return raw JSON data."""
        return self._rest_client.create_issue_comment(repo_name, issue_number, body)

    def close_issue(
        self, repo_name: str, issue_number: int, state_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close an issue with optional state reason and return raw JSON data."""
        return self._rest_client.close_issue(repo_name, issue_number, state_reason)

    # Public API - Rate Limit Monitoring

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status using GraphQL."""
        return self._graphql_client.get_rate_limit_status()

    # Low-level Repository Operations

    def _get_repository(self, repo_name: str) -> Repository:
        """Get repository object from GitHub API."""
        return self._github.get_repo(repo_name)

    # Public API - Pull Request Operations

    def get_repository_pull_requests(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull requests from repository using GraphQL for performance."""
        return self._graphql_client.get_repository_pull_requests(repo_name)

    def get_pull_request_comments(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request using GraphQL."""
        return self._graphql_client.get_pull_request_comments(repo_name, pr_number)

    def get_all_pull_request_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all comments from all pull requests using GraphQL for performance."""
        return self._graphql_client.get_all_pull_request_comments(repo_name)

    def create_pull_request(
        self, repo_name: str, title: str, body: str, head: str, base: str
    ) -> Dict[str, Any]:
        """Create a new pull request and return raw JSON data."""
        return self._rest_client.create_pull_request(repo_name, title, body, head, base)

    def create_pull_request_comment(
        self, repo_name: str, pr_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment on a pull request and return raw JSON data."""
        return self._rest_client.create_pull_request_comment(repo_name, pr_number, body)

    # Public API - Sub-Issues Operations (GraphQL)

    def get_repository_sub_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all sub-issue relationships from repository using GraphQL."""
        return self._graphql_client.get_repository_sub_issues(repo_name)

    def get_issue_sub_issues_graphql(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get sub-issues for a specific issue using GraphQL."""
        return self._graphql_client.get_issue_sub_issues_graphql(
            repo_name, issue_number
        )

    # Public API - Sub-Issues Operations (REST)

    def get_issue_sub_issues(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get sub-issues for a specific issue using REST API."""
        return self._rest_client.get_issue_sub_issues(repo_name, issue_number)

    def get_issue_parent(
        self, repo_name: str, issue_number: int
    ) -> Optional[Dict[str, Any]]:
        """Get parent issue if this issue is a sub-issue using REST API."""
        return self._rest_client.get_issue_parent(repo_name, issue_number)

    def add_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> Dict[str, Any]:
        """Add existing issue as sub-issue using REST API."""
        return self._rest_client.add_sub_issue(
            repo_name, parent_issue_number, sub_issue_number
        )

    def remove_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> None:
        """Remove sub-issue relationship using REST API."""
        self._rest_client.remove_sub_issue(
            repo_name, parent_issue_number, sub_issue_number
        )

    def reprioritize_sub_issue(
        self,
        repo_name: str,
        parent_issue_number: int,
        sub_issue_number: int,
        position: int,
    ) -> Dict[str, Any]:
        """Change sub-issue order/position using REST API."""
        return self._rest_client.reprioritize_sub_issue(
            repo_name, parent_issue_number, sub_issue_number, position
        )
