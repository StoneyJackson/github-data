"""
GraphQL queries for repository issue operations.

Provides optimized queries for fetching repository issues and their comments.
"""

from gql import gql

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
                    milestone {
                        id
                        number
                        title
                        description
                        state
                        createdAt
                        updatedAt
                        dueOn
                        closedAt
                        url
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
        }
    }
"""
)
