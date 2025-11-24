"""Tests for issues entity configuration."""

from github_data_tools.entities.issues.entity_config import IssuesEntityConfig
from github_data_core.entities.strategy_context import StrategyContext


def test_issues_create_save_strategy():
    """Test save strategy factory method."""
    context = StrategyContext()
    strategy = IssuesEntityConfig.create_save_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "issues"


def test_issues_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    context = StrategyContext()
    strategy = IssuesEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "issues"
    assert strategy._include_original_metadata is True


def test_issues_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    context = StrategyContext(_include_original_metadata=False)
    strategy = IssuesEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy._include_original_metadata is False


def test_issues_config_declares_github_api_operations():
    """Issues config should declare github_api_operations."""
    assert hasattr(IssuesEntityConfig, "github_api_operations")

    ops = IssuesEntityConfig.github_api_operations
    assert "get_repository_issues" in ops
    assert "create_issue" in ops
    assert "close_issue" in ops

    # Validate read operation
    assert ops["get_repository_issues"]["boundary_method"] == "get_repository_issues"
    assert ops["get_repository_issues"]["converter"] == "convert_to_issue"

    # Validate write operations
    assert ops["create_issue"]["boundary_method"] == "create_issue"
    assert ops["close_issue"]["boundary_method"] == "close_issue"
