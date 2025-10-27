"""Tests for StrategyFactory with EntityRegistry integration."""

import pytest
from src.operations.strategy_factory import StrategyFactory
from src.entities.registry import EntityRegistry


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

    strategies = factory.create_save_strategies()
    strategy_names = [s.get_entity_name() for s in strategies]

    assert "labels" in strategy_names


@pytest.mark.unit
def test_strategy_factory_creates_milestones_strategy():
    """Test that StrategyFactory creates milestones strategy via factory method."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    strategies = factory.create_save_strategies()
    strategy_names = [s.get_entity_name() for s in strategies]

    assert "milestones" in strategy_names


@pytest.mark.unit
def test_strategy_factory_creates_restore_strategy():
    """Test that StrategyFactory creates restore strategies via factory methods."""
    from src.entities.labels.conflict_strategies import LabelConflictStrategy

    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    strategies = factory.create_restore_strategies(
        conflict_strategy=LabelConflictStrategy.SKIP
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

    strategies = factory.create_save_strategies()
    strategy_names = [s.get_entity_name() for s in strategies]

    for entity_name in simple_entities:
        assert entity_name in strategy_names, f"Failed to create {entity_name}"

    # Verify git_repository entity is discovered
    # (even though it needs git_service param)
    git_entity = registry.get_entity("git_repository")
    assert git_entity is not None
    assert git_entity.config.name == "git_repository"


@pytest.mark.unit
def test_strategy_factory_creates_all_10_entities():
    """Test StrategyFactory creates all 10 migrated entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    # Entities that can be created without special constructor parameters
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

    strategies = factory.create_save_strategies()
    strategy_names = [s.get_entity_name() for s in strategies]

    for entity_name in simple_entities:
        assert entity_name in strategy_names, f"Failed to create {entity_name}"

    # Verify git_repository is discovered (even though it needs git_service param)
    git_entity = registry.get_entity("git_repository")
    assert git_entity is not None
    assert git_entity.config.name == "git_repository"


@pytest.mark.unit
def test_strategy_factory_works_without_config():
    """Test StrategyFactory works with only EntityRegistry."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    # Should work without config parameter
    assert factory.registry == registry


@pytest.mark.unit
def test_strategy_factory_create_save_strategies_from_registry():
    """Test factory creates save strategies for enabled entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    strategies = factory.create_save_strategies()

    # Should return strategies for all enabled entities except
    # git_repository (needs git_service)
    strategy_names = [s.get_entity_name() for s in strategies]
    assert "labels" in strategy_names
    assert "milestones" in strategy_names
    assert "git_repository" not in strategy_names  # Skipped without git_service
    assert len(strategy_names) == 9  # 9 entities when git_service not provided


@pytest.mark.unit
def test_strategy_factory_respects_disabled_entities():
    """Test factory skips disabled entities."""
    import os

    os.environ["INCLUDE_LABELS"] = "false"
    registry = EntityRegistry.from_environment()
    factory = StrategyFactory(registry=registry)

    strategies = factory.create_save_strategies()
    strategy_names = [s.get_entity_name() for s in strategies]

    assert "labels" not in strategy_names

    del os.environ["INCLUDE_LABELS"]
