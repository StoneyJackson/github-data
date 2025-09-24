"""Mock boundary instance fixture for testing."""

import pytest


@pytest.fixture
def mock_boundary():
    """Configured mock boundary instance with all required methods."""
    from unittest.mock import Mock

    boundary = Mock()

    # Configure all boundary methods with default empty responses
    boundary.get_repository_labels.return_value = []
    boundary.get_repository_issues.return_value = []
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_pull_requests.return_value = []
    boundary.get_all_pull_request_comments.return_value = []
    boundary.get_repository_sub_issues.return_value = []

    return boundary