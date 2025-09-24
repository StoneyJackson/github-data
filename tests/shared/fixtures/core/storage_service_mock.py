"""Storage service mock fixture for testing."""

import pytest


@pytest.fixture
def storage_service_mock():
    """Mock storage service for testing."""
    from src.storage import create_storage_service

    return create_storage_service("json")
