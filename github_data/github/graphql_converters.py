"""
Converters for GraphQL response data to match existing data models.

Transforms GraphQL response structures to be compatible with
the existing REST-based data processing pipeline.
"""

from typing import Dict, List, Any
from .converter_registry import get_converter


def convert_graphql_labels_to_rest_format(
    graphql_labels: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Convert GraphQL label nodes to REST API format."""
    return [
        {
            "id": label["id"],
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
                "id": label["id"],
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
                "id": issue["author"].get("id"),
                "avatar_url": issue["author"].get("avatarUrl"),
                "html_url": issue["author"].get("url"),
            }

        # Convert milestone - keep as dict for entity converter to handle
        milestone = None
        if issue.get("milestone"):
            milestone = issue["milestone"]

        rest_issue = {
            "id": issue["id"],
            "number": issue["number"],
            "title": issue["title"],
            "body": issue.get("body"),
            "state": issue["state"].lower(),
            "state_reason": issue.get("stateReason"),
            "html_url": issue["url"],
            "created_at": issue["createdAt"],
            "updated_at": issue["updatedAt"],
            "user": author,
            "author_association": "NONE",  # Not provided in basic GraphQL query
            "labels": labels,
            "assignee": None,  # Not requested in current query
            "assignees": [],  # Not requested in current query
            "milestone": milestone,
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
                "id": comment["author"].get("id"),
                "avatar_url": comment["author"].get("avatarUrl"),
                "html_url": comment["author"].get("url"),
            }

        rest_comment = {
            "id": comment["id"],
            "body": comment["body"],
            "created_at": comment["createdAt"],
            "updated_at": comment["updatedAt"],
            "html_url": comment["url"],
            "user": author,
            "author_association": "NONE",  # Not provided in basic GraphQL query
            "issue_url": comment.get("issue_url"),  # Added by our processing
        }
        rest_comments.append(rest_comment)

    return rest_comments


def convert_graphql_pull_requests_to_rest_format(
    graphql_prs: List[Dict[str, Any]], repo_name: str
) -> List[Dict[str, Any]]:
    """Convert GraphQL pull request nodes to REST API format."""
    owner, name = repo_name.split("/", 1)

    rest_prs = []
    for pr in graphql_prs:
        # Convert labels
        labels = [
            {
                "id": label["id"],
                "name": label["name"],
                "color": label["color"],
                "description": label["description"],
                "url": f"https://api.github.com/repos/{repo_name}/labels/"
                f"{label['name']}",
                "default": False,
            }
            for label in pr.get("labels", {}).get("nodes", [])
        ]

        # Convert author
        author = None
        if pr.get("author"):
            author = {
                "login": pr["author"]["login"],
                "id": pr["author"].get("id"),
                "avatar_url": pr["author"].get("avatarUrl"),
                "html_url": pr["author"].get("url"),
            }

        # Convert assignees
        assignees = [
            {
                "login": assignee["login"],
                "id": assignee.get("id"),
                "avatar_url": assignee.get("avatarUrl"),
                "html_url": assignee.get("url"),
            }
            for assignee in pr.get("assignees", {}).get("nodes", [])
        ]

        # Convert milestone - keep as dict for entity converter to handle
        milestone = None
        if pr.get("milestone"):
            milestone = pr["milestone"]

        # Extract merge commit SHA
        merge_commit_sha = None
        if pr.get("mergeCommit"):
            merge_commit_sha = pr["mergeCommit"]["oid"]

        # Extract branch references
        base_ref = pr.get("baseRef", {}).get("name") if pr.get("baseRef") else None
        head_ref = pr.get("headRef", {}).get("name") if pr.get("headRef") else None

        # Extract comment count
        comments_count = pr.get("comments", {}).get("totalCount", 0)

        rest_pr = {
            "id": pr["id"],
            "number": pr["number"],
            "title": pr["title"],
            "body": pr.get("body"),
            "state": pr["state"].upper(),
            "html_url": pr["url"],
            "created_at": pr["createdAt"],
            "updated_at": pr["updatedAt"],
            "closed_at": pr.get("closedAt"),
            "merged_at": pr.get("mergedAt"),
            "merge_commit_sha": merge_commit_sha,
            "base_ref": base_ref,
            "head_ref": head_ref,
            "user": author,
            "assignees": assignees,
            "labels": labels,
            "milestone": milestone,
            "comments": comments_count,
        }
        rest_prs.append(rest_pr)

    return rest_prs


def convert_graphql_pr_comments_to_rest_format(
    graphql_comments: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Convert GraphQL PR comment nodes to REST API format."""
    rest_comments = []

    for comment in graphql_comments:
        # Convert author
        author = None
        if comment.get("author"):
            author = {
                "login": comment["author"]["login"],
                "id": comment["author"].get("id"),
                "avatar_url": comment["author"].get("avatarUrl"),
                "html_url": comment["author"].get("url"),
            }

        rest_comment = {
            "id": comment["id"],
            "body": comment["body"],
            "created_at": comment["createdAt"],
            "updated_at": comment["updatedAt"],
            "html_url": comment["url"],
            "user": author,
            "author_association": "NONE",  # Not provided in basic GraphQL query
            "pull_request_url": comment.get(
                "pull_request_url"
            ),  # Added by our processing
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


def convert_graphql_pr_reviews_to_rest_format(
    graphql_reviews: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Convert GraphQL PR reviews data to REST API format."""
    rest_reviews = []

    for review in graphql_reviews:
        # Convert author
        author = None
        if review.get("author"):
            author = {
                "login": review["author"]["login"],
                "id": review["author"].get("id"),
                "avatar_url": review["author"].get("avatarUrl"),
                "html_url": review["author"].get("url"),
            }

        rest_review = {
            "id": review["id"],
            "body": review.get("body", ""),
            "state": review["state"],
            "submitted_at": review.get("submittedAt"),
            "author_association": review.get("authorAssociation", ""),
            "html_url": review["url"],
            "user": author,
            "pull_request_url": review.get("pullRequestUrl"),
            "pull_request_number": review.get("pullRequestNumber"),
        }
        rest_reviews.append(rest_review)

    return rest_reviews


def convert_graphql_review_comments_to_rest_format(
    graphql_comments: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Convert GraphQL review comments data to REST API format."""
    rest_comments = []

    for comment in graphql_comments:
        # Convert author
        author = None
        if comment.get("author"):
            author = {
                "login": comment["author"]["login"],
                "id": comment["author"].get("id"),
                "avatar_url": comment["author"].get("avatarUrl"),
                "html_url": comment["author"].get("url"),
            }

        rest_comment = {
            "id": comment["id"],
            "body": comment["body"],
            "created_at": comment["createdAt"],
            "updated_at": comment["updatedAt"],
            "diff_hunk": comment.get("diffHunk", ""),
            "path": comment.get("path", ""),
            "line": comment.get("line"),
            "html_url": comment["url"],
            "user": author,
            "review_id": comment.get("reviewId"),
            "pull_request_url": comment.get("pullRequestUrl"),
            "pull_request_number": comment.get("pullRequestNumber"),
        }
        rest_comments.append(rest_comment)

    return rest_comments
