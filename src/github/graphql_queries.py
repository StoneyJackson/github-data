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
                    comments {
                        totalCount
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

# Repository sub-issues query
REPOSITORY_SUB_ISSUES_QUERY = gql(
    """
    query getRepositorySubIssues(
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
                    subIssues(first: 100) {
                        nodes {
                            id
                            number
                            position
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                    parentIssue {
                        id
                        number
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

# Issue sub-issues query for specific issue
ISSUE_SUB_ISSUES_QUERY = gql(
    """
    query getIssueSubIssues(
        $owner: String!,
        $name: String!,
        $issueNumber: Int!,
        $first: Int!,
        $after: String
    ) {
        repository(owner: $owner, name: $name) {
            issue(number: $issueNumber) {
                id
                number
                subIssues(first: $first, after: $after) {
                    nodes {
                        id
                        number
                        position
                        title
                        state
                        url
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
                parentIssue {
                    id
                    number
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
