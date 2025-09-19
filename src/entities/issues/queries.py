"""GraphQL and REST queries for issues."""

from typing import Dict
from ...shared.queries.base_queries import BaseQueries


class IssueQueries(BaseQueries):
    """GitHub API queries for issues."""

    def get_graphql_query(self) -> str:
        """GraphQL query for bulk issue retrieval."""
        return """
        query GetRepositoryIssues($owner: String!, $name: String!, $cursor: String) {
            repository(owner: $owner, name: $name) {
                issues(
                    first: 100,
                    after: $cursor,
                    orderBy: {field: CREATED_AT, direction: ASC}
                ) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        id
                        number
                        title
                        body
                        state
                        author {
                            login
                            ... on User {
                                id
                                avatarUrl
                                url
                            }
                        }
                        assignees(first: 100) {
                            nodes {
                                login
                                id
                                avatarUrl
                                url
                            }
                        }
                        labels(first: 100) {
                            nodes {
                                id
                                name
                                color
                                description
                                url
                            }
                        }
                        createdAt
                        updatedAt
                        closedAt
                        closedBy {
                            login
                            ... on User {
                                id
                                avatarUrl
                                url
                            }
                        }
                        stateReason
                        url
                        comments {
                            totalCount
                        }
                    }
                }
            }
        }
        """

    def get_rest_endpoints(self) -> Dict[str, str]:
        """REST API endpoints for issue operations."""
        return {
            "list": "/repos/{owner}/{repo}/issues",
            "create": "/repos/{owner}/{repo}/issues",
            "update": "/repos/{owner}/{repo}/issues/{number}",
            "get": "/repos/{owner}/{repo}/issues/{number}",
        }

    def get_sub_issue_query(self) -> str:
        """GraphQL query for sub-issue relationships via issue body parsing."""
        return """
        query GetIssueBody($owner: String!, $name: String!, $number: Int!) {
            repository(owner: $owner, name: $name) {
                issue(number: $number) {
                    id
                    number
                    body
                }
            }
        }
        """
