# github_data/entities/labels/converters.py
"""Converters for labels entity."""

from typing import Dict, Any
from .models import Label


def convert_to_label(raw_data: Dict[str, Any]) -> Label:
    """
    Convert raw GitHub API label data to Label model.

    Args:
        raw_data: Raw label data from GitHub API

    Returns:
        Label domain model
    """
    return Label(
        id=raw_data["id"],
        name=raw_data["name"],
        color=raw_data["color"],
        description=raw_data.get("description"),
        url=raw_data["url"],
    )
