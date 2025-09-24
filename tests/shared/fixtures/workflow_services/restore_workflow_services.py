"""Restore workflow services fixture for testing."""

import pytest


@pytest.fixture
def restore_workflow_services(
    boundary_with_empty_repository, temp_data_dir, sample_github_data
):
    """Pre-configured services for restore workflow testing."""
    from src.github.service import GitHubService
    from src.github.rate_limiter import RateLimitHandler
    from src.storage import create_storage_service
    import json
    import os

    # Configure GitHub service for restore operations
    rate_limiter = RateLimitHandler(max_retries=3, base_delay=0.1)
    github_service = GitHubService(boundary_with_empty_repository, rate_limiter)

    # Configure storage service and pre-populate with sample data
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    # Write sample data files for restore testing
    data_files = {
        "labels.json": sample_github_data["labels"],
        "issues.json": sample_github_data["issues"],
        "comments.json": sample_github_data["comments"],
        "pull_requests.json": sample_github_data["pull_requests"],
        "pr_comments.json": sample_github_data["pr_comments"],
    }

    for filename, data in data_files.items():
        file_path = os.path.join(temp_data_dir, filename)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
        "data_files": list(data_files.keys()),
    }