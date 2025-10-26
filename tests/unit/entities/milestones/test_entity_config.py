"""Tests for milestones entity configuration."""

import pytest
from src.entities.milestones.entity_config import MilestonesEntityConfig


def test_milestones_create_save_strategy():
    """Test save strategy factory method."""
    strategy = MilestonesEntityConfig.create_save_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "milestones"


def test_milestones_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    strategy = MilestonesEntityConfig.create_restore_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "milestones"
    # Milestones restore strategy has no include_original_metadata (no constructor params)


def test_milestones_factory_ignores_unknown_context():
    """Test that factory methods ignore unknown context keys."""
    strategy = MilestonesEntityConfig.create_restore_strategy(
        unknown_key="should_be_ignored",
        include_original_metadata=False  # Should be ignored
    )
    assert strategy is not None
