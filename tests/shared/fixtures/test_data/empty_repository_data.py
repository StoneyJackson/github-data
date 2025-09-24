"""Empty repository data fixture for testing."""

import pytest


@pytest.fixture
def empty_repository_data():
    """Sample data for empty repository testing."""
    return {
        "labels": [],
        "issues": [],
        "comments": [],
        "pull_requests": [],
        "pr_comments": [],
        "sub_issues": [],
    }