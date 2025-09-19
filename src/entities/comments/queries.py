"""GraphQL and REST queries for comments."""

from typing import Dict
from ...shared.queries.base_queries import BaseQueries


class CommentQueries(BaseQueries):
    """GitHub API queries for comments."""

    def get_graphql_query(self) -> str:
        """GraphQL query for bulk comment retrieval."""
        return """
        query GetRepositoryComments($owner: String!, $name: String!, $cursor: String) {
            repository(owner: $owner, name: $name) {
                issues(first: 100) {
                    nodes {
                        number
                        comments(first: 100, after: $cursor) {
                            pageInfo {
                                hasNextPage
                                endCursor
                            }
                            nodes {
                                id
                                body
                                author {
                                    login
                                    ... on User {
                                        id
                                        avatarUrl
                                        url
                                    }
                                }
                                createdAt
                                updatedAt
                                url
                            }
                        }
                    }
                }
            }
        }
        """

    def get_rest_endpoints(self) -> Dict[str, str]:
        """REST API endpoints for comment operations."""
        return {
            "list": "/repos/{owner}/{repo}/issues/comments",
            "create": "/repos/{owner}/{repo}/issues/{issue_number}/comments",
            "update": "/repos/{owner}/{repo}/issues/comments/{comment_id}",
            "delete": "/repos/{owner}/{repo}/issues/comments/{comment_id}",
        }
