# github_data/entities/sub_issues/converters.py
"""Converters for sub_issues entity."""

from typing import Dict, Any
from .models import SubIssue


def convert_to_sub_issue(raw_data: Dict[str, Any]) -> SubIssue:
    """
    Convert raw GitHub API sub-issue data to SubIssue model.

    Args:
        raw_data: Raw sub-issue data from GitHub API

    Returns:
        SubIssue domain model
    """
    return SubIssue(
        sub_issue_id=raw_data["sub_issue_id"],
        sub_issue_number=raw_data["sub_issue_number"],
        parent_issue_id=raw_data["parent_issue_id"],
        parent_issue_number=raw_data["parent_issue_number"],
        position=raw_data["position"],
    )
