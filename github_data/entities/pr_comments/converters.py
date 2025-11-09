# github_data/entities/pr_comments/converters.py
"""Converters for pr_comments entity."""

from typing import Dict, Any
from .models import PullRequestComment
from github_data.github.converter_registry import get_converter
from github_data.github.converters import _parse_datetime


def convert_to_pr_comment(raw_data: Dict[str, Any]) -> PullRequestComment:
    """
    Convert raw GitHub API PR comment data to PullRequestComment model.

    Args:
        raw_data: Raw PR comment data from GitHub API

    Returns:
        PullRequestComment domain model
    """
    user = get_converter("convert_to_user")(raw_data["user"])

    return PullRequestComment(
        id=raw_data["id"],
        body=raw_data["body"],
        user=user,
        created_at=_parse_datetime(raw_data["created_at"]),
        updated_at=_parse_datetime(raw_data["updated_at"]),
        html_url=raw_data["html_url"],
        pull_request_url=raw_data["pull_request_url"],
    )
