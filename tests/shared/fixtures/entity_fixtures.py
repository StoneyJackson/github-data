"""Entity discovery fixtures for dynamic test validation.

These fixtures use EntityRegistry's auto-discovery to provide entity
information without requiring manual updates when entities are added.
"""

import pytest
from github_data.entities.registry import EntityRegistry


@pytest.fixture
def entity_registry():
    """Provide a fresh EntityRegistry instance.

    Returns:
        EntityRegistry: Fresh registry with all discovered entities
    """
    return EntityRegistry()


@pytest.fixture
def all_entity_names(entity_registry):
    """Get all registered entity names dynamically.

    Uses EntityRegistry auto-discovery to find all entities.
    No manual updates needed when adding new entities.

    Returns:
        List[str]: All discovered entity names
    """
    return entity_registry.get_all_entity_names()


@pytest.fixture
def enabled_entity_names(entity_registry):
    """Get all enabled entity names by default configuration.

    Returns:
        List[str]: Names of entities enabled by default
    """
    enabled = entity_registry.get_enabled_entities()
    return [e.config.name for e in enabled]


@pytest.fixture
def entity_names_by_dependency_order(entity_registry):
    """Get enabled entities sorted by dependency order.

    Returns:
        List[str]: Entity names in topological sort order
    """
    enabled = entity_registry.get_enabled_entities()
    return [e.config.name for e in enabled]


@pytest.fixture
def independent_entity_names(entity_registry):
    """Get entities with no dependencies.

    Returns:
        List[str]: Entity names with empty dependency lists
    """
    all_entities = entity_registry._entities.values()
    return [e.config.name for e in all_entities if not e.get_dependencies()]
