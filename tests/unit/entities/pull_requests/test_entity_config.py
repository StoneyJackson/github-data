"""Tests for pull_requests entity configuration."""

import pytest
from src.entities.registry import EntityRegistry
from src.entities.pull_requests.entity_config import PullRequestsEntityConfig
from src.entities.pull_requests.restore_strategy import DefaultPullRequestConflictStrategy
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
    strategy = PullRequestsEntityConfig.create_save_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "pull_requests"


@pytest.mark.unit
def test_pull_requests_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    strategy = PullRequestsEntityConfig.create_restore_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "pull_requests"
    # Default: include_original_metadata=True
    assert strategy._include_original_metadata is True
    # Default conflict strategy should be DefaultPullRequestConflictStrategy
    assert isinstance(strategy._conflict_strategy, DefaultPullRequestConflictStrategy)


@pytest.mark.unit
def test_pull_requests_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    mock_conflict_strategy = Mock()
    strategy = PullRequestsEntityConfig.create_restore_strategy(
        include_original_metadata=False,
        conflict_strategy=mock_conflict_strategy
    )
    assert strategy is not None
    assert strategy._include_original_metadata is False
    assert strategy._conflict_strategy is mock_conflict_strategy


@pytest.mark.unit
def test_pull_requests_factory_ignores_unknown_context():
    """Test that factory methods ignore unknown context keys."""
    strategy = PullRequestsEntityConfig.create_restore_strategy(
        unknown_key="should_be_ignored",
        include_original_metadata=False
    )
    assert strategy is not None
