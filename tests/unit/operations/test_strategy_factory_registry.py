"""Tests for StrategyFactory with EntityRegistry integration."""

import pytest
from unittest.mock import Mock
from src.operations.strategy_factory import StrategyFactory
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_strategy_factory_accepts_registry():
    """Test that StrategyFactory accepts EntityRegistry parameter."""
    registry = EntityRegistry()
    config = Mock()  # ApplicationConfig for unmigrated entities

    factory = StrategyFactory(registry=registry, config=config)

    assert factory.registry == registry
    assert factory.config == config


@pytest.mark.unit
def test_strategy_factory_loads_labels_from_registry():
    """Test that StrategyFactory loads labels strategy from registry."""
    registry = EntityRegistry()
    config = Mock()
    factory = StrategyFactory(registry=registry, config=config)

    strategy = factory.load_save_strategy("labels")

    assert strategy is not None
    assert strategy.get_entity_name() == "labels"


@pytest.mark.unit
def test_strategy_factory_loads_milestones_from_registry():
    """Test that StrategyFactory loads milestones strategy from registry."""
    registry = EntityRegistry()
    config = Mock()
    factory = StrategyFactory(registry=registry, config=config)

    strategy = factory.load_save_strategy("milestones")

    assert strategy is not None
    assert strategy.get_entity_name() == "milestones"


@pytest.mark.unit
def test_strategy_factory_loads_restore_strategy():
    """Test that StrategyFactory loads restore strategies from registry."""
    from src.entities.labels.conflict_strategies import LabelConflictStrategy

    registry = EntityRegistry()
    config = Mock()
    factory = StrategyFactory(registry=registry, config=config)

    strategy = factory.load_restore_strategy("labels", conflict_strategy=LabelConflictStrategy.OVERWRITE)

    assert strategy is not None
