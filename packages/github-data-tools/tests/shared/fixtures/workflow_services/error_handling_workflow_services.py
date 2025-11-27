"""Error handling workflow services fixture for testing."""

import pytest


@pytest.fixture
def error_handling_workflow_services(boundary_with_partial_failures, temp_data_dir):
    """Pre-configured services for error handling workflow testing."""
    from github_data_tools.github.service import GitHubService
    from github_data_tools.storage import create_storage_service

    # Configure GitHub service with minimal retry for fast error testing
    github_service = GitHubService(boundary_with_partial_failures)

    # Configure storage service
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
    }
