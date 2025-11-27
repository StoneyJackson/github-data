"""Integration tests for StrategyFactory with real entities."""

import pytest
from unittest.mock import Mock
from github_data_core.operations.strategy_factory import StrategyFactory
from github_data_core.entities.registry import EntityRegistry


@pytest.mark.integration
@pytest.mark.medium
def test_create_save_strategies_all_entities(all_entity_names):
    """Test creating save strategies for all enabled entities (github-data-tools only)."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)
    strategies = factory.create_save_strategies()

    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify we got all enabled entities (all entities in github-data-tools)
    assert set(strategy_names) == set(all_entity_names)


@pytest.mark.integration
@pytest.mark.medium
def test_create_save_strategies_with_git_repository(all_entity_names):
    """Test save strategies work even when git_service is provided (github-data-tools entities don't use it)."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)

    strategy_names = [s.get_entity_name() for s in strategies]

    # Should get all github-data-tools entities (git_repository is in different package)
    assert set(strategy_names) == set(all_entity_names)


@pytest.mark.integration
@pytest.mark.medium
def test_create_restore_strategies_all_entities(all_entity_names):
    """Test creating restore strategies for all enabled entities (github-data-tools only)."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)
    mock_github_service = Mock()
    strategies = factory.create_restore_strategies(github_service=mock_github_service)

    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify we got all enabled entities (all entities in github-data-tools)
    assert set(strategy_names) == set(all_entity_names)


@pytest.mark.integration
def test_create_restore_strategies_labels_with_conflict_strategy():
    """Test labels restore with custom conflict strategy (github-data-tools only)."""
    from github_data_tools.entities.labels.conflict_strategies import LabelConflictStrategy
    from github_data_tools.entities.labels.restore_strategy import FailIfConflictStrategy

    registry = EntityRegistry()
    factory = StrategyFactory(registry)
    mock_github_service = Mock()
    strategies = factory.create_restore_strategies(
        github_service=mock_github_service,
        conflict_strategy=LabelConflictStrategy.FAIL_IF_CONFLICT,
    )

    # Find labels strategy
    labels_strategy = next(s for s in strategies if s.get_entity_name() == "labels")
    assert isinstance(labels_strategy._conflict_strategy, FailIfConflictStrategy)


@pytest.mark.integration
def test_git_repository_requires_git_service():
    """Test that github-data-tools entities don't require git_service.

    Note: git_repository entity is in git-repo-tools package, not github-data-tools.
    All entities in github-data-tools work without git_service.
    """
    registry = EntityRegistry()
    factory = StrategyFactory(registry)

    # All github-data-tools entities should work without git_service
    strategies = factory.create_save_strategies()  # No git_service - should work
    assert len(strategies) > 0  # Should have created strategies

    # Same for restore
    mock_github_service = Mock()
    restore_strategies = factory.create_restore_strategies(github_service=mock_github_service)
    assert len(restore_strategies) > 0  # Should have created strategies
