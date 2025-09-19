"""GraphQL and REST queries for labels."""

from typing import Dict
from ...shared.queries.base_queries import BaseQueries


class LabelQueries(BaseQueries):
    """GitHub API queries for labels."""

    def get_graphql_query(self) -> str:
        """GraphQL query for bulk label retrieval."""
        return """
        query GetRepositoryLabels($owner: String!, $name: String!, $cursor: String) {
            repository(owner: $owner, name: $name) {
                labels(first: 100, after: $cursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        id
                        name
                        color
                        description
                        url
                    }
                }
            }
        }
        """

    def get_rest_endpoints(self) -> Dict[str, str]:
        """REST API endpoints for label operations."""
        return {
            "list": "/repos/{owner}/{repo}/labels",
            "create": "/repos/{owner}/{repo}/labels",
            "update": "/repos/{owner}/{repo}/labels/{name}",
            "delete": "/repos/{owner}/{repo}/labels/{name}",
        }
