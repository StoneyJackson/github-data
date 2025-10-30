"""Tests for comments entity configuration."""

from unittest.mock import Mock
from src.entities.comments.entity_config import CommentsEntityConfig
from src.entities.strategy_context import StrategyContext


def test_comments_create_save_strategy():
    """Test save strategy factory method."""
    context = StrategyContext()
    strategy = CommentsEntityConfig.create_save_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "comments"


def test_comments_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    context = StrategyContext()
    strategy = CommentsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "comments"
    # Default: include_original_metadata=True
    assert strategy._include_original_metadata is True


def test_comments_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    context = StrategyContext(_include_original_metadata=False)
    strategy = CommentsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy._include_original_metadata is False


def test_comments_factory_ignores_unknown_context():
    """Test that factory methods ignore unknown context keys."""
    # Unknown keys in StrategyContext are simply ignored
    context = StrategyContext(_include_original_metadata=False)
    strategy = CommentsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
