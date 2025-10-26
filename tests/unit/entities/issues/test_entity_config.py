"""Tests for issues entity configuration."""

import pytest
from src.entities.issues.entity_config import IssuesEntityConfig


def test_issues_create_save_strategy():
    """Test save strategy factory method."""
    strategy = IssuesEntityConfig.create_save_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "issues"


def test_issues_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    strategy = IssuesEntityConfig.create_restore_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "issues"
    assert strategy._include_original_metadata is True


def test_issues_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    strategy = IssuesEntityConfig.create_restore_strategy(
        include_original_metadata=False
    )
    assert strategy is not None
    assert strategy._include_original_metadata is False
