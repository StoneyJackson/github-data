# github_data/entities/issues/converters.py
"""Converters for issues entity."""

from typing import Dict, Any
from .models import Issue
from github_data_tools.github.converter_registry import get_converter
from github_data_tools.github.converters import _parse_datetime


def convert_to_issue(raw_data: Dict[str, Any]) -> Issue:
    """
    Convert raw GitHub API issue data to Issue model.

    Args:
        raw_data: Raw issue data from GitHub API

    Returns:
        Issue domain model
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

    # Comments handled separately in save/restore workflows

    return Issue(
        id=raw_data["id"],
        number=raw_data["number"],
        title=raw_data["title"],
        body=raw_data.get("body"),
        state=raw_data["state"],
        labels=labels,
        assignees=assignees,
        milestone=milestone,
        comments=raw_data.get("comments", 0),  # Use alias name
        created_at=_parse_datetime(raw_data["created_at"]),
        updated_at=_parse_datetime(raw_data["updated_at"]),
        closed_at=(
            _parse_datetime(raw_data["closed_at"])
            if raw_data.get("closed_at")
            else None
        ),
        user=user,
        html_url=raw_data["html_url"],
    )
