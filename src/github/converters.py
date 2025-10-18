"""
Data converters for GitHub API responses.

Converts raw JSON data from GitHub API to our domain models.
"""

from typing import Dict, Any
from datetime import datetime

from ..entities import (
    Label,
    Issue,
    Comment,
    GitHubUser,
    PullRequest,
    PullRequestComment,
    PullRequestReview,
    PullRequestReviewComment,
    SubIssue,
    Milestone,
)


def convert_to_label(raw_data: Dict[str, Any]) -> Label:
    """Convert raw GitHub API label data to Label model."""
    return Label(
        name=raw_data["name"],
        color=raw_data["color"],
        description=raw_data.get("description"),
        url=raw_data["url"],
        id=raw_data["id"],
    )


def convert_to_issue(raw_data: Dict[str, Any]) -> Issue:
    """Convert raw GitHub API issue data to Issue model."""
    return Issue(
        id=raw_data["id"],
        number=raw_data["number"],
        title=raw_data["title"],
        body=raw_data.get("body"),
        state=raw_data["state"],
        user=convert_to_user(raw_data["user"]),
        assignees=[
            convert_to_user(assignee) for assignee in raw_data.get("assignees", [])
        ],
        labels=[convert_to_label(label) for label in raw_data.get("labels", [])],
        milestone=(
            convert_to_milestone(raw_data["milestone"])
            if raw_data.get("milestone")
            else None
        ),
        created_at=_parse_datetime(raw_data["created_at"]),
        updated_at=_parse_datetime(raw_data["updated_at"]),
        closed_at=(
            _parse_datetime(raw_data["closed_at"])
            if raw_data.get("closed_at")
            else None
        ),
        html_url=raw_data["html_url"],
        comments=raw_data.get("comments", 0),
    )


def convert_to_comment(raw_data: Dict[str, Any]) -> Comment:
    """Convert raw GitHub API comment data to Comment model."""
    return Comment(
        id=raw_data["id"],
        body=raw_data["body"],
        user=convert_to_user(raw_data["user"]),
        created_at=_parse_datetime(raw_data["created_at"]),
        updated_at=_parse_datetime(raw_data["updated_at"]),
        html_url=raw_data["html_url"],
        issue_url=raw_data["issue_url"],
    )


def convert_to_pull_request(raw_data: Dict[str, Any]) -> PullRequest:
    """Convert raw GitHub API pull request data to PullRequest model."""
    return PullRequest(
        id=raw_data["id"],
        number=raw_data["number"],
        title=raw_data["title"],
        body=raw_data.get("body"),
        state=raw_data["state"],
        user=convert_to_user(raw_data["user"]),
        assignees=[
            convert_to_user(assignee) for assignee in raw_data.get("assignees", [])
        ],
        labels=[convert_to_label(label) for label in raw_data.get("labels", [])],
        milestone=(
            convert_to_milestone(raw_data["milestone"])
            if raw_data.get("milestone")
            else None
        ),
        created_at=_parse_datetime(raw_data["created_at"]),
        updated_at=_parse_datetime(raw_data["updated_at"]),
        closed_at=(
            _parse_datetime(raw_data["closed_at"])
            if raw_data.get("closed_at")
            else None
        ),
        merged_at=(
            _parse_datetime(raw_data["merged_at"])
            if raw_data.get("merged_at")
            else None
        ),
        merge_commit_sha=raw_data.get("merge_commit_sha"),
        base_ref=raw_data.get("base_ref", ""),
        head_ref=raw_data.get("head_ref", ""),
        html_url=raw_data["html_url"],
        comments=raw_data.get("comments", 0),
    )


def convert_to_pr_comment(raw_data: Dict[str, Any]) -> PullRequestComment:
    """Convert raw GitHub API PR comment data to PullRequestComment model."""
    return PullRequestComment(
        id=raw_data["id"],
        body=raw_data["body"],
        user=convert_to_user(raw_data["user"]),
        created_at=_parse_datetime(raw_data["created_at"]),
        updated_at=_parse_datetime(raw_data["updated_at"]),
        html_url=raw_data["html_url"],
        pull_request_url=raw_data["pull_request_url"],
    )


def convert_to_user(raw_data: Dict[str, Any]) -> GitHubUser:
    """Convert raw GitHub API user data to GitHubUser model."""
    return GitHubUser(
        login=raw_data["login"],
        id=raw_data["id"],
        avatar_url=raw_data["avatar_url"],
        html_url=raw_data["html_url"],
    )


