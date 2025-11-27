"""Conftest for core package tests."""

import pytest
from pathlib import Path
import tempfile
import shutil

# Import shared fixtures
from .shared.fixtures.support.storage_service_for_temp_dir import storage_service_for_temp_dir  # noqa: F401
from .shared.fixtures.support.performance_monitoring_services import performance_monitoring_services  # noqa: F401


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
