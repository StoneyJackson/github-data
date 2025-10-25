"""Tests for issues entity configuration."""

import pytest
from src.entities.registry import EntityRegistry
from typing import Union, Set


@pytest.mark.unit
def test_issues_entity_discovered():
    """Test that issues entity is discovered by registry."""
    registry = EntityRegistry()
    entity = registry.get_entity("issues")

    assert entity.config.name == "issues"
    assert entity.config.env_var == "INCLUDE_ISSUES"
    assert entity.config.default_value is True
    assert entity.config.value_type == Union[bool, Set[int]]
    assert entity.config.dependencies == ["milestones"]
    assert entity.config.description != ""


@pytest.mark.unit
def test_issues_depends_on_milestones():
    """Test that issues entity depends on milestones."""
    registry = EntityRegistry()
    entity = registry.get_entity("issues")

    assert "milestones" in entity.get_dependencies()


@pytest.mark.unit
def test_issues_disabled_when_milestones_disabled():
    """Test that issues auto-disable when milestones disabled (non-strict mode)."""
    import os

    # Set environment to disable milestones
    os.environ["INCLUDE_MILESTONES"] = "false"
    os.environ["INCLUDE_ISSUES"] = "true"

    registry = EntityRegistry.from_environment(strict=False)
    issues_entity = registry.get_entity("issues")

    # Issues should be auto-disabled with warning
    assert issues_entity.is_enabled() is False

    # Cleanup
    del os.environ["INCLUDE_MILESTONES"]
    del os.environ["INCLUDE_ISSUES"]
