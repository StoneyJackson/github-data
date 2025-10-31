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
