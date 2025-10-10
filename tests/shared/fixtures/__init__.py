"""Individual fixture modules for GitHub Data tests."""

# Re-export all fixtures from their categorized locations for compatibility

# Core Infrastructure Fixtures
from .core.temp_data_dir import temp_data_dir
from .core.github_service_mock import github_service_mock
from .core.storage_service_mock import storage_service_mock
from .core.mock_boundary_class import mock_boundary_class
from .core.mock_boundary import mock_boundary
from .core.github_service_with_mock import github_service_with_mock

# Test Data Fixtures
from .test_data.sample_github_data import sample_github_data
from .test_data.empty_repository_data import empty_repository_data
from .test_data.sample_sub_issues_data import sample_sub_issues_data
from .test_data.complex_hierarchy_data import complex_hierarchy_data
from .test_data.sample_pr_data import sample_pr_data
from .test_data.sample_labels_data import sample_labels_data

# Boundary Mock Fixtures
from .boundary_mocks.boundary_with_repository_data import boundary_with_repository_data
from .boundary_mocks.boundary_with_empty_repository import (
    boundary_with_empty_repository,
)
from .boundary_mocks.boundary_with_large_dataset import boundary_with_large_dataset
from .boundary_mocks.boundary_with_pr_workflow_data import (
    boundary_with_pr_workflow_data,
)
from .boundary_mocks.boundary_with_sub_issues_hierarchy import (
    boundary_with_sub_issues_hierarchy,
)

# Error Simulation Fixtures
from .error_simulation.boundary_with_api_errors import boundary_with_api_errors
from .error_simulation.boundary_with_partial_failures import (
    boundary_with_partial_failures,
)
from .error_simulation.boundary_with_rate_limiting import boundary_with_rate_limiting

# Workflow Service Fixtures
from .workflow_services.save_workflow_services import save_workflow_services
from .workflow_services.restore_workflow_services import restore_workflow_services
from .workflow_services.sync_workflow_services import sync_workflow_services
from .workflow_services.error_handling_workflow_services import (
    error_handling_workflow_services,
)

# Support Fixtures
from .support.boundary_factory import boundary_factory
from .support.boundary_with_data import boundary_with_data
from .support.storage_service_for_temp_dir import storage_service_for_temp_dir

# Configuration Fixtures
from .config_fixtures import (
    base_config,
    config_with_comments_disabled,
    config_with_minimal_features,
    restore_config,
    config_with_pr_comments_only,
    config_with_prs_no_comments,
    config_with_prs_and_comments,
)

# Environment Variable Fixtures
from .env_fixtures import (
    minimal_env_vars,
    standard_env_vars,
    pr_enabled_env_vars,
    minimal_features_env_vars,
    all_features_env_vars,
    restore_env_vars,
    issues_only_env_vars,
    config_builder,
    config_factory,
    env_config_context,
    make_env_vars,
)

# Export all fixtures
__all__ = [
    # Core Infrastructure Fixtures
    "temp_data_dir",
    "github_service_mock",
    "storage_service_mock",
    "mock_boundary_class",
    "mock_boundary",
    "github_service_with_mock",
    # Test Data Fixtures
    "sample_github_data",
    "empty_repository_data",
    "sample_sub_issues_data",
    "complex_hierarchy_data",
    "sample_pr_data",
    "sample_labels_data",
    # Boundary Mock Fixtures
    "boundary_with_repository_data",
    "boundary_with_empty_repository",
    "boundary_with_large_dataset",
    "boundary_with_pr_workflow_data",
    "boundary_with_sub_issues_hierarchy",
    # Error Simulation Fixtures
    "boundary_with_api_errors",
    "boundary_with_partial_failures",
    "boundary_with_rate_limiting",
    # Workflow Service Fixtures
    "save_workflow_services",
    "restore_workflow_services",
    "sync_workflow_services",
    "error_handling_workflow_services",
    # Support Fixtures
    "boundary_factory",
    "boundary_with_data",
    "storage_service_for_temp_dir",
    # Configuration Fixtures
    "base_config",
    "config_with_comments_disabled",
    "config_with_minimal_features",
    "restore_config",
    "config_with_pr_comments_only",
    "config_with_prs_no_comments",
    "config_with_prs_and_comments",
    # Environment Variable Fixtures
    "minimal_env_vars",
    "standard_env_vars",
    "pr_enabled_env_vars",
    "minimal_features_env_vars",
    "all_features_env_vars",
    "restore_env_vars",
    "issues_only_env_vars",
    "config_builder",
    "config_factory",
    "env_config_context",
    "make_env_vars",
]
