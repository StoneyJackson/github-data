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

# Required GraphQL imports
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from .graphql_queries import (
    REPOSITORY_LABELS_QUERY,
    REPOSITORY_ISSUES_QUERY,
    REPOSITORY_COMMENTS_QUERY,
    REPOSITORY_PULL_REQUESTS_QUERY,
    PULL_REQUEST_COMMENTS_QUERY,
    REPOSITORY_PR_COMMENTS_QUERY,
    RATE_LIMIT_QUERY,
)
from .graphql_converters import (
    convert_graphql_labels_to_rest_format,
    convert_graphql_issues_to_rest_format,
    convert_graphql_comments_to_rest_format,
    convert_graphql_pull_requests_to_rest_format,
    convert_graphql_pr_comments_to_rest_format,
    convert_graphql_rate_limit_to_rest_format,
)


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
        self._token = token
        self._gql_client = self._create_graphql_client(token)

    # GraphQL Client Setup

    def _create_graphql_client(self, token: str) -> Client:
        """Create and configure GraphQL client for GitHub API."""
        transport = RequestsHTTPTransport(
            url="https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {token}"},
        )
        return Client(transport=transport, fetch_schema_from_transport=True)

    # Public API - Repository Data Operations (GraphQL-enhanced)

    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all labels from repository using GraphQL for better performance."""
        owner, name = self._parse_repo_name(repo_name)

        result = self._gql_client.execute(
            REPOSITORY_LABELS_QUERY, variable_values={"owner": owner, "name": name}
        )

        graphql_labels = result["repository"]["labels"]["nodes"]
        return convert_graphql_labels_to_rest_format(graphql_labels)

    def get_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issues from repository using GraphQL for better performance."""
        owner, name = self._parse_repo_name(repo_name)
        all_issues = []
        cursor = None

        while True:
            result = self._gql_client.execute(
                REPOSITORY_ISSUES_QUERY,
                variable_values={
                    "owner": owner,
                    "name": name,
                    "first": 100,
                    "after": cursor,
                },
            )

            issues_data = result["repository"]["issues"]
            all_issues.extend(issues_data["nodes"])

            if not issues_data["pageInfo"]["hasNextPage"]:
                break
            cursor = issues_data["pageInfo"]["endCursor"]

        return convert_graphql_issues_to_rest_format(all_issues, repo_name)

    def get_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific issue as raw JSON data."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)
        comments = issue.get_comments()
        return self._extract_raw_data_list(comments)

    def get_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all comments from all issues using GraphQL for better performance."""
        owner, name = self._parse_repo_name(repo_name)
        all_comments = []
        cursor = None

        while True:
            result = self._gql_client.execute(
                REPOSITORY_COMMENTS_QUERY,
                variable_values={
                    "owner": owner,
                    "name": name,
                    "first": 100,
                    "after": cursor,
                },
            )

            issues_data = result["repository"]["issues"]

            for issue in issues_data["nodes"]:
                for comment in issue["comments"]["nodes"]:
                    comment["issue_url"] = issue["url"]
                    all_comments.append(comment)

            if not issues_data["pageInfo"]["hasNextPage"]:
                break
            cursor = issues_data["pageInfo"]["endCursor"]

        return convert_graphql_comments_to_rest_format(all_comments)

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
        """Get current rate limit status using GraphQL."""
        result = self._gql_client.execute(RATE_LIMIT_QUERY)
        rate_limit_data = result["rateLimit"]

        rate_limit_response = {
            "core": {
                "limit": rate_limit_data["limit"],
                "remaining": rate_limit_data["remaining"],
                "reset": rate_limit_data["resetAt"],
            }
        }
        return convert_graphql_rate_limit_to_rest_format(rate_limit_response)

    # GraphQL Utility Methods

    def _parse_repo_name(self, repo_name: str) -> tuple[str, str]:
        """Parse owner/repo format into separate components."""
        if "/" not in repo_name:
            raise ValueError(
                f"Repository name must be in 'owner/repo' format, got: {repo_name}"
            )

        owner, name = repo_name.split("/", 1)
        return owner, name

    # Low-level Repository Operations

    def _get_repository(self, repo_name: str) -> Repository:
        """Get repository object from GitHub API."""
        return self._github.get_repo(repo_name)

    # Public API - Pull Request Operations

    def get_repository_pull_requests(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull requests from repository using GraphQL for performance."""
        owner, name = self._parse_repo_name(repo_name)
        all_prs = []
        cursor = None

        while True:
            result = self._gql_client.execute(
                REPOSITORY_PULL_REQUESTS_QUERY,
                variable_values={
                    "owner": owner,
                    "name": name,
                    "first": 100,
                    "after": cursor,
                },
            )

            prs_data = result["repository"]["pullRequests"]
            all_prs.extend(prs_data["nodes"])

            if not prs_data["pageInfo"]["hasNextPage"]:
                break
            cursor = prs_data["pageInfo"]["endCursor"]

        return convert_graphql_pull_requests_to_rest_format(all_prs, repo_name)

    def get_pull_request_comments(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request using GraphQL."""
        owner, name = self._parse_repo_name(repo_name)
        all_comments = []
        cursor = None

        while True:
            result = self._gql_client.execute(
                PULL_REQUEST_COMMENTS_QUERY,
                variable_values={
                    "owner": owner,
                    "name": name,
                    "prNumber": pr_number,
                    "first": 100,
                    "after": cursor,
                },
            )

            pr_data = result["repository"]["pullRequest"]
            if not pr_data:
                break

            comments_data = pr_data["comments"]
            for comment in comments_data["nodes"]:
                comment["pull_request_url"] = pr_data["url"]
                all_comments.append(comment)

            if not comments_data["pageInfo"]["hasNextPage"]:
                break
            cursor = comments_data["pageInfo"]["endCursor"]

        return convert_graphql_pr_comments_to_rest_format(all_comments)

    def get_all_pull_request_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all comments from all pull requests using GraphQL for performance."""
        owner, name = self._parse_repo_name(repo_name)
        all_comments = []
        cursor = None

        while True:
            result = self._gql_client.execute(
                REPOSITORY_PR_COMMENTS_QUERY,
                variable_values={
                    "owner": owner,
                    "name": name,
                    "first": 100,
                    "after": cursor,
                },
            )

            prs_data = result["repository"]["pullRequests"]

            for pr in prs_data["nodes"]:
                for comment in pr["comments"]["nodes"]:
                    comment["pull_request_url"] = pr["url"]
                    all_comments.append(comment)

            if not prs_data["pageInfo"]["hasNextPage"]:
                break
            cursor = prs_data["pageInfo"]["endCursor"]

        return convert_graphql_pr_comments_to_rest_format(all_comments)

    def create_pull_request(
        self, repo_name: str, title: str, body: str, head: str, base: str
    ) -> Dict[str, Any]:
        """Create a new pull request and return raw JSON data."""
        repo = self._get_repository(repo_name)
        created_pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return self._extract_raw_data(created_pr)

    def create_pull_request_comment(
        self, repo_name: str, pr_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment on a pull request and return raw JSON data."""
        repo = self._get_repository(repo_name)
        pr = repo.get_pull(pr_number)
        created_comment = pr.create_issue_comment(body)
        return self._extract_raw_data(created_comment)

    # Raw Data Extraction Utilities (for REST write operations)

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
