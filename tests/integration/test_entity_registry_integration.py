"""Integration tests for Batch 1 entity migration."""

import pytest
from src.entities.registry import EntityRegistry
from src.operations.strategy_factory import StrategyFactory


@pytest.mark.integration
def test_batch1_entities_discovered():
    """Test that all Batch 1 entities are discovered."""
    registry = EntityRegistry()

    entity_names = registry.get_all_entity_names()

    assert "labels" in entity_names
    assert "milestones" in entity_names
    assert "git_repository" in entity_names


@pytest.mark.integration
def test_batch1_entities_enabled_by_default():
    """Test that Batch 1 entities are enabled by default."""
    registry = EntityRegistry()

    enabled_entities = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled_entities]

    assert "labels" in enabled_names
    assert "milestones" in enabled_names
    assert "git_repository" in enabled_names


@pytest.mark.integration
def test_batch1_entities_no_dependencies():
    """Test that Batch 1 entities have no dependencies."""
    registry = EntityRegistry()

    for entity_name in ["labels", "milestones", "git_repository"]:
        entity = registry.get_entity(entity_name)
        assert entity.get_dependencies() == []


@pytest.mark.integration
def test_batch1_save_strategies_load():
    """Test that save strategies load for Batch 1 entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry, config=None)

    for entity_name in ["labels", "milestones"]:
        strategy = factory.load_save_strategy(entity_name)
        assert strategy is not None
        assert strategy.get_entity_name() == entity_name


@pytest.mark.integration
def test_batch1_execution_order():
    """Test that Batch 1 entities can be sorted (no circular deps)."""
    registry = EntityRegistry()

    enabled_entities = registry.get_enabled_entities()

    # Should not raise ValueError for circular dependency
    assert len(enabled_entities) >= 3
