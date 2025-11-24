"""
GitHub API boundary layer.

Ultra-thin wrapper around PyGithub that returns raw JSON data.
This creates a true API boundary that's not coupled to PyGithub types.
Focused solely on API access - no rate limiting, caching, or retry logic.
"""

import logging
from typing import Dict, List, Any, Optional, cast
from .protocols import GitHubApiBoundary as GitHubApiBoundaryProtocol
from .graphql_client import GitHubGraphQLClient
from .restapi_client import GitHubRestApiClient
from github import Github, Auth
from github.Repository import Repository
from github.AuthenticatedUser import AuthenticatedUser


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
        self._rest_client = GitHubRestApiClient(token, github_instance=self._github)

    # Public API - Repository Data Operations (GraphQL-enhanced)

    def get_repository_metadata(self, repo_name: str) -> Dict[str, Any]:
        """Get repository metadata.

        Args:
            repo_name: Repository name in format "owner/repo"

        Returns:
            Raw JSON dictionary of repository metadata

        Raises:
            UnknownObjectException: If repository not found (404)
            GithubException: For other API errors
        """
        repo = self._github.get_repo(repo_name)
        return repo.raw_data

    # NOTE: create_repository method moved to github-repo-manager package
    # for focused repository lifecycle management

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
        self,
        repo_name: str,
        title: str,
        body: str,
        labels: List[str],
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new issue and return raw JSON data."""
        return self._rest_client.create_issue(
            repo_name, title, body, labels, milestone=milestone
        )

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

    # Public API - Milestone Operations

    def get_repository_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get milestones via GraphQL with pagination."""
        try:
            return self._graphql_client.get_repository_milestones(repo_name)
        except Exception as e:
            logging.error(f"Failed to get milestones for {repo_name}: {e}")
            raise

    def get_repository_releases(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all releases from repository via REST API.

        Note: Uses REST API as releases are not fully supported in GraphQL.
        PyGithub's get_releases() returns a PaginatedList that handles
        pagination automatically.
        """
        repo = self._github.get_repo(repo_name)
        releases = repo.get_releases()

        # Convert PaginatedList to list of raw_data dicts
        return [release.raw_data for release in releases]

    def create_milestone(
        self,
        repo_name: str,
        title: str,
        description: Optional[str] = None,
        due_on: Optional[str] = None,
        state: str = "open",
    ) -> Dict[str, Any]:
        """Create milestone via REST API."""
        try:
            return self._rest_client.create_milestone(
                repo_name, title, description, due_on, state
            )
        except Exception as e:
            logging.error(f"Failed to create milestone '{title}' for {repo_name}: {e}")
            raise

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
        """Create a release via REST API."""
        repo = self._github.get_repo(repo_name)

        release = repo.create_git_release(
            tag=tag_name,
            name=name or tag_name,
            message=body or "",
            draft=draft,
            prerelease=prerelease,
            target_commitish=target_commitish,
        )

        return release.raw_data

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
        self,
        repo_name: str,
        title: str,
        body: str,
        head: str,
        base: str,
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new pull request and return raw JSON data."""
        return self._rest_client.create_pull_request(
            repo_name, title, body, head, base, milestone=milestone
        )

    def create_pull_request_comment(
        self, repo_name: str, pr_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment on a pull request and return raw JSON data."""
        return self._rest_client.create_pull_request_comment(repo_name, pr_number, body)

    def get_pull_request_reviews(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get reviews for specific pull request using GraphQL."""
        return self._graphql_client.get_pull_request_reviews(repo_name, pr_number)

    def get_all_pull_request_reviews(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull request reviews using GraphQL for performance."""
        return self._graphql_client.get_all_pull_request_reviews(repo_name)

    def get_pull_request_review_comments(
        self, repo_name: str, review_id: str
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request review using GraphQL."""
        return self._graphql_client.get_pull_request_review_comments(
            repo_name, review_id
        )

    def get_all_pull_request_review_comments(
        self, repo_name: str
    ) -> List[Dict[str, Any]]:
        """Get all pull request review comments using GraphQL for performance."""
        return self._graphql_client.get_all_pull_request_review_comments(repo_name)

    def create_pull_request_review(
        self, repo_name: str, pr_number: int, body: str, state: str
    ) -> Dict[str, Any]:
        """Create a new pull request review and return raw JSON data."""
        return self._rest_client.create_pull_request_review(
            repo_name, pr_number, body, state
        )

    def create_pull_request_review_comment(
        self, repo_name: str, review_id: str, body: str
    ) -> Dict[str, Any]:
        """Create a new pull request review comment and return raw JSON data."""
        return self._rest_client.create_pull_request_review_comment(
            repo_name, review_id, body
        )

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
