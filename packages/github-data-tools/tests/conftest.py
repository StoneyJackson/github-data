"""Conftest for github-data-tools tests.

This conftest imports shared fixtures to make them available to all tests.
Using direct imports instead of pytest_plugins to avoid the "non-top-level conftest" error.
"""

# Import all fixtures to register them with pytest
# Test data fixtures
from .shared.fixtures.test_data.sample_github_data import sample_github_data  # noqa: F401
from .shared.fixtures.test_data.empty_repository_data import empty_repository_data  # noqa: F401
from .shared.fixtures.test_data.complex_hierarchy_data import complex_hierarchy_data  # noqa: F401
from .shared.fixtures.test_data.chronological_comments_data import chronological_comments_data  # noqa: F401
from .shared.fixtures.test_data.orphaned_sub_issues_data import orphaned_sub_issues_data, regular_issue_data  # noqa: F401
from .shared.fixtures.test_data.mixed_states_data import existing_repository_data  # noqa: F401
from .shared.fixtures.test_data.sample_labels_data import sample_labels_data  # noqa: F401
from .shared.fixtures.test_data.sample_pr_data import sample_pr_data  # noqa: F401
from .shared.fixtures.test_data.sample_sub_issues_data import sample_sub_issues_data  # noqa: F401

# Core support fixtures
from .shared.fixtures.support.storage_service_for_temp_dir import storage_service_for_temp_dir  # noqa: F401
from .shared.fixtures.support.boundary_factory import boundary_factory  # noqa: F401
from .shared.fixtures.support.boundary_with_data import boundary_with_data  # noqa: F401

# Boundary mock fixtures
from .shared.fixtures.boundary_mocks.boundary_with_empty_repository import boundary_with_empty_repository  # noqa: F401
from .shared.fixtures.boundary_mocks.boundary_with_large_dataset import boundary_with_large_dataset  # noqa: F401
from .shared.fixtures.boundary_mocks.boundary_with_pr_workflow_data import boundary_with_pr_workflow_data  # noqa: F401
from .shared.fixtures.boundary_mocks.boundary_with_repository_data import boundary_with_repository_data  # noqa: F401
from .shared.fixtures.boundary_mocks.boundary_with_sub_issues_hierarchy import boundary_with_sub_issues_hierarchy  # noqa: F401

# Error simulation fixtures
from .shared.fixtures.error_simulation.boundary_with_api_errors import boundary_with_api_errors  # noqa: F401
from .shared.fixtures.error_simulation.boundary_with_partial_failures import boundary_with_partial_failures  # noqa: F401
from .shared.fixtures.error_simulation.boundary_with_rate_limiting import boundary_with_rate_limiting  # noqa: F401

# Workflow service fixtures
from .shared.fixtures.workflow_services.error_handling_workflow_services import *  # noqa: F401,F403
from .shared.fixtures.workflow_services.restore_workflow_services import *  # noqa: F401,F403
from .shared.fixtures.workflow_services.save_workflow_services import *  # noqa: F401,F403
from .shared.fixtures.workflow_services.sync_workflow_services import *  # noqa: F401,F403
