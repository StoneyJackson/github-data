# github_data/entities/releases/converters.py
"""Converters for releases entity."""

from typing import Dict, Any
from .models import Release, ReleaseAsset
from github_data_tools.github.converter_registry import get_converter
from github_data_tools.github.converters import _parse_datetime


def convert_to_release_asset(raw_data: Dict[str, Any]) -> ReleaseAsset:
    """
    Convert raw GitHub API release asset data to ReleaseAsset model.

    Args:
        raw_data: Raw asset data from GitHub API

    Returns:
        ReleaseAsset domain model
    """
    uploader = get_converter("convert_to_user")(raw_data["uploader"])

    return ReleaseAsset(
        id=raw_data["id"],
        name=raw_data["name"],
        content_type=raw_data["content_type"],
        size=raw_data["size"],
        download_count=raw_data["download_count"],
        browser_download_url=raw_data["browser_download_url"],
        created_at=_parse_datetime(raw_data["created_at"]),
        updated_at=_parse_datetime(raw_data["updated_at"]),
        uploader=uploader,
        local_path=raw_data.get("local_path"),  # May be set during save
    )


def convert_to_release(raw_data: Dict[str, Any]) -> Release:
    """
    Convert raw GitHub API release data to Release model.

    Args:
        raw_data: Raw release data from GitHub API

    Returns:
        Release domain model
    """
    # Convert assets
    assets = [
        convert_to_release_asset(asset_data)
        for asset_data in raw_data.get("assets", [])
    ]

    # Use registry for nested user conversion
    author = get_converter("convert_to_user")(raw_data["author"])

    # Handle published_at (can be None for drafts)
    published_at = None
    if raw_data.get("published_at"):
        published_at = _parse_datetime(raw_data["published_at"])

    return Release(
        id=raw_data["id"],
        tag_name=raw_data["tag_name"],
        target_commitish=raw_data["target_commitish"],
        name=raw_data.get("name"),
        body=raw_data.get("body"),
        draft=raw_data.get("draft", False),
        prerelease=raw_data.get("prerelease", False),
        immutable=raw_data.get("immutable", False),  # New 2025 feature
        created_at=_parse_datetime(raw_data["created_at"]),
        published_at=published_at,
        author=author,
        assets=assets,
        html_url=raw_data["html_url"],
    )
