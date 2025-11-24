"""Tests for comments entity configuration."""

from github_data.entities.comments.entity_config import CommentsEntityConfig
from github_data.entities.strategy_context import StrategyContext


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


def test_comments_config_declares_github_api_operations():
    """Comments config should declare github_api_operations."""
    assert hasattr(CommentsEntityConfig, "github_api_operations")

    ops = CommentsEntityConfig.github_api_operations
    assert "get_issue_comments" in ops
    assert "get_all_issue_comments" in ops
    assert "create_issue_comment" in ops

    # Validate read operations
    assert ops["get_issue_comments"]["boundary_method"] == "get_issue_comments"
    assert ops["get_issue_comments"]["converter"] == "convert_to_comment"
    assert ops["get_all_issue_comments"]["boundary_method"] == "get_all_issue_comments"
    assert ops["get_all_issue_comments"]["converter"] == "convert_to_comment"

    # Validate write operation
    assert ops["create_issue_comment"]["boundary_method"] == "create_issue_comment"
