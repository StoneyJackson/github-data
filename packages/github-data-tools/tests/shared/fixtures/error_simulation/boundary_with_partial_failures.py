"""Boundary with partial failures fixture for testing."""

import pytest


@pytest.fixture
def boundary_with_partial_failures():
    """Boundary mock that simulates partial API failures."""
    from requests.exceptions import ConnectionError, Timeout
    from unittest.mock import Mock

    boundary = Mock()

    # Some endpoints work, others fail
    boundary.get_repository_labels.return_value = [
        {"name": "bug", "color": "d73a4a", "id": 1001}
    ]
    boundary.get_repository_issues.side_effect = ConnectionError("Network error")
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_pull_requests.return_value = []
    boundary.get_all_pull_request_comments.side_effect = Timeout("Request timeout")
    boundary.get_repository_sub_issues.return_value = []

    return boundary
