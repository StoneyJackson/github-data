"""
Data converters for GitHub API responses.

Converts raw JSON data from GitHub API to our domain models.
"""

from typing import Dict, Any
from datetime import datetime

from ..models import (
    Label,
    Issue,
    Comment,
    GitHubUser,
    PullRequest,
    PullRequestComment,
    SubIssue,
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


def _parse_datetime(datetime_str: str) -> datetime:
    """Parse GitHub API datetime string to datetime object."""
    return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
