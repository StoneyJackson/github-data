"""Tests for sub_issues entity configuration."""

import pytest
from src.entities.sub_issues.entity_config import SubIssuesEntityConfig


def test_sub_issues_create_save_strategy():
    """Test save strategy factory method."""
    strategy = SubIssuesEntityConfig.create_save_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "sub_issues"


def test_sub_issues_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    strategy = SubIssuesEntityConfig.create_restore_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "sub_issues"
    assert strategy._include_original_metadata is True


def test_sub_issues_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    strategy = SubIssuesEntityConfig.create_restore_strategy(
        include_original_metadata=False
    )
    assert strategy is not None
    assert strategy._include_original_metadata is False
