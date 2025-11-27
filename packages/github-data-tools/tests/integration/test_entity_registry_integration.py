"""Integration tests for Batch 1 entity migration."""

import pytest
from unittest.mock import Mock
from github_data_core.entities.registry import EntityRegistry
from github_data_core.operations.strategy_factory import StrategyFactory


@pytest.mark.integration
def test_batch1_entities_discovered():
    """Test that all Batch 1 entities are discovered (github-data-tools only)."""
    registry = EntityRegistry()

    entity_names = registry.get_all_entity_names()

    assert "labels" in entity_names
    assert "milestones" in entity_names
    assert "releases" in entity_names


@pytest.mark.integration
def test_batch1_entities_enabled_by_default():
    """Test that Batch 1 entities are enabled by default (github-data-tools only)."""
    registry = EntityRegistry()

    enabled_entities = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled_entities]

    assert "labels" in enabled_names
    assert "milestones" in enabled_names
    assert "releases" in enabled_names


@pytest.mark.integration
def test_batch1_entities_no_dependencies():
    """Test that Batch 1 entities have no dependencies (github-data-tools only)."""
    registry = EntityRegistry()

    for entity_name in ["labels", "milestones", "releases"]:
        entity = registry.get_entity(entity_name)
        assert entity.get_dependencies() == []


@pytest.mark.integration
def test_batch1_save_strategies_create():
    """Test that save strategies create for Batch 1 entities (github-data-tools only)."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    mock_git_service = Mock()
    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    assert "labels" in strategy_names
    assert "milestones" in strategy_names
    assert "releases" in strategy_names


@pytest.mark.integration
def test_batch1_execution_order():
    """Test that Batch 1 entities can be sorted (no circular deps)."""
    registry = EntityRegistry()

    enabled_entities = registry.get_enabled_entities()

    # Should not raise ValueError for circular dependency
    assert len(enabled_entities) >= 3
