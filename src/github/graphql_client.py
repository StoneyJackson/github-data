"""
GitHub GraphQL client.

Handles all GraphQL operations for GitHub API interactions.
Provides methods for querying labels, issues, comments, pull requests,
sub-issues, and rate limits using GraphQL for better performance.
"""

from typing import Dict, List, Any
from .utils.graphql_paginator import GraphQLPaginator
from .utils.data_enrichment import CommentEnricher, SubIssueRelationshipBuilder

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
    REPOSITORY_SUB_ISSUES_QUERY,
    ISSUE_SUB_ISSUES_QUERY,
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


class GitHubGraphQLClient:
    """
    GitHub GraphQL client for efficient API operations.

    Provides GraphQL-based methods for retrieving repository data
    with better performance than REST API for bulk operations.
    """

    def __init__(self, token: str):
        """
        Initialize GraphQL client with authentication.

        Args:
            token: GitHub authentication token
        """
        self._gql_client = self._create_graphql_client(token)

    def _create_graphql_client(self, token: str) -> Client:
        """Create and configure GraphQL client for GitHub API."""
        transport = RequestsHTTPTransport(
            url="https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {token}"},
        )
        return Client(transport=transport, fetch_schema_from_transport=True)

    def _parse_repo_name(self, repo_name: str) -> tuple[str, str]:
        """Parse owner/repo format into separate components."""
        if "/" not in repo_name:
            raise ValueError(
                f"Repository name must be in 'owner/repo' format, got: {repo_name}"
            )

        owner, name = repo_name.split("/", 1)
        return owner, name

    # Repository Data Operations

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

        paginator = GraphQLPaginator(self._gql_client)
        all_issues = paginator.paginate_all(
            query=REPOSITORY_ISSUES_QUERY,
            variable_values={"owner": owner, "name": name},
            data_path="repository.issues",
        )

        return convert_graphql_issues_to_rest_format(all_issues, repo_name)

    def get_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all comments from all issues using GraphQL for better performance."""
        owner, name = self._parse_repo_name(repo_name)

        def comment_post_processor(
            issues_nodes: List[Dict[str, Any]],
        ) -> List[Dict[str, Any]]:
            """Post-process comments by adding issue URL and flattening."""
            all_comments = []
            for issue in issues_nodes:
                comments = CommentEnricher.enrich_issue_comments(
                    issue["comments"]["nodes"], issue["url"]
                )
                all_comments.extend(comments)
            return all_comments

        paginator = GraphQLPaginator(self._gql_client)
        all_comments = paginator.paginate_all(
            query=REPOSITORY_COMMENTS_QUERY,
            variable_values={"owner": owner, "name": name},
            data_path="repository.issues",
            post_processor=comment_post_processor,
        )

        return convert_graphql_comments_to_rest_format(all_comments)

    # Pull Request Operations

    def get_repository_pull_requests(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull requests from repository using GraphQL for performance."""
        owner, name = self._parse_repo_name(repo_name)

        paginator = GraphQLPaginator(self._gql_client)
        all_prs = paginator.paginate_all(
            query=REPOSITORY_PULL_REQUESTS_QUERY,
            variable_values={"owner": owner, "name": name},
            data_path="repository.pullRequests",
        )

        return convert_graphql_pull_requests_to_rest_format(all_prs, repo_name)

    def get_pull_request_comments(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request using GraphQL."""
        owner, name = self._parse_repo_name(repo_name)

        def comment_post_processor(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """Post-process comments to add pull request URL."""
            pr_data = self._gql_client.execute(
                PULL_REQUEST_COMMENTS_QUERY,
                variable_values={
                    "owner": owner,
                    "name": name,
                    "prNumber": pr_number,
                    "first": 1,  # Only needed to get the PR URL
                    "after": None,
                },
            )["repository"]["pullRequest"]

            if not pr_data:
                return []

            pull_request_url = pr_data["url"]
            return CommentEnricher.enrich_pr_comments(nodes, pull_request_url)

        paginator = GraphQLPaginator(self._gql_client)
        all_comments = paginator.paginate_all(
            query=PULL_REQUEST_COMMENTS_QUERY,
            variable_values={
                "owner": owner,
                "name": name,
                "prNumber": pr_number,
            },
            data_path="repository.pullRequest.comments",
            post_processor=comment_post_processor,
        )

        return convert_graphql_pr_comments_to_rest_format(all_comments)

    def get_all_pull_request_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all comments from all pull requests using GraphQL for performance."""
        owner, name = self._parse_repo_name(repo_name)

        def comment_post_processor(
            prs_nodes: List[Dict[str, Any]],
        ) -> List[Dict[str, Any]]:
            """Post-process comments by adding pull request URL and flattening."""
            all_comments = []
            for pr in prs_nodes:
                comments = CommentEnricher.enrich_pr_comments(
                    pr["comments"]["nodes"], pr["url"]
                )
                all_comments.extend(comments)
            return all_comments

        paginator = GraphQLPaginator(self._gql_client)
        all_comments = paginator.paginate_all(
            query=REPOSITORY_PR_COMMENTS_QUERY,
            variable_values={"owner": owner, "name": name},
            data_path="repository.pullRequests",
            post_processor=comment_post_processor,
        )

        return convert_graphql_pr_comments_to_rest_format(all_comments)

    # Sub-Issues Operations

    def get_repository_sub_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all sub-issue relationships from repository using GraphQL."""
        owner, name = self._parse_repo_name(repo_name)

        def sub_issues_post_processor(
            issues_nodes: List[Dict[str, Any]],
        ) -> List[Dict[str, Any]]:
            """Post-process sub-issues by extracting relationship data."""
            return SubIssueRelationshipBuilder.build_repository_relationships(
                issues_nodes
            )

        paginator = GraphQLPaginator(self._gql_client)
        all_sub_issues = paginator.paginate_all(
            query=REPOSITORY_SUB_ISSUES_QUERY,
            variable_values={"owner": owner, "name": name},
            data_path="repository.issues",
            post_processor=sub_issues_post_processor,
        )

        return all_sub_issues

    def get_issue_sub_issues_graphql(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get sub-issues for a specific issue using GraphQL."""
        owner, name = self._parse_repo_name(repo_name)

        def sub_issues_post_processor(
            sub_issues_nodes: List[Dict[str, Any]],
        ) -> List[Dict[str, Any]]:
            """Post-process sub-issues with additional metadata."""
            # First, get the parent issue details to enrich sub-issues
            result = self._gql_client.execute(
                ISSUE_SUB_ISSUES_QUERY,
                variable_values={
                    "owner": owner,
                    "name": name,
                    "issueNumber": issue_number,
                    "first": 1,  # We just need the parent issue details
                },
            )

            issue_data = result["repository"]["issue"]
            if not issue_data:
                return []

            # Enrich each sub-issue with parent issue details
            return SubIssueRelationshipBuilder.build_issue_relationships(
                sub_issues_nodes, issue_data
            )

        paginator = GraphQLPaginator(self._gql_client)
        all_sub_issues = paginator.paginate_all(
            query=ISSUE_SUB_ISSUES_QUERY,
            variable_values={
                "owner": owner,
                "name": name,
                "issueNumber": issue_number,
            },
            data_path="repository.issue.subIssues",
            post_processor=sub_issues_post_processor,
        )

        return all_sub_issues

    # Rate Limit Monitoring

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
