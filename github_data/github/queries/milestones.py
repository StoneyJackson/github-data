"""GraphQL queries for milestone operations."""

from typing import Optional

REPOSITORY_MILESTONES_QUERY = """
query getRepositoryMilestones($owner: String!, $name: String!, $after: String) {
  repository(owner: $owner, name: $name) {
    milestones(first: 100, after: $after) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
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
        issues {
          totalCount
        }
        pullRequests {
          totalCount
        }
        url
      }
    }
  }
}
"""


def build_milestones_query_variables(
    owner: str, name: str, after: Optional[str] = None
) -> dict:
    """Build variables for milestone GraphQL query."""
    variables = {
        "owner": owner,
        "name": name,
    }
    if after:
        variables["after"] = after

    return variables
