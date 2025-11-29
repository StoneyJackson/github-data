"""GitHub service registry validation fixture."""

import pytest
from unittest.mock import Mock
from github_data_tools.github.service import GitHubService
from github_data_tools.github.boundary import GitHubApiBoundary


@pytest.fixture
def validate_github_service_registry():
    """Provide GitHubService with validated operation registry."""
    # Create a mock boundary
    mock_boundary = Mock(spec=GitHubApiBoundary)

    # Create GitHubService which will initialize the operation registry
    service = GitHubService(mock_boundary)

    return service
