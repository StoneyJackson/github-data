"""Tests for issues entity configuration."""

from unittest.mock import Mock
from src.entities.issues.entity_config import IssuesEntityConfig
from src.entities.strategy_context import StrategyContext


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
