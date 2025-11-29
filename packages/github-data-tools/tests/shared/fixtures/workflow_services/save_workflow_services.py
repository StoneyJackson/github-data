"""Save workflow services fixture for testing."""

import pytest


@pytest.fixture
def save_workflow_services(boundary_with_repository_data, temp_data_dir):
    """Pre-configured services for save workflow testing."""
    from github_data_tools.github.service import GitHubService
    from github_data_tools.storage import create_storage_service

    # Configure GitHub service without rate limiting for tests
    github_service = GitHubService(boundary_with_repository_data)

    # Configure storage service for temp directory
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
    }
