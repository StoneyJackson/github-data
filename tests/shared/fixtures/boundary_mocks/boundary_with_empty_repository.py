"""Boundary with empty repository fixture for testing."""

import pytest


@pytest.fixture
def boundary_with_empty_repository():
    """Boundary mock simulating empty repository responses."""
    from unittest.mock import Mock

    boundary = Mock()

    # Configure with empty responses for all endpoints
    boundary.get_repository_labels.return_value = []
    boundary.get_repository_issues.return_value = []
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_pull_requests.return_value = []
    boundary.get_all_pull_request_comments.return_value = []
    boundary.get_repository_sub_issues.return_value = []

    return boundary