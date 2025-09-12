"""
Converters for GraphQL response data to match existing data models.

Transforms GraphQL response structures to be compatible with
the existing REST-based data processing pipeline.
"""

from typing import Dict, List, Any


def convert_graphql_labels_to_rest_format(
    graphql_labels: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Convert GraphQL label nodes to REST API format."""
    return [
        {
            "name": label["name"],
            "color": label["color"],
            "description": label["description"],
            "url": f"https://api.github.com/repos/owner/repo/labels/{label['name']}",
            "default": False,  # GraphQL doesn't provide default info easily
        }
        for label in graphql_labels
    ]


def convert_graphql_issues_to_rest_format(
    graphql_issues: List[Dict[str, Any]], repo_name: str
) -> List[Dict[str, Any]]:
    """Convert GraphQL issue nodes to REST API format."""
    owner, name = repo_name.split("/", 1)

    rest_issues = []
    for issue in graphql_issues:
        # Convert labels
        labels = [
            {
                "name": label["name"],
                "color": label["color"],
                "description": label["description"],
                "url": f"https://api.github.com/repos/{repo_name}/labels/"
                f"{label['name']}",
                "default": False,
            }
            for label in issue.get("labels", {}).get("nodes", [])
        ]

        # Convert author
        author = None
        if issue.get("author"):
            author = {
                "login": issue["author"]["login"],
                "id": None,  # GraphQL response doesn't include ID in this query
                "url": f"https://api.github.com/users/{issue['author']['login']}",
            }

        rest_issue = {
            "number": issue["number"],
            "title": issue["title"],
            "body": issue.get("body"),
            "state": issue["state"].lower(),
            "state_reason": issue.get("stateReason"),
            "url": issue["url"],
            "created_at": issue["createdAt"],
            "updated_at": issue["updatedAt"],
            "user": author,
            "author_association": "NONE",  # Not provided in basic GraphQL query
            "labels": labels,
            "assignee": None,  # Not requested in current query
            "assignees": [],  # Not requested in current query
            "milestone": None,  # Not requested in current query
            "comments": 0,  # Could be enhanced to include comment count
            "pull_request": None,  # Issues don't have pull_request field
        }
        rest_issues.append(rest_issue)

    return rest_issues


def convert_graphql_comments_to_rest_format(
    graphql_comments: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Convert GraphQL comment nodes to REST API format."""
    rest_comments = []

    for comment in graphql_comments:
        # Convert author
        author = None
        if comment.get("author"):
            author = {
                "login": comment["author"]["login"],
                "id": None,  # GraphQL response doesn't include ID in this query
                "url": f"https://api.github.com/users/{comment['author']['login']}",
            }

        rest_comment = {
            "id": None,  # Not provided in basic GraphQL query
            "body": comment["body"],
            "created_at": comment["createdAt"],
            "updated_at": comment["updatedAt"],
            "url": comment["url"],
            "user": author,
            "author_association": "NONE",  # Not provided in basic GraphQL query
            "issue_url": comment.get("issue_url"),  # Added by our processing
        }
        rest_comments.append(rest_comment)

    return rest_comments


def convert_graphql_rate_limit_to_rest_format(
    graphql_rate_limit: Dict[str, Any],
) -> Dict[str, Any]:
    """Convert GraphQL rate limit data to REST API format."""
    return {
        "core": {
            "limit": graphql_rate_limit["core"]["limit"],
            "remaining": graphql_rate_limit["core"]["remaining"],
            "reset": graphql_rate_limit["core"]["reset"],
        }
    }
