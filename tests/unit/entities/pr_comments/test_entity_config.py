"""Tests for pr_comments entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_pr_comments_entity_discovered():
    """Test pr_comments entity discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_comments")

    assert entity.config.name == "pr_comments"
    assert entity.config.env_var == "INCLUDE_PULL_REQUEST_COMMENTS"
    assert entity.config.dependencies == ["pull_requests"]


@pytest.mark.unit
def test_pr_comments_depends_on_pull_requests():
    """Test pr_comments depend on pull_requests."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_comments")

    assert "pull_requests" in entity.get_dependencies()
