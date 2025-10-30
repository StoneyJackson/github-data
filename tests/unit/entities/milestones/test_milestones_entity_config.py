"""Tests for milestones entity configuration."""

from unittest.mock import Mock
from src.entities.milestones.entity_config import MilestonesEntityConfig
from src.entities.strategy_context import StrategyContext


def test_milestones_create_save_strategy():
    """Test save strategy factory method."""
    context = StrategyContext()
    strategy = MilestonesEntityConfig.create_save_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "milestones"


def test_milestones_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    context = StrategyContext()
    strategy = MilestonesEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "milestones"
    # Milestones restore strategy has no include_original_metadata
    # (no constructor params)


def test_milestones_factory_ignores_unknown_context():
    """Test that factory methods ignore unknown context keys."""
    # Unknown keys in StrategyContext are simply ignored
    context = StrategyContext(_include_original_metadata=False)
    strategy = MilestonesEntityConfig.create_restore_strategy(context)
    assert strategy is not None
