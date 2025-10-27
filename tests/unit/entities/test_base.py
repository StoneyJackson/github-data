"""Tests for entity base protocols."""

import pytest
from typing import Optional
from src.entities.base import EntityConfig


def test_entity_config_has_factory_methods():
    """Verify EntityConfig protocol defines factory methods."""
    # This test validates protocol structure
    assert hasattr(EntityConfig, "create_save_strategy")
    assert hasattr(EntityConfig, "create_restore_strategy")


class MinimalTestConfig:
    """Minimal config for testing protocol compliance."""

    name = "test"
    env_var = "INCLUDE_TEST"
    default_value = True
    value_type = bool
    dependencies = []
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Test config"

    @staticmethod
    def create_save_strategy(**context):
        return None

    @staticmethod
    def create_restore_strategy(**context):
        return None


def test_config_implements_protocol():
    """Test that minimal config satisfies protocol."""
    config = MinimalTestConfig()
    assert config.name == "test"

    # Factory methods should be callable
    result = config.create_save_strategy()
    assert result is None

    result = config.create_restore_strategy()
    assert result is None


def test_factory_methods_accept_context():
    """Verify factory methods accept **context kwargs."""
    config = MinimalTestConfig()

    # Should accept arbitrary context
    result = config.create_save_strategy(git_service="test")
    assert result is None

    result = config.create_restore_strategy(
        git_service="test", conflict_strategy="skip", include_original_metadata=True
    )
    assert result is None
