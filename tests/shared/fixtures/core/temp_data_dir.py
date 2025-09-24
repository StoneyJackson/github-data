"""Temporary directory fixture for GitHub Data tests."""

import tempfile
import pytest


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir