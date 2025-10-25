"""Tests for sub_issues entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_sub_issues_entity_discovered():
    """Test that sub_issues entity is discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("sub_issues")

    assert entity.config.name == "sub_issues"
    assert entity.config.env_var == "INCLUDE_SUB_ISSUES"
    assert entity.config.dependencies == ["issues"]


@pytest.mark.unit
def test_sub_issues_depends_on_issues():
    """Test that sub_issues depend on issues."""
    registry = EntityRegistry()
    entity = registry.get_entity("sub_issues")

    assert "issues" in entity.get_dependencies()
