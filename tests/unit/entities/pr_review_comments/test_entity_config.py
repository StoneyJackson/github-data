"""Tests for pr_review_comments entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_pr_review_comments_entity_discovered():
    """Test pr_review_comments entity discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_review_comments")

    assert entity.config.name == "pr_review_comments"
    assert entity.config.env_var == "INCLUDE_PR_REVIEW_COMMENTS"
    assert entity.config.dependencies == ["pr_reviews"]


@pytest.mark.unit
def test_pr_review_comments_depends_on_pr_reviews():
    """Test pr_review_comments depend on pr_reviews."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_review_comments")

    assert "pr_reviews" in entity.get_dependencies()
