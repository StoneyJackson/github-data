"""Performance monitoring services fixture for github-data-tools."""

import pytest
import tempfile
import shutil


@pytest.fixture
def performance_monitoring_services():
    """Provide storage service with monitoring for performance tests."""
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
