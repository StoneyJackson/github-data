# github_data/entities/pr_review_comments/converters.py
"""Converters for pr_review_comments entity."""

from typing import Dict, Any
from .models import PullRequestReviewComment
from github_data_tools.github.converter_registry import get_converter
from github_data_tools.github.converters import (
    _parse_datetime,
    _extract_pr_number_from_url,
)


def convert_to_pr_review_comment(api_data: Dict[str, Any]) -> PullRequestReviewComment:
    """
    Convert GitHub API review comment data to PullRequestReviewComment model.

    Args:
        api_data: Raw review comment data from GitHub API

    Returns:
        PullRequestReviewComment domain model
    """
    user = get_converter("convert_to_user")(api_data["user"])

    return PullRequestReviewComment(
        id=api_data["id"],
        review_id=api_data.get("review_id", ""),
        pr_number=_extract_pr_number_from_url(api_data.get("pull_request_url", "")),
        diff_hunk=api_data.get("diff_hunk", ""),
        path=api_data.get("path", ""),
        line=api_data.get("line"),
        body=api_data["body"],
        user=user,
        created_at=_parse_datetime(api_data["created_at"]),
        updated_at=_parse_datetime(api_data["updated_at"]),
        html_url=api_data["html_url"],
        pull_request_url=api_data.get("pull_request_url", ""),
        in_reply_to_id=api_data.get("in_reply_to_id"),
    )