def convert_to_sub_issue(raw_data: Dict[str, Any]) -> SubIssue:
    """Convert raw GitHub API sub-issue data to SubIssue model."""
    return SubIssue(
        sub_issue_id=raw_data["sub_issue_id"],
        sub_issue_number=raw_data["sub_issue_number"],
        parent_issue_id=raw_data["parent_issue_id"],
        parent_issue_number=raw_data["parent_issue_number"],
        position=raw_data["position"],
    )


def convert_to_pr_review(api_data: Dict[str, Any]) -> PullRequestReview:
    """Convert GitHub API review data to PullRequestReview model."""
    return PullRequestReview(
        id=api_data["id"],
        pr_number=_extract_pr_number_from_url(api_data.get("pull_request_url", "")),
        user=convert_to_user(api_data["user"]),
        body=api_data.get("body", ""),
        state=api_data["state"],
        html_url=api_data["html_url"],
        pull_request_url=api_data.get("pull_request_url", ""),
        author_association=api_data.get("author_association", ""),
        submitted_at=(
            _parse_datetime(api_data["submitted_at"])
            if api_data.get("submitted_at")
            else None
        ),
        commit_id=api_data.get("commit_id"),
    )


def convert_to_pr_review_comment(api_data: Dict[str, Any]) -> PullRequestReviewComment:
    """Convert GitHub API review comment data to PullRequestReviewComment model."""
    return PullRequestReviewComment(
        id=api_data["id"],
        review_id=api_data.get("review_id", ""),
        pr_number=_extract_pr_number_from_url(api_data.get("pull_request_url", "")),
        diff_hunk=api_data.get("diff_hunk", ""),
        path=api_data.get("path", ""),
        line=api_data.get("line"),
        body=api_data["body"],
        user=convert_to_user(api_data["user"]),
        created_at=_parse_datetime(api_data["created_at"]),
        updated_at=_parse_datetime(api_data["updated_at"]),
        html_url=api_data["html_url"],
        pull_request_url=api_data.get("pull_request_url", ""),
        in_reply_to_id=api_data.get("in_reply_to_id"),
    )


def convert_to_milestone(raw_data: Dict[str, Any]) -> Milestone:
    """Convert raw GitHub API milestone data to Milestone model."""
    # Handle GraphQL vs REST API differences
    issues_count = raw_data.get("issues", {})
    if isinstance(issues_count, dict):
        # GraphQL format
        open_issues = issues_count.get("totalCount", 0)
        closed_issues = 0  # GraphQL doesn't provide this directly
    else:
        # REST API format
        open_issues = raw_data.get("open_issues", 0)
        closed_issues = raw_data.get("closed_issues", 0)

    return Milestone(
        id=raw_data["id"],
        number=raw_data["number"],
        title=raw_data["title"],
        description=raw_data.get("description"),
        state=raw_data["state"].lower(),
        creator=convert_to_user(raw_data["creator"]),
        created_at=_parse_datetime(
            raw_data.get("createdAt") or raw_data.get("created_at") or ""
        ),
        updated_at=_parse_datetime(
            raw_data.get("updatedAt") or raw_data.get("updated_at") or ""
        ),
        due_on=(
            _parse_datetime(raw_data.get("dueOn") or raw_data.get("due_on") or "")
            if raw_data.get("dueOn") or raw_data.get("due_on")
            else None
        ),
        closed_at=(
            _parse_datetime(raw_data.get("closedAt") or raw_data.get("closed_at") or "")
            if raw_data.get("closedAt") or raw_data.get("closed_at")
            else None
        ),
        open_issues=open_issues,
        closed_issues=closed_issues,
        html_url=raw_data.get("url") or raw_data.get("html_url") or "",
    )


def _extract_pr_number_from_url(url: str) -> int:
    """Extract PR number from GitHub URL."""
    if not url:
        return 0
    try:
        # URL format: https://github.com/owner/repo/pull/123
        # or: https://api.github.com/repos/owner/repo/pulls/123
        parts = url.rstrip("/").split("/")
        return int(parts[-1])
    except (ValueError, IndexError):
        return 0


def _parse_datetime(datetime_str: str) -> datetime:
    """Parse GitHub API datetime string to datetime object."""
    return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
