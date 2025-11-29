# github_data/entities/milestones/converters.py
"""Converters for milestones entity."""

from typing import Dict, Any
from .models import Milestone
from github_data_tools.github.converter_registry import get_converter
from github_data_tools.github.converters import _parse_datetime


def convert_to_milestone(raw_data: Dict[str, Any]) -> Milestone:
    """
    Convert raw GitHub API milestone data to Milestone model.

    Args:
        raw_data: Raw milestone data from GitHub API

    Returns:
        Milestone domain model
    """
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

    # Use registry for nested user conversion
    creator = get_converter("convert_to_user")(raw_data["creator"])

    return Milestone(
        id=raw_data["id"],
        number=raw_data["number"],
        title=raw_data["title"],
        description=raw_data.get("description"),
        state=raw_data["state"].lower(),
        creator=creator,
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
