"""Boundary with sub-issues hierarchy fixture for testing."""

import pytest


@pytest.fixture
def boundary_with_sub_issues_hierarchy(sample_sub_issues_data, complex_hierarchy_data):
    """Boundary mock configured for hierarchical sub-issue testing."""
    from unittest.mock import Mock

    boundary = Mock()

    # Combine sample and complex hierarchy data
    all_issues = sample_sub_issues_data["issues"] + complex_hierarchy_data["issues"]
    all_sub_issues = (
        sample_sub_issues_data["sub_issues"] + complex_hierarchy_data["sub_issues"]
    )

    boundary.get_repository_issues.return_value = all_issues
    boundary.get_repository_sub_issues.return_value = all_sub_issues

    # Empty responses for other endpoints
    boundary.get_repository_labels.return_value = []
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_pull_requests.return_value = []
    boundary.get_all_pull_request_comments.return_value = []

    return boundary
