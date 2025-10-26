"""Integration tests for StrategyFactory with real entities."""

import pytest
from unittest.mock import Mock
from src.operations.strategy_factory import StrategyFactory
from src.entities.registry import EntityRegistry


@pytest.mark.integration
def test_create_save_strategies_all_entities():
    """Test creating save strategies for all real entities."""
    registry = EntityRegistry()

    # Enable all entities
    for entity_name in ["labels", "milestones", "issues", "comments",
                        "pull_requests", "pr_reviews", "pr_comments",
                        "pr_review_comments", "sub_issues"]:
        pass  # Already enabled by default

    factory = StrategyFactory(registry)
    strategies = factory.create_save_strategies()

    # Should get strategies for all enabled entities except git_repository
    assert len(strategies) == 9
    entity_names = [s.get_entity_name() for s in strategies]
    assert "labels" in entity_names
    assert "issues" in entity_names


@pytest.mark.integration
def test_create_save_strategies_with_git_repository():
    """Test creating save strategies including git_repository."""
    registry = EntityRegistry()

    factory = StrategyFactory(registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)

    # Should include git_repository when git_service provided
    entity_names = [s.get_entity_name() for s in strategies]
    assert "git_repository" in entity_names

    # Find git_repository strategy and verify it has git_service
    git_strategy = next(s for s in strategies if s.get_entity_name() == "git_repository")
    assert git_strategy._git_service is mock_git_service


@pytest.mark.integration
def test_create_restore_strategies_all_entities():
    """Test creating restore strategies for all real entities."""
    registry = EntityRegistry()

    factory = StrategyFactory(registry)
    strategies = factory.create_restore_strategies(
        include_original_metadata=False
    )

    # Should get strategies for all enabled entities except git_repository
    assert len(strategies) == 9

    # Verify metadata flag was passed
    for strategy in strategies:
        if hasattr(strategy, '_include_original_metadata'):
            assert strategy._include_original_metadata is False


@pytest.mark.integration
def test_create_restore_strategies_labels_with_conflict_strategy():
    """Test labels restore with custom conflict strategy."""
    from src.entities.labels.conflict_strategies import LabelConflictStrategy
    from src.entities.labels.restore_strategy import FailIfConflictStrategy

    registry = EntityRegistry()

    factory = StrategyFactory(registry)
    strategies = factory.create_restore_strategies(
        conflict_strategy=LabelConflictStrategy.FAIL_IF_CONFLICT
    )

    # Find labels strategy
    labels_strategy = next(s for s in strategies if s.get_entity_name() == "labels")
    assert isinstance(labels_strategy._conflict_strategy, FailIfConflictStrategy)


@pytest.mark.integration
def test_git_repository_requires_git_service():
    """Test that git_repository is skipped without git_service."""
    registry = EntityRegistry()

    factory = StrategyFactory(registry)

    # Without git_service, git_repository should be skipped (returns None)
    strategies = factory.create_save_strategies()  # No git_service provided
    entity_names = [s.get_entity_name() for s in strategies]
    assert "git_repository" not in entity_names

    # Same for restore
    strategies = factory.create_restore_strategies()  # No git_service provided
    entity_names = [s.get_entity_name() for s in strategies]
    assert "git_repository" not in entity_names
