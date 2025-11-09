# github_data/entities/comments/converters.py
"""Converters for comments entity."""

from typing import Dict, Any
from .models import Comment
from github_data.github.converter_registry import get_converter
from github_data.github.converters import _parse_datetime


def convert_to_comment(raw_data: Dict[str, Any]) -> Comment:
    """
    Convert raw GitHub API comment data to Comment model.

    Args:
        raw_data: Raw comment data from GitHub API

    Returns:
        Comment domain model
    """
    # Use registry for nested user conversion
    user = get_converter("convert_to_user")(raw_data["user"])

    return Comment(
        id=raw_data["id"],
        body=raw_data["body"],
        user=user,
        created_at=_parse_datetime(raw_data["created_at"]),
        updated_at=_parse_datetime(raw_data["updated_at"]),
        html_url=raw_data["html_url"],
        issue_url=raw_data["issue_url"],
    )
