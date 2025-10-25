import pytest
from src.entities.registry import EntityRegistry
from src.entities.base import RegisteredEntity


@pytest.fixture
def populated_registry():
    """Registry with test entities."""

    class LabelsConfig:
        name = "labels"
        env_var = "INCLUDE_LABELS"
        dependencies = []

    class IssuesConfig:
        name = "issues"
        env_var = "INCLUDE_ISSUES"
        dependencies = []

    registry = EntityRegistry.__new__(EntityRegistry)
    registry._entities = {
        "labels": RegisteredEntity(config=LabelsConfig(), enabled=True),
        "issues": RegisteredEntity(config=IssuesConfig(), enabled=False),
    }
    registry._explicitly_set = set()
    return registry


def test_get_entity_returns_entity(populated_registry):
    """Test get_entity returns registered entity."""
    entity = populated_registry.get_entity("labels")
    assert entity.config.name == "labels"


def test_get_entity_raises_for_unknown(populated_registry):
    """Test get_entity raises ValueError for unknown entity."""
    with pytest.raises(ValueError, match="Unknown entity"):
        populated_registry.get_entity("nonexistent")


def test_get_enabled_entities_returns_only_enabled(populated_registry):
    """Test get_enabled_entities filters to enabled only."""
    enabled = populated_registry.get_enabled_entities()
    names = [e.config.name for e in enabled]

    assert "labels" in names
    assert "issues" not in names


def test_get_all_entity_names_returns_all(populated_registry):
    """Test get_all_entity_names returns all registered entities."""
    names = populated_registry.get_all_entity_names()

    assert "labels" in names
    assert "issues" in names
    assert len(names) == 2
