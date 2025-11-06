"""Tests for sub_issues entity configuration."""

from github_data.entities.sub_issues.entity_config import SubIssuesEntityConfig
from github_data.entities.strategy_context import StrategyContext


def test_sub_issues_create_save_strategy():
    """Test save strategy factory method."""
    context = StrategyContext()
    strategy = SubIssuesEntityConfig.create_save_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "sub_issues"


def test_sub_issues_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    context = StrategyContext()
    strategy = SubIssuesEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "sub_issues"
    assert strategy._include_original_metadata is True


def test_sub_issues_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    context = StrategyContext(_include_original_metadata=False)
    strategy = SubIssuesEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy._include_original_metadata is False


def test_sub_issues_config_declares_github_api_operations():
    """Sub-issues config should declare github_api_operations."""
    assert hasattr(SubIssuesEntityConfig, "github_api_operations")

    ops = SubIssuesEntityConfig.github_api_operations
    assert "get_repository_sub_issues" in ops
    assert "get_issue_sub_issues" in ops
    assert "add_sub_issue" in ops
    assert "remove_sub_issue" in ops
    assert "reprioritize_sub_issue" in ops

    # Validate read operations
    assert (
        ops["get_repository_sub_issues"]["boundary_method"]
        == "get_repository_sub_issues"
    )
    assert ops["get_repository_sub_issues"]["converter"] == "convert_to_sub_issue"
    assert ops["get_issue_sub_issues"]["boundary_method"] == "get_issue_sub_issues"

    # Validate write operations
    assert ops["add_sub_issue"]["boundary_method"] == "add_sub_issue"
    assert ops["remove_sub_issue"]["boundary_method"] == "remove_sub_issue"
    assert ops["reprioritize_sub_issue"]["boundary_method"] == "reprioritize_sub_issue"
