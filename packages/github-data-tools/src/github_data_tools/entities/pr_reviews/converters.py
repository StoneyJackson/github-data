# github_data/entities/pr_reviews/converters.py
"""Converters for pr_reviews entity."""

from typing import Dict, Any
from .models import PullRequestReview
from github_data_tools.github.converter_registry import get_converter
from github_data_tools.github.converters import (
    _parse_datetime,
    _extract_pr_number_from_url,
)


def convert_to_pr_review(api_data: Dict[str, Any]) -> PullRequestReview:
    """
    Convert GitHub API review data to PullRequestReview model.

    Args:
        api_data: Raw review data from GitHub API

    Returns:
        PullRequestReview domain model
    """
    user = get_converter("convert_to_user")(api_data["user"])

    return PullRequestReview(
        id=api_data["id"],
        pr_number=_extract_pr_number_from_url(api_data.get("pull_request_url", "")),
        user=user,
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
