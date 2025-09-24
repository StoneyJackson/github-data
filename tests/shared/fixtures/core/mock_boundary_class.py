"""Mock GitHubApiBoundary class fixture for testing."""

import pytest


@pytest.fixture
def mock_boundary_class():
    """Mock GitHubApiBoundary class for patching."""
    from unittest.mock import patch

    with patch("src.github.service.GitHubApiBoundary") as mock:
        yield mock