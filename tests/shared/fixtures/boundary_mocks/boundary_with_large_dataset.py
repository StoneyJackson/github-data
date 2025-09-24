"""Boundary with large dataset fixture for testing."""

import pytest


@pytest.fixture
def boundary_with_large_dataset():
    """Boundary mock simulating large dataset with pagination."""
    from unittest.mock import Mock

    boundary = Mock()

    # Generate large datasets for pagination testing
    large_issues = [
        {
            "id": 2000 + i,
            "number": i + 1,
            "title": f"Issue {i + 1}",
            "body": f"Description for issue {i + 1}",
            "state": "open" if i % 3 != 0 else "closed",
            "labels": [{"name": "bug" if i % 2 == 0 else "enhancement"}],
            "user": {"login": "testuser", "id": 1},
            "assignees": [],
            "created_at": f"2024-01-{(i % 28) + 1:02d}T00:00:00Z",
            "updated_at": f"2024-01-{(i % 28) + 1:02d}T00:00:00Z",
            "closed_at": None,
            "html_url": f"https://github.com/owner/repo/issues/{i + 1}",
            "comments": 0,
        }
        for i in range(250)  # Large dataset requiring pagination
    ]

    boundary.get_repository_issues.return_value = large_issues
    boundary.get_repository_labels.return_value = [
        {"name": "bug", "color": "d73a4a", "id": 1001},
        {"name": "enhancement", "color": "a2eeef", "id": 1002},
    ]
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_pull_requests.return_value = []
    boundary.get_all_pull_request_comments.return_value = []
    boundary.get_repository_sub_issues.return_value = []

    return boundary