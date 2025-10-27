"""Tests for labels entity configuration."""

from unittest.mock import Mock
from src.entities.labels.entity_config import LabelsEntityConfig
from src.entities.labels.conflict_strategies import LabelConflictStrategy


def test_labels_create_save_strategy():
    """Test save strategy factory method."""
    strategy = LabelsEntityConfig.create_save_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "labels"


def test_labels_create_restore_strategy_default():
    """Test restore strategy factory with default conflict strategy."""
    strategy = LabelsEntityConfig.create_restore_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "labels"
    # Default should be SKIP strategy - verify by class name to avoid circular import
    assert strategy._conflict_strategy.__class__.__name__ == "SkipConflictStrategy"


def test_labels_create_restore_strategy_custom():
    """Test restore strategy factory with custom conflict strategy."""
    # OVERWRITE strategy requires github_service
    mock_github_service = Mock()
    strategy = LabelsEntityConfig.create_restore_strategy(
        conflict_strategy=LabelConflictStrategy.OVERWRITE,
        github_service=mock_github_service,
    )
    assert strategy is not None
    # Should be OverwriteConflictStrategy instance - check by class name
    assert strategy._conflict_strategy.__class__.__name__ == "OverwriteConflictStrategy"


def test_labels_create_restore_strategy_ignores_metadata():
    """Test that labels factory ignores include_original_metadata."""
    # Labels don't use this parameter
    strategy = LabelsEntityConfig.create_restore_strategy(
        include_original_metadata=False, conflict_strategy=LabelConflictStrategy.SKIP
    )
    assert strategy is not None
    assert strategy._conflict_strategy.__class__.__name__ == "SkipConflictStrategy"
