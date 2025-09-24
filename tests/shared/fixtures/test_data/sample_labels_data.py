"""Sample label data fixture for testing."""

import pytest


@pytest.fixture
def sample_labels_data():
    """Sample label data for conflict testing."""
    return {
        "labels": [
            {
                "name": "enhancement",
                "color": "a2eeef",
                "description": "New feature or request",
                "id": 1001,
                "url": "https://api.github.com/repos/owner/repo/labels/enhancement",
            },
            {
                "name": "bug",
                "color": "d73a4a",
                "description": "Something isn't working",
                "id": 1002,
                "url": "https://api.github.com/repos/owner/repo/labels/bug",
            },
            {
                "name": "documentation",
                "color": "0075ca",
                "description": "Improvements or additions to documentation",
                "id": 1003,
                "url": "https://api.github.com/repos/owner/repo/labels/documentation",
            },
            {
                "name": "good first issue",
                "color": "7057ff",
                "description": "Good for newcomers",
                "id": 1004,
                "url": (
                    "https://api.github.com/repos/owner/repo/labels/"
                    "good%20first%20issue"
                ),
            },
        ],
        "issues": [],
        "comments": [],
        "pull_requests": [],
        "pr_comments": [],
        "sub_issues": [],
    }