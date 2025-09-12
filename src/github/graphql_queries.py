"""
GraphQL query definitions for GitHub API operations.

Provides optimized queries for backup operations that fetch
repository data in single requests instead of multiple REST calls.
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
                    }
                    labels(first: 20) {
                        nodes {
                            name
                            color
                            description
                        }
                    }
                    comments(
                        first: $commentsFirst,
                        orderBy: {field: CREATED_AT, direction: ASC}
                    ) {
                        nodes {
                            body
                            createdAt
                            updatedAt
                            url
                            author {
                                login
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

# Repository labels only (for label-only backup operations)
REPOSITORY_LABELS_QUERY = gql(
    """
    query getRepositoryLabels($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            labels(first: 100) {
                nodes {
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

# Repository issues with labels (for issue-only backup operations)
REPOSITORY_ISSUES_QUERY = gql(
    """
    query getRepositoryIssues(
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
                    title
                    body
                    state
                    stateReason
                    url
                    createdAt
                    updatedAt
                    author {
                        login
                    }
                    labels(first: 20) {
                        nodes {
                            name
                            color
                            description
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

# Issue comments for a specific issue
ISSUE_COMMENTS_QUERY = gql(
    """
    query getIssueComments(
        $owner: String!,
        $name: String!,
        $issueNumber: Int!,
        $first: Int!,
        $after: String
    ) {
        repository(owner: $owner, name: $name) {
            issue(number: $issueNumber) {
                comments(
                    first: $first,
                    after: $after,
                    orderBy: {field: CREATED_AT, direction: ASC}
                ) {
                    nodes {
                        body
                        createdAt
                        updatedAt
                        url
                        author {
                            login
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
    }
"""
)

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
                        orderBy: {field: CREATED_AT, direction: ASC}
                    ) {
                        nodes {
                            body
                            createdAt
                            updatedAt
                            url
                            author {
                                login
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
