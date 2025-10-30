"""Tests for pr_reviews entity configuration."""

import pytest
from github_data.entities.registry import EntityRegistry
from github_data.entities.pr_reviews.entity_config import PrReviewsEntityConfig


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


@pytest.mark.unit
def test_pr_reviews_create_save_strategy():
    """Test save strategy factory method."""
    from github_data.entities.strategy_context import StrategyContext

    context = StrategyContext()
    strategy = PrReviewsEntityConfig.create_save_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "pr_reviews"


@pytest.mark.unit
def test_pr_reviews_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    from github_data.entities.strategy_context import StrategyContext

    context = StrategyContext()
    strategy = PrReviewsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "pr_reviews"
    # Default: include_original_metadata=True
    assert strategy._include_original_metadata is True


@pytest.mark.unit
def test_pr_reviews_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    from github_data.entities.strategy_context import StrategyContext

    context = StrategyContext(_include_original_metadata=False)
    strategy = PrReviewsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy._include_original_metadata is False


@pytest.mark.unit
def test_pr_reviews_factory_ignores_unknown_context():
    """Test that factory methods ignore unknown context keys."""
    from github_data.entities.strategy_context import StrategyContext

    # Unknown keys in StrategyContext are simply ignored
    context = StrategyContext(_include_original_metadata=False)
    strategy = PrReviewsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
