"""Integration tests for StrategyFactory with real entities."""

import pytest
from unittest.mock import Mock
from github_data.operations.strategy_factory import StrategyFactory
from github_data.entities.registry import EntityRegistry


@pytest.mark.integration
@pytest.mark.medium
def test_create_save_strategies_all_entities(all_entity_names):
    """Test creating save strategies for all enabled entities except git_repository."""
    registry = EntityRegistry()
    registry.get_entity("git_repository").enabled = False
    factory = StrategyFactory(registry)
    strategies = factory.create_save_strategies()

    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify we got all enabled entities
    expected = set(all_entity_names) - {"git_repository"}
    assert set(strategy_names) == expected


@pytest.mark.integration
@pytest.mark.medium
def test_create_save_strategies_with_git_repository(all_entity_names):
    """Test git_repository strategy is included when git_service provided."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)

    strategy_names = [s.get_entity_name() for s in strategies]

    # Should get ALL entities when git_service provided
    assert set(strategy_names) == set(all_entity_names)

    # Verify git_repository strategy received git_service
    git_strategy = next(
        s for s in strategies if s.get_entity_name() == "git_repository"
    )
    assert git_strategy._git_service is mock_git_service


@pytest.mark.integration
@pytest.mark.medium
def test_create_restore_strategies_all_entities(all_entity_names):
    """Test creating restore strategies for all enabled entities."""
    registry = EntityRegistry()
    registry.get_entity("git_repository").enabled = False
    factory = StrategyFactory(registry)
    mock_github_service = Mock()
    strategies = factory.create_restore_strategies(github_service=mock_github_service)

    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify we got all enabled entities
    expected = set(all_entity_names) - {"git_repository"}
    assert set(strategy_names) == expected


@pytest.mark.integration
def test_create_restore_strategies_labels_with_conflict_strategy():
    """Test labels restore with custom conflict strategy."""
    from github_data.entities.labels.conflict_strategies import LabelConflictStrategy
    from github_data.entities.labels.restore_strategy import FailIfConflictStrategy

    registry = EntityRegistry()

    # Disable git_repository since we're not providing git_service
    registry.get_entity("git_repository").enabled = False

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
    """Test that git_repository validation requires git_service."""
    registry = EntityRegistry()

    factory = StrategyFactory(registry)

    # Without git_service, should raise validation error for git_repository
    with pytest.raises(
        RuntimeError, match="Entity 'git_repository' requires 'git_service'"
    ):
        factory.create_save_strategies()  # No git_service provided

    # Same for restore
    with pytest.raises(
        RuntimeError, match="Entity 'git_repository' requires 'git_service'"
    ):
        factory.create_restore_strategies()  # No git_service provided
