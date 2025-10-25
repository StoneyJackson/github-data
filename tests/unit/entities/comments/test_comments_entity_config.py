"""Tests for comments entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_comments_entity_discovered():
    """Test that comments entity is discovered by registry."""
    registry = EntityRegistry()
    entity = registry.get_entity("comments")

    assert entity.config.name == "comments"
    assert entity.config.env_var == "INCLUDE_ISSUE_COMMENTS"
    assert entity.config.default_value is True
    assert entity.config.dependencies == ["issues"]


@pytest.mark.unit
def test_comments_depends_on_issues():
    """Test that comments depend on issues."""
    registry = EntityRegistry()
    entity = registry.get_entity("comments")

    assert "issues" in entity.get_dependencies()


@pytest.mark.unit
def test_comments_disabled_when_issues_disabled():
    """Test comments auto-disable when issues disabled."""
    import os

    os.environ["INCLUDE_ISSUES"] = "false"
    os.environ["INCLUDE_ISSUE_COMMENTS"] = "true"

    registry = EntityRegistry.from_environment(strict=False)
    comments = registry.get_entity("comments")

    assert comments.is_enabled() is False

    del os.environ["INCLUDE_ISSUES"]
    del os.environ["INCLUDE_ISSUE_COMMENTS"]
