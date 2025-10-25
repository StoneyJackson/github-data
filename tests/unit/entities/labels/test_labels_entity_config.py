"""Tests for labels entity configuration."""

import importlib

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_labels_entity_discovered():
    """Test that labels entity is discovered by registry."""
    registry = EntityRegistry()
    entity = registry.get_entity("labels")

    assert entity.config.name == "labels"
    assert entity.config.env_var == "INCLUDE_LABELS"
    assert entity.config.default_value is True
    assert entity.config.value_type == bool
    assert entity.config.dependencies == []
    assert entity.config.description != ""


@pytest.mark.unit
def test_labels_entity_no_dependencies():
    """Test that labels entity has no dependencies."""
    registry = EntityRegistry()
    entity = registry.get_entity("labels")

    assert entity.get_dependencies() == []


@pytest.mark.unit
def test_labels_entity_enabled_by_default():
    """Test that labels entity is enabled by default."""
    registry = EntityRegistry()
    entity = registry.get_entity("labels")

    assert entity.is_enabled() is True


@pytest.mark.unit
def test_labels_save_strategy_exists():
    """Test that labels save strategy exists at expected location."""
    module = importlib.import_module("src.entities.labels.save_strategy")
    strategy_class = getattr(module, "LabelsSaveStrategy")
    assert strategy_class is not None


@pytest.mark.unit
def test_labels_restore_strategy_exists():
    """Test that labels restore strategy exists at expected location."""
    module = importlib.import_module("src.entities.labels.restore_strategy")
    strategy_class = getattr(module, "LabelsRestoreStrategy")
    assert strategy_class is not None
