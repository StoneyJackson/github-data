"""Test environment fixtures for integration tests."""

import pytest


@pytest.fixture
def integration_test_environment(parametrized_data_factory):
    """Provide integration test environment with test data."""
    return {
        "test_data": parametrized_data_factory("basic"),
        "repo_name": "owner/repo",
        "config": {
            "include_issues": True,
            "include_pull_requests": True,
            "include_comments": True,
        },
    }


@pytest.fixture
def rate_limiting_test_services(boundary_with_rate_limiting):
    """Provide services configured for rate limiting tests."""
    from github_data_tools.github.service import GitHubService
    from github_data_core.storage import create_storage_service
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_dir

    github_service = GitHubService(boundary_with_rate_limiting)

    services = {
        "github": github_service,
        "storage": storage_service,
        "boundary": boundary_with_rate_limiting,
        "temp_dir": temp_dir,
    }

    yield services

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
