"""
GraphQL queries for utility operations.

Provides queries for backup operations and rate limit monitoring.
"""

from gql import gql

# Repository with basic info, labels, and issues with comments
REPOSITORY_BACKUP_QUERY = gql(
    """
    query getRepositoryData(
        $owner: String!,
        $name: String!,
        $issuesFirst: Int!,
        $commentsFirst: Int!
    ) {
        repository(owner: $owner, name: $name) {
            name
            description
            url
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
            issues(
                first: $issuesFirst,
                orderBy: {field: CREATED_AT, direction: ASC}
            ) {
                nodes {
                    id
                    number
                    title
                    body
                    state
                    stateReason
                    url
                    createdAt
                    updatedAt
                    author {
                        login
                        ... on User {
                            id
                            avatarUrl
                            url
                        }
                    }
                    labels(first: 20) {
                        nodes {
                            id
                            name
                            color
                            description
                        }
                    }
                    comments(
                        first: $commentsFirst,
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

# Rate limit status query
RATE_LIMIT_QUERY = gql(
    """
    query {
        rateLimit {
            limit
            cost
            remaining
            resetAt
        }
    }
"""
)
