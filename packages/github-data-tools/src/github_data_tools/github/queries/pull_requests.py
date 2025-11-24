"""
GraphQL queries for repository pull request operations.

Provides optimized queries for fetching pull requests and their comments.
"""

from gql import gql

# Repository pull requests (for PR-only backup operations)
REPOSITORY_PULL_REQUESTS_QUERY = gql(
    """
    query getRepositoryPullRequests(
        $owner: String!,
        $name: String!,
        $first: Int!,
        $after: String
    ) {
        repository(owner: $owner, name: $name) {
            pullRequests(
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
                    url
                    createdAt
                    updatedAt
                    closedAt
                    mergedAt
                    mergeCommit {
                        oid
                    }
                    baseRef {
                        name
                    }
                    headRef {
                        name
                    }
                    author {
                        login
                        ... on User {
                            id
                            avatarUrl
                            url
                        }
                    }
                    assignees(first: 20) {
                        nodes {
                            login
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
                        creator {
                            login
                            ... on User {
                                id
                                avatarUrl
                                url
                            }
                        }
                        createdAt
                        updatedAt
                        dueOn
                        closedAt
                        url
                    }
                    comments {
                        totalCount
                    }
                    reviews(first: 10) {
                        nodes {
                            id
                            author {
                                login
                                ... on User {
                                    id
                                    avatarUrl
                                    url
                                }
                            }
                            body
                            state
                            submittedAt
                            authorAssociation
                            url
                            comments(first: 10) {
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
                                    diffHunk
                                    path
                                    line
                                    url
                                }
                            }
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

# Pull request comments for a specific PR
PULL_REQUEST_COMMENTS_QUERY = gql(
    """
    query getPullRequestComments(
        $owner: String!,
        $name: String!,
        $prNumber: Int!,
        $first: Int!,
        $after: String
    ) {
        repository(owner: $owner, name: $name) {
            pullRequest(number: $prNumber) {
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
                url
            }
        }
    }
"""
)

# All pull request comments across repository
REPOSITORY_PR_COMMENTS_QUERY = gql(
    """
    query getRepositoryPRComments(
        $owner: String!,
        $name: String!,
        $first: Int!,
        $after: String
    ) {
        repository(owner: $owner, name: $name) {
            pullRequests(
                first: $first,
                after: $after,
                orderBy: {field: CREATED_AT, direction: ASC}
            ) {
                nodes {
                    number
                    url
                    comments(
                        first: 10,
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
