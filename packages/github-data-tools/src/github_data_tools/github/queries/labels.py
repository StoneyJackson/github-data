"""
GraphQL queries for repository label operations.

Provides optimized queries for fetching repository labels.
"""

from gql import gql

# Repository labels only (for label-only backup operations)
REPOSITORY_LABELS_QUERY = gql(
    """
    query getRepositoryLabels($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            labels(first: 100) {
                nodes {
                    id
                    name
                    color
                    description
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
    }
"""
)
