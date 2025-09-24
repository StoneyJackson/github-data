"""Storage service for temporary directory fixture for testing."""

import pytest


@pytest.fixture
def storage_service_for_temp_dir(temp_data_dir):
    """Storage service configured for temporary directory."""
    from src.storage import create_storage_service

    # Create storage service and set base path for testing
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir  # Set internal path for testing
    return storage_service
