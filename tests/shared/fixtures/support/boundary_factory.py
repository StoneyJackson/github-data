"""Boundary factory fixture for testing."""

import pytest


@pytest.fixture
def boundary_factory():
    """Factory for creating configured boundary mocks."""
    from tests.shared.mocks import MockBoundaryFactory

    return MockBoundaryFactory