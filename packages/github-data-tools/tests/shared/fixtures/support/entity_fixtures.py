"""Entity-related fixtures for testing."""

import pytest
from github_data_core.entities.registry import EntityRegistry


@pytest.fixture
def all_entity_names():
    """Provide list of all entity names from registry."""
    registry = EntityRegistry()
    return registry.get_all_entity_names()


@pytest.fixture
def enabled_entity_names():
    """Provide list of enabled entity names from registry."""
    registry = EntityRegistry()
    return [entity.config.name for entity in registry.get_enabled_entities()]
