"""Conftest for github-data-tools tests.

This conftest imports shared fixtures to make them available to all tests.
Using direct imports instead of pytest_plugins to avoid the
"non-top-level conftest" error.
"""

# Import all fixtures to register them with pytest
# Test data fixtures
from .shared.fixtures.test_data.sample_github_data import (  # noqa: F401
    sample_github_data,
)
from .shared.fixtures.test_data.empty_repository_data import (  # noqa: F401
    empty_repository_data,
)
from .shared.fixtures.test_data.complex_hierarchy_data import (  # noqa: F401
    complex_hierarchy_data,
)
from .shared.fixtures.test_data.chronological_comments_data import (  # noqa
    chronological_comments_data,
)
from .shared.fixtures.test_data.orphaned_sub_issues_data import (  # noqa: F401
    orphaned_sub_issues_data,
    regular_issue_data,
)
from .shared.fixtures.test_data.mixed_states_data import (  # noqa: F401
    existing_repository_data,
)
from .shared.fixtures.test_data.sample_labels_data import (  # noqa: F401
    sample_labels_data,
)
from .shared.fixtures.test_data.sample_pr_data import (  # noqa: F401
    sample_pr_data,
)
from .shared.fixtures.test_data.sample_sub_issues_data import (  # noqa: F401
    sample_sub_issues_data,
)

# Core support fixtures
from .shared.fixtures.support.storage_service_for_temp_dir import (  # noqa: F401
    storage_service_for_temp_dir,
)
from .shared.fixtures.support.boundary_factory import (  # noqa: F401
    boundary_factory,
)
from .shared.fixtures.support.boundary_with_data import (  # noqa: F401
    boundary_with_data,
)

# Boundary mock fixtures
from .shared.fixtures.boundary_mocks.boundary_with_empty_repository import (  # noqa: F401, E501
    boundary_with_empty_repository,
)
from .shared.fixtures.boundary_mocks.boundary_with_large_dataset import (  # noqa: F401, E501
    boundary_with_large_dataset,
)
from .shared.fixtures.boundary_mocks.boundary_with_pr_workflow_data import (  # noqa: F401, E501
    boundary_with_pr_workflow_data,
)
from .shared.fixtures.boundary_mocks.boundary_with_repository_data import (  # noqa: F401, E501
    boundary_with_repository_data,
)
from .shared.fixtures.boundary_mocks.boundary_with_sub_issues_hierarchy import (  # noqa: F401, E501
    boundary_with_sub_issues_hierarchy,
)

# Error simulation fixtures
from .shared.fixtures.error_simulation.boundary_with_api_errors import (  # noqa: F401, E501
    boundary_with_api_errors,
)
from .shared.fixtures.error_simulation.boundary_with_partial_failures import (  # noqa: F401, E501
    boundary_with_partial_failures,
)
from .shared.fixtures.error_simulation.boundary_with_rate_limiting import (  # noqa: F401, E501
    boundary_with_rate_limiting,
)

# Workflow service fixtures
from .shared.fixtures.workflow_services.error_handling_workflow_services import *  # noqa: F401, F403, E501
from .shared.fixtures.workflow_services.restore_workflow_services import *  # noqa: F401, F403, E501
from .shared.fixtures.workflow_services.save_workflow_services import *  # noqa: F401, F403, E501
from .shared.fixtures.workflow_services.sync_workflow_services import *  # noqa: F401, F403, E501

# Additional support fixtures
from .shared.fixtures.support.entity_fixtures import (  # noqa: F401
    all_entity_names,
    enabled_entity_names,
)
from .shared.fixtures.support.github_service_registry import (  # noqa: F401
    validate_github_service_registry,
)
from .shared.fixtures.support.data_builders import (  # noqa: F401
    github_data_builder,
    parametrized_data_factory,
)
from .shared.fixtures.support.test_environments import (  # noqa: F401
    integration_test_environment,
    rate_limiting_test_services,
)
from .shared.fixtures.support.performance_monitoring_services import (  # noqa: F401, E501
    performance_monitoring_services,
)

# Entity registry fixture for monorepo
import pytest
from pathlib import Path
from github_data_core.entities.registry import EntityRegistry
import tempfile
import shutil


@pytest.fixture(autouse=True)
def patch_entity_registry_default(monkeypatch):
    """Automatically patch EntityRegistry to find entities in github-data-tools package.

    This fixture runs automatically for all tests in github-data-tools package,
    ensuring that EntityRegistry() without arguments will find entities in the
    correct location.
    """
    original_init = EntityRegistry.__init__

    def patched_init(self, entities_dir=None):
        if entities_dir is None:
            # Default to github-data-tools entities directory
            entities_dir = (
                Path(__file__).parent.parent / "src/github_data_tools/entities"
            )
        original_init(self, entities_dir)

    monkeypatch.setattr(EntityRegistry, "__init__", patched_init)


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
