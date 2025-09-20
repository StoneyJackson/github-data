"""
GraphQL queries for repository comment operations.

Provides optimized queries for fetching all comments across a repository.
"""

from gql import gql

# All issue comments across repository
REPOSITORY_COMMENTS_QUERY = gql(
    """
    query getRepositoryComments(
        $owner: String!,
        $name: String!,
        $first: Int!,
        $after: String
    ) {
        repository(owner: $owner, name: $name) {
            issues(
                first: $first,
                after: $after,
                orderBy: {field: CREATED_AT, direction: ASC}
            ) {
                nodes {
                    number
                    url
                    comments(
                        first: 100,
                        orderBy: {field: UPDATED_AT, direction: ASC}
                    ) {
                        nodes {
                            id
                            body
                            createdAt
                            updatedAt
                            url
                            author {
                                login
                                ... on User {
                                    id
                                    avatarUrl
                                    url
                                }
                            }
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
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
