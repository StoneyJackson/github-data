"""
GraphQL queries for repository sub-issue operations.

Provides optimized queries for fetching sub-issue relationships and hierarchies.
"""

from gql import gql

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
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                    parent {
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
                        title
                        state
                        url
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
                parent {
                    id
                    number
                }
            }
        }
    }
"""
)
