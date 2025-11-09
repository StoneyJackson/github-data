# github_data/entities/pull_requests/converters.py
"""Converters for pull requests entity."""

from typing import Dict, Any
from .models import PullRequest
from github_data.github.converter_registry import get_converter
from github_data.github.converters import _parse_datetime


def convert_to_pull_request(raw_data: Dict[str, Any]) -> PullRequest:
    """
    Convert raw GitHub API pull request data to PullRequest model.

    Args:
        raw_data: Raw pull request data from GitHub API

    Returns:
        PullRequest domain model
    """
    # Use registry for all nested conversions
    labels = [
        get_converter("convert_to_label")(label) for label in raw_data.get("labels", [])
    ]

    milestone = None
    if raw_data.get("milestone"):
        milestone = get_converter("convert_to_milestone")(raw_data["milestone"])

    user = get_converter("convert_to_user")(raw_data["user"])

    assignees = [
        get_converter("convert_to_user")(assignee)
        for assignee in raw_data.get("assignees", [])
    ]

    return PullRequest(
        id=raw_data["id"],
        number=raw_data["number"],
        title=raw_data["title"],
        body=raw_data.get("body"),
        state=raw_data["state"],
        user=user,
        assignees=assignees,
        labels=labels,
        milestone=milestone,
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
