"""Test configuration and shared fixtures."""

import pytest
import requests_cache
import os

# Import shared fixtures to make them available globally
pytest_plugins = ["tests.shared.fixtures"]


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    # Register custom markers
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "container: Container tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "labels: Label-related tests")
    config.addinivalue_line("markers", "issues: Issue-related tests")
    config.addinivalue_line("markers", "comments: Comment-related tests")
    config.addinivalue_line("markers", "errors: Error handling tests")


@pytest.fixture(autouse=True)
def cleanup_cache():
    """Clean up any global cache before and after each test."""
    # Clean up before test
    if requests_cache.is_installed():
        requests_cache.uninstall_cache()

    # Remove cache file if it exists
    cache_file = "github_api_cache.sqlite"
    if os.path.exists(cache_file):
        os.remove(cache_file)

    yield

    # Clean up after test
    if requests_cache.is_installed():
        requests_cache.uninstall_cache()

    # Remove cache file if it exists
    if os.path.exists(cache_file):
        os.remove(cache_file)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment with proper isolation."""
    # Ensure clean environment for each test
    yield
    # Cleanup after each test
