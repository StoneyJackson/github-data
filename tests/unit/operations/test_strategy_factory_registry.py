"""Tests for StrategyFactory with EntityRegistry integration."""

import pytest
from unittest.mock import Mock
from src.operations.strategy_factory import StrategyFactory
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_strategy_factory_accepts_registry():
    """Test that StrategyFactory accepts EntityRegistry parameter."""
    registry = EntityRegistry()
    config = Mock()  # ApplicationConfig for unmigrated entities

    factory = StrategyFactory(registry=registry, config=config)

    assert factory.registry == registry
    assert factory.config == config


@pytest.mark.unit
def test_strategy_factory_loads_labels_from_registry():
    """Test that StrategyFactory loads labels strategy from registry."""
    registry = EntityRegistry()
    config = Mock()
    factory = StrategyFactory(registry=registry, config=config)

    strategy = factory.load_save_strategy("labels")

    assert strategy is not None
    assert strategy.get_entity_name() == "labels"


@pytest.mark.unit
def test_strategy_factory_loads_milestones_from_registry():
    """Test that StrategyFactory loads milestones strategy from registry."""
    registry = EntityRegistry()
    config = Mock()
    factory = StrategyFactory(registry=registry, config=config)

    strategy = factory.load_save_strategy("milestones")

    assert strategy is not None
    assert strategy.get_entity_name() == "milestones"


@pytest.mark.unit
def test_strategy_factory_loads_restore_strategy():
    """Test that StrategyFactory loads restore strategies from registry."""
    from src.entities.labels.conflict_strategies import LabelConflictStrategy

    registry = EntityRegistry()
    config = Mock()
    factory = StrategyFactory(registry=registry, config=config)

    strategy = factory.load_restore_strategy(
        "labels", conflict_strategy=LabelConflictStrategy.OVERWRITE
    )

    assert strategy is not None


@pytest.mark.unit
def test_strategy_factory_loads_all_batch1_and_batch2():
    """Test StrategyFactory loads strategies for all Batch 1+2 entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry, config=None)

    # Test entities that don't require special constructor parameters
    simple_entities = ["labels", "milestones", "issues", "comments", "sub_issues"]

    for entity_name in simple_entities:
        strategy = factory.load_save_strategy(entity_name)
        assert strategy is not None, f"Failed to load {entity_name}"
        assert strategy.get_entity_name() == entity_name

    # Verify git_repository entity is discovered
    # (even though it needs git_service param)
    git_entity = registry.get_entity("git_repository")
    assert git_entity is not None
    assert git_entity.config.name == "git_repository"


@pytest.mark.unit
def test_strategy_factory_loads_all_10_entities():
    """Test StrategyFactory loads all 10 migrated entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry, config=None)

    # Entities that can be loaded without special constructor parameters
    simple_entities = [
        "labels",
        "milestones",
        "issues",
        "comments",
        "sub_issues",
        "pull_requests",
        "pr_reviews",
        "pr_review_comments",
        "pr_comments",
    ]

    for entity_name in simple_entities:
        strategy = factory.load_save_strategy(entity_name)
        assert strategy is not None, f"Failed to load {entity_name}"
        assert strategy.get_entity_name() == entity_name

    # Verify git_repository is discovered (even though it needs git_service param)
    git_entity = registry.get_entity("git_repository")
    assert git_entity is not None
    assert git_entity.config.name == "git_repository"
