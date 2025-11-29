"""Tests for pr_comments entity configuration."""

import pytest
from github_data_core.entities.registry import EntityRegistry
from github_data_tools.entities.pr_comments.entity_config import PrCommentsEntityConfig
from github_data_tools.entities.pr_comments.restore_strategy import (
    DefaultPRCommentConflictStrategy,
)
from unittest.mock import Mock


@pytest.mark.unit
def test_pr_comments_entity_discovered():
    """Test pr_comments entity discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_comments")

    assert entity.config.name == "pr_comments"
    assert entity.config.env_var == "INCLUDE_PULL_REQUEST_COMMENTS"
    assert entity.config.dependencies == ["pull_requests"]


@pytest.mark.unit
def test_pr_comments_depends_on_pull_requests():
    """Test pr_comments depend on pull_requests."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_comments")

    assert "pull_requests" in entity.get_dependencies()


@pytest.mark.unit
def test_pr_comments_create_save_strategy():
    """Test save strategy factory method."""
    from github_data_core.entities.strategy_context import StrategyContext

    context = StrategyContext()
    strategy = PrCommentsEntityConfig.create_save_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "pr_comments"


@pytest.mark.unit
def test_pr_comments_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    from github_data_core.entities.strategy_context import StrategyContext

    context = StrategyContext()
    strategy = PrCommentsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "pr_comments"
    # Default: include_original_metadata=True
    assert strategy._include_original_metadata is True
    # Default conflict strategy should be DefaultPRCommentConflictStrategy
    assert isinstance(strategy._conflict_strategy, DefaultPRCommentConflictStrategy)


@pytest.mark.unit
def test_pr_comments_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    from github_data_core.entities.strategy_context import StrategyContext

    mock_conflict_strategy = Mock()
    context = StrategyContext(
        _conflict_strategy=mock_conflict_strategy, _include_original_metadata=False
    )
    strategy = PrCommentsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy._include_original_metadata is False
    assert strategy._conflict_strategy is mock_conflict_strategy


@pytest.mark.unit
def test_pr_comments_factory_ignores_unknown_context():
    """Test that factory methods ignore unknown context keys."""
    from github_data_core.entities.strategy_context import StrategyContext

    # Unknown keys in StrategyContext are simply ignored
    context = StrategyContext(_include_original_metadata=False)
    strategy = PrCommentsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
