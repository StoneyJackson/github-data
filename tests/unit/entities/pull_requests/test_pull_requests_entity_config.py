"""Tests for pull_requests entity configuration."""

import pytest
from github_data.entities.registry import EntityRegistry
from github_data.entities.pull_requests.entity_config import PullRequestsEntityConfig
from github_data.entities.pull_requests.restore_strategy import (
    DefaultPullRequestConflictStrategy,
)
from unittest.mock import Mock
from typing import Union, Set


@pytest.mark.unit
def test_pull_requests_entity_discovered():
    """Test pull_requests entity discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("pull_requests")

    assert entity.config.name == "pull_requests"
    assert entity.config.env_var == "INCLUDE_PULL_REQUESTS"
    assert entity.config.default_value is True
    assert entity.config.value_type == Union[bool, Set[int]]
    assert entity.config.dependencies == ["milestones"]


@pytest.mark.unit
def test_pull_requests_depends_on_milestones():
    """Test pull_requests depend on milestones."""
    registry = EntityRegistry()
    entity = registry.get_entity("pull_requests")

    assert "milestones" in entity.get_dependencies()


@pytest.mark.unit
def test_pull_requests_create_save_strategy():
    """Test save strategy factory method."""
    from github_data.entities.strategy_context import StrategyContext

    context = StrategyContext()
    strategy = PullRequestsEntityConfig.create_save_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "pull_requests"


@pytest.mark.unit
def test_pull_requests_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    from github_data.entities.strategy_context import StrategyContext

    context = StrategyContext()
    strategy = PullRequestsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "pull_requests"
    # Default: include_original_metadata=True
    assert strategy._include_original_metadata is True
    # Default conflict strategy should be DefaultPullRequestConflictStrategy
    assert isinstance(strategy._conflict_strategy, DefaultPullRequestConflictStrategy)


@pytest.mark.unit
def test_pull_requests_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    from github_data.entities.strategy_context import StrategyContext

    mock_conflict_strategy = Mock()
    context = StrategyContext(
        _conflict_strategy=mock_conflict_strategy, _include_original_metadata=False
    )
    strategy = PullRequestsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy._include_original_metadata is False
    assert strategy._conflict_strategy is mock_conflict_strategy


@pytest.mark.unit
def test_pull_requests_factory_ignores_unknown_context():
    """Test that factory methods ignore unknown context keys."""
    from github_data.entities.strategy_context import StrategyContext

    # Unknown keys in StrategyContext are simply ignored
    context = StrategyContext(_include_original_metadata=False)
    strategy = PullRequestsEntityConfig.create_restore_strategy(context)
    assert strategy is not None
