"""Tests for milestones entity configuration."""

import importlib

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_milestones_entity_discovered():
    """Test that milestones entity is discovered by registry."""
    registry = EntityRegistry()
    entity = registry.get_entity("milestones")

    assert entity.config.name == "milestones"
    assert entity.config.env_var == "INCLUDE_MILESTONES"
    assert entity.config.default_value is True
    assert entity.config.value_type == bool
    assert entity.config.dependencies == []
    assert entity.config.description != ""


@pytest.mark.unit
def test_milestones_entity_no_dependencies():
    """Test that milestones entity has no dependencies."""
    registry = EntityRegistry()
    entity = registry.get_entity("milestones")

    assert entity.get_dependencies() == []


@pytest.mark.unit
def test_milestones_entity_enabled_by_default():
    """Test that milestones entity is enabled by default."""
    registry = EntityRegistry()
    entity = registry.get_entity("milestones")

    assert entity.is_enabled() is True


@pytest.mark.unit
def test_milestones_save_strategy_exists():
    """Test that milestones save strategy exists at expected location."""
    module = importlib.import_module("src.entities.milestones.save_strategy")
    strategy_class = getattr(module, "MilestonesSaveStrategy")
    assert strategy_class is not None


@pytest.mark.unit
def test_milestones_restore_strategy_exists():
    """Test that milestones restore strategy exists at expected location."""
    module = importlib.import_module("src.entities.milestones.restore_strategy")
    strategy_class = getattr(module, "MilestonesRestoreStrategy")
    assert strategy_class is not None
