"""Tests for pr_reviews entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_pr_reviews_entity_discovered():
    """Test pr_reviews entity discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_reviews")

    assert entity.config.name == "pr_reviews"
    assert entity.config.env_var == "INCLUDE_PR_REVIEWS"
    assert entity.config.dependencies == ["pull_requests"]


@pytest.mark.unit
def test_pr_reviews_depends_on_pull_requests():
    """Test pr_reviews depend on pull_requests."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_reviews")

    assert "pull_requests" in entity.get_dependencies()
