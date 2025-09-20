"""Shared test utilities and fixtures.

This module provides centralized access to all shared test infrastructure:
- Common fixtures for temporary directories, sample data, and service mocks
- Mock utilities and factory classes for boundary configuration
- Builder patterns for dynamic test data generation

Usage:
    from tests.shared import temp_data_dir, sample_github_data
    from tests.shared import MockBoundaryFactory, add_pr_method_mocks
"""

# Core fixtures - used across most test files
from .fixtures import (
    temp_data_dir,
    sample_github_data,
    github_service_mock,
    storage_service_mock,
    mock_boundary_class,
    mock_boundary,
    github_service_with_mock,
    empty_repository_data,
    sample_sub_issues_data,
    sample_pr_data,
    sample_labels_data,
    complex_hierarchy_data,
    boundary_factory,
    boundary_with_data,
    storage_service_for_temp_dir,
)

# Mock utilities - for advanced boundary configuration
from .mocks import (
    add_pr_method_mocks,
    add_sub_issues_method_mocks,
    MockBoundaryFactory,
)

# Builder patterns - for dynamic test data (if available)
try:
    from .builders import GitHubDataBuilder
except ImportError:
    GitHubDataBuilder = None

# Export all fixtures and utilities
__all__ = [
    # Core fixtures
    "temp_data_dir",
    "sample_github_data",
    "github_service_mock",
    "storage_service_mock",
    # Service mocking fixtures
    "mock_boundary_class",
    "mock_boundary",
    "github_service_with_mock",
    # Specialized data fixtures
    "empty_repository_data",
    "sample_sub_issues_data",
    "sample_pr_data",
    "sample_labels_data",
    "complex_hierarchy_data",
    # Factory fixtures
    "boundary_factory",
    "boundary_with_data",
    "storage_service_for_temp_dir",
    # Mock utilities
    "add_pr_method_mocks",
    "add_sub_issues_method_mocks",
    "MockBoundaryFactory",
    # Builders (if available)
    "GitHubDataBuilder",
]
