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
def test_strategy_factory_creates_all_10_entities():
    """Test StrategyFactory creates all 11 migrated entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    # All entities including git_repository and releases
    all_entities = [
        "labels",
        "milestones",
        "issues",
        "comments",
        "sub_issues",
        "pull_requests",
        "pr_reviews",
        "pr_review_comments",
        "pr_comments",
        "git_repository",
        "releases",
    ]

    mock_git_service = Mock()
    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    for entity_name in all_entities:
        assert entity_name in strategy_names, f"Failed to create {entity_name}"

    # Verify all 11 entities are created
    assert len(strategy_names) == 11


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

    mock_git_service = Mock()
    strategies = factory.create_save_strategies(git_service=mock_git_service)

    # Should return strategies for all enabled entities including
    # git_repository and releases
    strategy_names = [s.get_entity_name() for s in strategies]
    assert "labels" in strategy_names
    assert "milestones" in strategy_names
    assert "git_repository" in strategy_names  # Included with git_service
    assert "releases" in strategy_names
    assert len(strategy_names) == 11  # All 11 entities with git_service provided


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
