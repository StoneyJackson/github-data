"""Test configuration and shared fixtures."""

import pytest
import requests_cache
import os


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
