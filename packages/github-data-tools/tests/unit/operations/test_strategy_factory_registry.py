"""Tests for StrategyFactory with EntityRegistry integration."""

import pytest
from unittest.mock import Mock
from github_data.operations.strategy_factory import StrategyFactory
from github_data.entities.registry import EntityRegistry


@pytest.mark.unit
def test_strategy_factory_accepts_registry():
    """Test that StrategyFactory accepts EntityRegistry parameter."""
    registry = EntityRegistry()

    factory = StrategyFactory(registry=registry)

    assert factory.registry == registry


@pytest.mark.unit
def test_strategy_factory_creates_labels_strategy():
    """Test that StrategyFactory creates labels strategy via factory method."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    mock_git_service = Mock()
    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    assert "labels" in strategy_names


@pytest.mark.unit
def test_strategy_factory_creates_milestones_strategy():
    """Test that StrategyFactory creates milestones strategy via factory method."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    mock_git_service = Mock()
    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    assert "milestones" in strategy_names


@pytest.mark.unit
def test_strategy_factory_creates_restore_strategy():
    """Test that StrategyFactory creates restore strategies via factory methods."""
    from github_data.entities.labels.conflict_strategies import LabelConflictStrategy

    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    mock_git_service = Mock()
    mock_github_service = Mock()
    strategies = factory.create_restore_strategies(
        git_service=mock_git_service,
        github_service=mock_github_service,
        conflict_strategy=LabelConflictStrategy.SKIP,
    )
    strategy_names = [s.get_entity_name() for s in strategies]

    assert "labels" in strategy_names


@pytest.mark.unit
def test_strategy_factory_creates_all_batch1_and_batch2():
    """Test StrategyFactory creates strategies for all Batch 1+2 entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    # Test entities that don't require special constructor parameters
    simple_entities = ["labels", "milestones", "issues", "comments", "sub_issues"]

    mock_git_service = Mock()
    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    for entity_name in simple_entities:
        assert entity_name in strategy_names, f"Failed to create {entity_name}"

    # Verify git_repository entity is discovered and created with git_service
    git_entity = registry.get_entity("git_repository")
    assert git_entity is not None
    assert git_entity.config.name == "git_repository"
    assert "git_repository" in strategy_names


@pytest.mark.unit
@pytest.mark.fast
def test_strategy_factory_creates_all_entities(all_entity_names):
    """Test StrategyFactory creates strategies for all discovered entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify all discovered entities have strategies
    assert set(strategy_names) == set(all_entity_names)


@pytest.mark.unit
def test_strategy_factory_works_without_config():
    """Test StrategyFactory works with only EntityRegistry."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    # Should work without config parameter
    assert factory.registry == registry


@pytest.mark.unit
@pytest.mark.fast
def test_strategy_factory_create_save_strategies_from_registry(all_entity_names):
    """Test save strategies created from registry match all entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify strategies for all entities
    assert set(strategy_names) == set(all_entity_names)


@pytest.mark.unit
def test_strategy_factory_respects_disabled_entities():
    """Test factory skips disabled entities."""
    import os

    os.environ["INCLUDE_LABELS"] = "false"
    registry = EntityRegistry.from_environment()
    factory = StrategyFactory(registry=registry)

    mock_git_service = Mock()
    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    assert "labels" not in strategy_names

    del os.environ["INCLUDE_LABELS"]
