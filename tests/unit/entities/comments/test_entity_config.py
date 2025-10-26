"""Tests for comments entity configuration."""

import pytest
from src.entities.comments.entity_config import CommentsEntityConfig


def test_comments_create_save_strategy():
    """Test save strategy factory method."""
    strategy = CommentsEntityConfig.create_save_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "comments"


def test_comments_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    strategy = CommentsEntityConfig.create_restore_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "comments"
    # Default: include_original_metadata=True
    assert strategy._include_original_metadata is True


def test_comments_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    strategy = CommentsEntityConfig.create_restore_strategy(
        include_original_metadata=False
    )
    assert strategy is not None
    assert strategy._include_original_metadata is False


def test_comments_factory_ignores_unknown_context():
    """Test that factory methods ignore unknown context keys."""
    strategy = CommentsEntityConfig.create_restore_strategy(
        unknown_key="should_be_ignored",
        include_original_metadata=False
    )
    assert strategy is not None
