"""Boundary with data fixture for testing."""

import pytest


@pytest.fixture
def boundary_with_data(sample_github_data):
    """Boundary mock pre-configured with comprehensive sample data."""
    from tests.shared.mocks import MockBoundaryFactory

    return MockBoundaryFactory.create_with_data("full", sample_data=sample_github_data)