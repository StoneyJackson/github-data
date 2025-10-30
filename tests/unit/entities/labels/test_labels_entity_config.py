"""Tests for labels entity configuration."""

from unittest.mock import Mock
from github_data.entities.labels.entity_config import LabelsEntityConfig
from github_data.entities.labels.conflict_strategies import LabelConflictStrategy
from github_data.entities.strategy_context import StrategyContext


def test_labels_create_save_strategy():
    """Test save strategy factory method."""
    context = StrategyContext()
    strategy = LabelsEntityConfig.create_save_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "labels"


def test_labels_create_restore_strategy_default():
    """Test restore strategy factory with default conflict strategy."""
    mock_github_service = Mock()
    context = StrategyContext(_github_service=mock_github_service)
    strategy = LabelsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "labels"
    # Default should be SKIP strategy - verify by class name to avoid circular import
    assert strategy._conflict_strategy.__class__.__name__ == "SkipConflictStrategy"


def test_labels_create_restore_strategy_custom():
    """Test restore strategy factory with custom conflict strategy."""
    # OVERWRITE strategy requires github_service
    mock_github_service = Mock()
    context = StrategyContext(
        _conflict_strategy=LabelConflictStrategy.OVERWRITE,
        _github_service=mock_github_service,
    )
    strategy = LabelsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    # Should be OverwriteConflictStrategy instance - check by class name
    assert strategy._conflict_strategy.__class__.__name__ == "OverwriteConflictStrategy"


def test_labels_create_restore_strategy_ignores_metadata():
    """Test that labels factory ignores include_original_metadata."""
    # Labels don't use this parameter
    mock_github_service = Mock()
    context = StrategyContext(
        _include_original_metadata=False,
        _conflict_strategy=LabelConflictStrategy.SKIP,
        _github_service=mock_github_service,
    )
    strategy = LabelsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy._conflict_strategy.__class__.__name__ == "SkipConflictStrategy"
