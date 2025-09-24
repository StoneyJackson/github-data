"""Shared test utilities and fixtures.

This module provides centralized access to all shared test infrastructure:
- Common fixtures for temporary directories, sample data, and service mocks
- Enhanced boundary mock configurations for specific testing scenarios
- Error simulation fixtures for testing resilience and error handling
- Workflow-specific service configurations for backup, restore, and sync operations
- Performance testing fixtures with timing monitoring and rate limiting
- Dynamic data builder patterns for scalable test data generation
- Integration test environments for end-to-end testing
- Mock utilities and factory classes for boundary configuration

Usage:
    from tests.shared import temp_data_dir, sample_github_data
    from tests.shared import MockBoundaryFactory, add_pr_method_mocks
    from tests.shared import boundary_with_repository_data, github_data_builder
    from tests.shared import backup_workflow_services, integration_test_environment
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
    # Enhanced boundary configurations
    boundary_with_repository_data,
    boundary_with_empty_repository,
    boundary_with_large_dataset,
    boundary_with_pr_workflow_data,
    boundary_with_sub_issues_hierarchy,
    # Error simulation fixtures
    boundary_with_api_errors,
    boundary_with_partial_failures,
    boundary_with_rate_limiting,
    # Workflow service fixtures
    backup_workflow_services,
    restore_workflow_services,
    sync_workflow_services,
    error_handling_workflow_services,
)

# Mock utilities - for advanced boundary configuration
from .mocks import (
    add_pr_method_mocks,
    add_sub_issues_method_mocks,
    MockBoundaryFactory,
)

# Enhanced fixtures - for advanced testing patterns
from .fixtures.enhanced import (
    performance_monitoring_services,
    rate_limiting_test_services,
    github_data_builder,
    parametrized_data_factory,
    integration_test_environment,
    validation_test_environment,
)

# Test helper utilities - for standardized test patterns
from .helpers import (
    TestDataHelper,
    MockHelper,
    TestMarkerHelper,
    AssertionHelper,
    FixtureHelper,
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
    # Enhanced boundary configurations
    "boundary_with_repository_data",
    "boundary_with_empty_repository",
    "boundary_with_large_dataset",
    "boundary_with_pr_workflow_data",
    "boundary_with_sub_issues_hierarchy",
    # Error simulation fixtures
    "boundary_with_api_errors",
    "boundary_with_partial_failures",
    "boundary_with_rate_limiting",
    # Workflow service fixtures
    "backup_workflow_services",
    "restore_workflow_services",
    "sync_workflow_services",
    "error_handling_workflow_services",
    # Performance testing fixtures
    "performance_monitoring_services",
    "rate_limiting_test_services",
    # Data builder fixtures
    "github_data_builder",
    "parametrized_data_factory",
    # Integration fixtures
    "integration_test_environment",
    "validation_test_environment",
    # Test helper utilities
    "TestDataHelper",
    "MockHelper",
    "TestMarkerHelper",
    "AssertionHelper",
    "FixtureHelper",
    # Builders (if available)
    "GitHubDataBuilder",
]
