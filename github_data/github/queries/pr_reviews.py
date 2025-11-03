"""
GraphQL queries for repository pull request reviews and review comments.

Provides optimized queries for fetching PR reviews and their comments.
"""

from gql import gql

# Pull request reviews for a specific PR
PULL_REQUEST_REVIEWS_QUERY = gql(
    """
    query getPullRequestReviews(
        $owner: String!,
        $name: String!,
        $prNumber: Int!,
        $first: Int!,
        $after: String
    ) {
        repository(owner: $owner, name: $name) {
            pullRequest(number: $prNumber) {
                reviews(
                    first: $first,
                    after: $after
                ) {
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

# All pull request reviews across repository
REPOSITORY_PR_REVIEWS_QUERY = gql(
    """
    query getRepositoryPRReviews(
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
                    reviews(
                        first: 100
                    ) {
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
                            comments(first: 100) {
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

# Review comments for a specific review
REVIEW_COMMENTS_QUERY = gql(
    """
    query getReviewComments(
        $owner: String!,
        $name: String!,
        $prNumber: Int!,
        $reviewId: ID!,
        $first: Int!,
        $after: String
    ) {
        repository(owner: $owner, name: $name) {
            pullRequest(number: $prNumber) {
                review(id: $reviewId) {
                    comments(
                        first: $first,
                        after: $after
                    ) {
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
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
                url
            }
        }
    }
"""
)

# All review comments across repository
REPOSITORY_REVIEW_COMMENTS_QUERY = gql(
    """
    query getRepositoryReviewComments(
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
                    reviews(first: 10) {
                        nodes {
                            id
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
