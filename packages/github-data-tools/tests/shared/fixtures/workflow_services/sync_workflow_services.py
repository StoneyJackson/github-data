"""Sync workflow services fixture for testing."""

import pytest


@pytest.fixture
def sync_workflow_services(boundary_with_repository_data, temp_data_dir):
    """Pre-configured services for sync workflow testing."""
    from github_data_tools.github.service import GitHubService
    from github_data_tools.github.rate_limiter import RateLimitHandler
    from github_data_tools.storage import create_storage_service

    # Configure GitHub service with aggressive rate limiting for sync scenarios
    rate_limiter = RateLimitHandler(max_retries=5, base_delay=0.05)
    github_service = GitHubService(boundary_with_repository_data, rate_limiter)

    # Configure storage service
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
    }
