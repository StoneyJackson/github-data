"""Shared fixtures for GitHub service testing."""

import pytest
from unittest.mock import Mock
from github_data.github.service import GitHubService
from github_data.entities.registry import EntityRegistry


@pytest.fixture
def validate_github_service_registry():
    """
    Validate GitHubService registry at test startup.

    Ensures all entity operations are properly registered and discoverable.
    """
    mock_boundary = Mock()
    service = GitHubService(boundary=mock_boundary, caching_enabled=False)
    registry = service._operation_registry

    # Ensure all entity operations are registered
    entity_registry = EntityRegistry()

    for entity_name, entity in entity_registry._entities.items():
        if not hasattr(entity.config, "github_api_operations"):
            continue

        for method_name in entity.config.github_api_operations:
            assert (
                method_name in registry.list_operations()
            ), f"Operation '{method_name}' from entity '{entity_name}' not registered"

    return service
