"""Error handling workflow services fixture for testing."""

import pytest


@pytest.fixture
def error_handling_workflow_services(boundary_with_partial_failures, temp_data_dir):
    """Pre-configured services for error handling workflow testing."""
    from src.github.service import GitHubService
    from src.github.rate_limiter import RateLimitHandler
    from src.storage import create_storage_service

    # Configure GitHub service with minimal retry for fast error testing
    rate_limiter = RateLimitHandler(max_retries=1, base_delay=0.01)
    github_service = GitHubService(boundary_with_partial_failures, rate_limiter)

    # Configure storage service
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
    }