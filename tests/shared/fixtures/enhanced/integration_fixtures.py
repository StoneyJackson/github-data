"""Integration and validation fixtures for advanced testing patterns."""

import pytest


@pytest.fixture
def integration_test_environment(temp_data_dir, parametrized_data_factory):
    """Complete environment for end-to-end integration testing."""
    from src.github.service import GitHubService
    from src.github.rate_limiter import RateLimitHandler
    from src.storage import create_storage_service
    from unittest.mock import Mock

    # Create realistic test data
    test_data = parametrized_data_factory("mixed_states")

    # Setup boundary mock with test data
    boundary = Mock()
    boundary.get_repository_labels.return_value = test_data["labels"]
    boundary.get_repository_issues.return_value = test_data["issues"]
    boundary.get_all_issue_comments.return_value = test_data["comments"]
    boundary.get_repository_pull_requests.return_value = test_data["pull_requests"]
    boundary.get_all_pull_request_comments.return_value = test_data["pr_comments"]
    boundary.get_repository_sub_issues.return_value = test_data["sub_issues"]

    # Setup services
    rate_limiter = RateLimitHandler(max_retries=2, base_delay=0.1)
    github_service = GitHubService(boundary, rate_limiter)
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    # Create expected file structure
    expected_files = [
        "labels.json",
        "issues.json",
        "comments.json",
        "pull_requests.json",
        "pr_comments.json",
        "sub_issues.json",
    ]

    return {
        "github": github_service,
        "storage": storage_service,
        "boundary": boundary,
        "temp_dir": temp_data_dir,
        "test_data": test_data,
        "expected_files": expected_files,
    }


@pytest.fixture
def validation_test_environment(temp_data_dir, github_data_builder):
    """Environment for testing data validation and integrity."""
    from src.github.service import GitHubService
    from src.github.rate_limiter import RateLimitHandler
    from src.storage import create_storage_service
    from unittest.mock import Mock

    # Create data with known validation issues
    test_data = (
        github_data_builder.reset()
        .with_labels(3)
        .with_issues(10)
        .with_sub_issue_hierarchy(2, 2)
        .build()
    )

    # Add some data integrity issues for testing
    test_data["issues"][0]["labels"] = [{"name": "nonexistent-label"}]  # Invalid label
    test_data["sub_issues"].append(
        {  # Orphaned sub-issue
            "parent_issue_id": 99999,
            "child_issue_id": test_data["issues"][1]["id"],
            "parent_issue_number": 99999,
            "sub_issue_number": test_data["issues"][1]["number"],
            "sub_issue_id": test_data["issues"][1]["id"],
            "position": 1,
        }
    )

    boundary = Mock()
    boundary.get_repository_labels.return_value = test_data["labels"]
    boundary.get_repository_issues.return_value = test_data["issues"]
    boundary.get_all_issue_comments.return_value = test_data["comments"]
    boundary.get_repository_pull_requests.return_value = test_data["pull_requests"]
    boundary.get_all_pull_request_comments.return_value = test_data["pr_comments"]
    boundary.get_repository_sub_issues.return_value = test_data["sub_issues"]

    # Setup services
    rate_limiter = RateLimitHandler(max_retries=1, base_delay=0.01)
    github_service = GitHubService(boundary, rate_limiter)
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    return {
        "github": github_service,
        "storage": storage_service,
        "boundary": boundary,
        "temp_dir": temp_data_dir,
        "test_data": test_data,
        "validation_issues": {
            "invalid_label_reference": test_data["issues"][0],
            "orphaned_sub_issue": test_data["sub_issues"][-1],
        },
    }