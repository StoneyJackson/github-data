"""Boundary with API errors fixture for testing."""

import pytest


@pytest.fixture
def boundary_with_api_errors():
    """Boundary mock that simulates various GitHub API errors."""
    from requests.exceptions import ConnectionError, Timeout
    from unittest.mock import Mock

    boundary = Mock()

    # Configure different types of errors for different endpoints
    boundary.get_repository_labels.side_effect = ConnectionError("Network error")
    boundary.get_repository_issues.side_effect = Timeout("Request timeout")
    boundary.get_all_issue_comments.side_effect = Exception("API Error")
    boundary.get_repository_pull_requests.side_effect = Exception("Rate limit exceeded")
    boundary.get_all_pull_request_comments.return_value = []
    boundary.get_repository_sub_issues.return_value = []

    return boundary