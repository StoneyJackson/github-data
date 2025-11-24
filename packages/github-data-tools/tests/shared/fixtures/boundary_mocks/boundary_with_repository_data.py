"""Boundary with repository data fixture for testing."""

import pytest


@pytest.fixture
def boundary_with_repository_data(sample_github_data):
    """Boundary mock configured with full repository data responses."""
    from unittest.mock import Mock

    boundary = Mock()

    # Configure with realistic repository responses
    boundary.get_repository_labels.return_value = sample_github_data["labels"]
    boundary.get_repository_issues.return_value = sample_github_data["issues"]
    boundary.get_all_issue_comments.return_value = sample_github_data["comments"]
    boundary.get_repository_pull_requests.return_value = sample_github_data[
        "pull_requests"
    ]
    boundary.get_all_pull_request_comments.return_value = sample_github_data[
        "pr_comments"
    ]
    boundary.get_repository_sub_issues.return_value = sample_github_data.get(
        "sub_issues", []
    )
    boundary.get_all_pull_request_reviews.return_value = sample_github_data.get(
        "pr_reviews", []
    )
    boundary.get_all_pull_request_review_comments.return_value = sample_github_data.get(
        "pr_review_comments", []
    )

    return boundary
