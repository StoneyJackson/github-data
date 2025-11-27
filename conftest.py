"""Root conftest.py for monorepo pytest configuration.

This file provides shared fixtures used across all packages.
Package-specific fixtures are defined in each package's tests/conftest.py file.
"""

import pytest
import tempfile
import shutil


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data.

    This fixture is shared across all packages in the monorepo.
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def storage_service_for_temp_dir(temp_data_dir):
    """Storage service configured for temporary directory.

    This fixture is used by core package tests and is shared across the monorepo.
    """
    from github_data_core.storage import create_storage_service

    # Create storage service and set base path for testing
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir  # Set internal path for testing
    return storage_service


@pytest.fixture
def performance_monitoring_services():
    """Provide storage service with monitoring for performance tests.

    This fixture is used by core package tests and is shared across the monorepo.
    """
    from github_data_core.storage import create_storage_service

    temp_dir = tempfile.mkdtemp()
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_dir

    yield {
        "storage": storage_service,
        "temp_dir": temp_dir,
    }

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
