"""GitHub service mock fixture for testing."""

import pytest


@pytest.fixture
def github_service_mock():
    """Mock GitHub service for testing."""
    from unittest.mock import Mock
    from src.github import create_github_service

    service = create_github_service("fake_token")
    service.boundary = Mock()
    return service
