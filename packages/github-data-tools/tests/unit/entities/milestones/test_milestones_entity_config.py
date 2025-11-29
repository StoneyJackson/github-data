"""Tests for milestones entity configuration."""

from github_data_tools.entities.milestones.entity_config import MilestonesEntityConfig
from github_data_core.entities.strategy_context import StrategyContext


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


def test_milestones_config_declares_github_api_operations():
    """Milestones config should declare github_api_operations."""
    assert hasattr(MilestonesEntityConfig, "github_api_operations")

    ops = MilestonesEntityConfig.github_api_operations
    assert "get_repository_milestones" in ops
    assert "create_milestone" in ops

    # Validate read operation
    assert (
        ops["get_repository_milestones"]["boundary_method"]
        == "get_repository_milestones"
    )
    assert ops["get_repository_milestones"]["converter"] == "convert_to_milestone"

    # Validate write operation
    assert ops["create_milestone"]["boundary_method"] == "create_milestone"
