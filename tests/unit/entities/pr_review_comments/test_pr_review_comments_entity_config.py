"""Tests for pr_review_comments entity configuration."""

import pytest
from src.entities.registry import EntityRegistry
from src.entities.pr_review_comments.entity_config import PrReviewCommentsEntityConfig


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


@pytest.mark.unit
def test_pr_review_comments_create_save_strategy():
    """Test save strategy factory method."""
    strategy = PrReviewCommentsEntityConfig.create_save_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "pr_review_comments"


@pytest.mark.unit
def test_pr_review_comments_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    strategy = PrReviewCommentsEntityConfig.create_restore_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "pr_review_comments"
    # Default: include_original_metadata=True
    assert strategy._include_original_metadata is True


@pytest.mark.unit
def test_pr_review_comments_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    strategy = PrReviewCommentsEntityConfig.create_restore_strategy(
        include_original_metadata=False
    )
    assert strategy is not None
    assert strategy._include_original_metadata is False


@pytest.mark.unit
def test_pr_review_comments_factory_ignores_unknown_context():
    """Test that factory methods ignore unknown context keys."""
    strategy = PrReviewCommentsEntityConfig.create_restore_strategy(
        unknown_key="should_be_ignored", include_original_metadata=False
    )
    assert strategy is not None
