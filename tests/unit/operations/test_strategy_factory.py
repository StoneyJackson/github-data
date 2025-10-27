"""Tests for StrategyFactory."""

import pytest
from unittest.mock import Mock
from src.operations.strategy_factory import StrategyFactory


def test_create_save_strategies_uses_factory_methods(mock_registry):
    """Test that create_save_strategies delegates to entity factory methods."""
    # Setup mock entity with factory method
    mock_entity = Mock()
    mock_entity.config.name = "test_entity"
    mock_entity.config.save_strategy_class = Mock()
    mock_strategy = Mock()
    mock_entity.config.create_save_strategy = Mock(return_value=mock_strategy)

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)

    # Verify factory method was called with context
    mock_entity.config.create_save_strategy.assert_called_once()
    call_kwargs = mock_entity.config.create_save_strategy.call_args[1]
    assert call_kwargs["git_service"] is mock_git_service

    # Verify strategy was added to list
    assert mock_strategy in strategies


def test_create_save_strategies_skips_none_results(mock_registry):
    """Test that None results from factory are skipped."""
    mock_entity = Mock()
    mock_entity.config.name = "test_entity"
    mock_entity.config.save_strategy_class = Mock()
    mock_entity.config.create_save_strategy = Mock(return_value=None)

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)
    strategies = factory.create_save_strategies()

    assert len(strategies) == 0


def test_create_save_strategies_raises_on_factory_error(mock_registry):
    """Test that factory errors are re-raised as RuntimeError."""
    mock_entity = Mock()
    mock_entity.config.name = "failing_entity"
    mock_entity.config.save_strategy_class = Mock()
    mock_entity.config.create_save_strategy = Mock(
        side_effect=ValueError("Missing dependency")
    )

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)

    with pytest.raises(RuntimeError, match="Failed to create save strategy"):
        factory.create_save_strategies()


def test_create_restore_strategies_uses_factory_methods(mock_registry):
    """Test that create_restore_strategies delegates to entity factory methods."""
    mock_entity = Mock()
    mock_entity.config.name = "test_entity"
    mock_entity.config.restore_strategy_class = Mock()
    mock_strategy = Mock()
    mock_entity.config.create_restore_strategy = Mock(return_value=mock_strategy)

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)
    mock_git_service = Mock()
    mock_conflict_strategy = Mock()

    strategies = factory.create_restore_strategies(
        git_service=mock_git_service,
        conflict_strategy=mock_conflict_strategy,
        include_original_metadata=False,
    )

    # Verify factory method was called with all context
    mock_entity.config.create_restore_strategy.assert_called_once()
    call_kwargs = mock_entity.config.create_restore_strategy.call_args[1]
    assert call_kwargs["git_service"] is mock_git_service
    assert call_kwargs["conflict_strategy"] is mock_conflict_strategy
    assert call_kwargs["include_original_metadata"] is False

    assert mock_strategy in strategies


def test_create_restore_strategies_raises_on_factory_error(mock_registry):
    """Test that factory errors are re-raised as RuntimeError."""
    mock_entity = Mock()
    mock_entity.config.name = "failing_entity"
    mock_entity.config.restore_strategy_class = Mock()
    mock_entity.config.create_restore_strategy = Mock(
        side_effect=ValueError("Missing dependency")
    )

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)

    with pytest.raises(RuntimeError, match="Failed to create restore strategy"):
        factory.create_restore_strategies()


@pytest.fixture
def mock_registry():
    """Provide mock EntityRegistry."""
    return Mock()
