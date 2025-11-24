"""Boundary with PR workflow data fixture for testing."""

import pytest


@pytest.fixture
def boundary_with_pr_workflow_data(sample_pr_data):
    """Boundary mock configured for pull request workflow testing."""
    from unittest.mock import Mock

    boundary = Mock()

    # Configure PR-specific responses
    boundary.get_repository_pull_requests.return_value = sample_pr_data["pull_requests"]
    boundary.get_all_pull_request_comments.return_value = sample_pr_data["pr_comments"]

    # Add PR branch information
    def get_pr_commits(pr_number):
        return [
            {
                "sha": f"abc123{pr_number}",
                "message": f"Commit for PR #{pr_number}",
                "author": {"login": "developer"},
            }
        ]

    boundary.get_pull_request_commits.side_effect = get_pr_commits

    # Empty responses for non-PR data
    boundary.get_repository_labels.return_value = []
    boundary.get_repository_issues.return_value = []
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_sub_issues.return_value = []

    return boundary
