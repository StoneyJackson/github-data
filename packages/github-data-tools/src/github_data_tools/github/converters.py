"""
Common data converters for GitHub API responses.

Shared utility converters used across multiple entities.
Entity-specific converters are in their respective entity packages.
"""

from typing import Dict, Any
from datetime import datetime

from ..entities import GitHubUser


def convert_to_user(raw_data: Dict[str, Any]) -> GitHubUser:
    """
    Convert raw GitHub API user data to GitHubUser model.

    This is a common converter used by many entities (issues, PRs, comments, etc.).

    Args:
        raw_data: Raw user data from GitHub API

    Returns:
        GitHubUser domain model
    """
    return GitHubUser(
        login=raw_data["login"],
        id=raw_data["id"],
        avatar_url=raw_data.get("avatarUrl") or raw_data.get("avatar_url") or "",
        html_url=raw_data.get("htmlUrl") or raw_data.get("html_url") or "",
    )


def _extract_pr_number_from_url(url: str) -> int:
    """
    Extract PR number from GitHub URL.

    Utility function used by PR review and comment converters.

    Args:
        url: GitHub URL containing PR number

    Returns:
        PR number extracted from URL, or 0 if extraction fails

    Examples:
        >>> _extract_pr_number_from_url(
        ...     "https://github.com/owner/repo/pull/123")
        123
        >>> _extract_pr_number_from_url(
        ...     "https://api.github.com/repos/owner/repo/pulls/456")
        456
    """
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
    """
    Parse GitHub API datetime string to datetime object.

    Common utility used across all entities that handle timestamps.

    Args:
        datetime_str: ISO 8601 datetime string from GitHub API

    Returns:
        Parsed datetime object with timezone info

    Examples:
        >>> _parse_datetime("2025-11-09T12:00:00Z")
        datetime.datetime(2025, 11, 9, 12, 0, tzinfo=...)
    """
    return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
