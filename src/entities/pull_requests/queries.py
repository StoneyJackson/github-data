"""GraphQL and REST queries for pull requests."""

from typing import Dict
from ...shared.queries.base_queries import BaseQueries


class PullRequestQueries(BaseQueries):
    """GitHub API queries for pull requests."""

    def get_graphql_query(self) -> str:
        """GraphQL query for bulk PR retrieval."""
        return """
        query GetRepositoryPullRequests(
            $owner: String!, $name: String!, $cursor: String
        ) {
            repository(owner: $owner, name: $name) {
                pullRequests(
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
                        mergedAt
                        mergeCommit {
                            oid
                        }
                        baseRefName
                        headRefName
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
        """REST API endpoints for PR operations."""
        return {
            "list": "/repos/{owner}/{repo}/pulls",
            "create": "/repos/{owner}/{repo}/pulls",
            "update": "/repos/{owner}/{repo}/pulls/{number}",
            "get": "/repos/{owner}/{repo}/pulls/{number}",
        }
