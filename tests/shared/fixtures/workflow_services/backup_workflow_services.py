"""Backup workflow services fixture for testing."""

import pytest


@pytest.fixture
def backup_workflow_services(boundary_with_repository_data, temp_data_dir):
    """Pre-configured services for backup workflow testing."""
    from src.github.service import GitHubService
    from src.github.rate_limiter import RateLimitHandler
    from src.storage import create_storage_service

    # Configure GitHub service with realistic rate limiting
    rate_limiter = RateLimitHandler(max_retries=3, base_delay=0.1)
    github_service = GitHubService(boundary_with_repository_data, rate_limiter)

    # Configure storage service for temp directory
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
    }
