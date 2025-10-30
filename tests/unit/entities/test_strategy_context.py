"""Tests for StrategyContext."""

import pytest
from unittest.mock import Mock


def test_service_property_returns_value_when_set():
    """Test that service_property returns the service when set."""
    from github_data.entities.strategy_context import StrategyContext

    mock_git_service = Mock()
    context = StrategyContext(_git_service=mock_git_service)

    assert context.git_service is mock_git_service


def test_service_property_raises_when_none():
    """Test that service_property raises RuntimeError when service is None."""
    from github_data.entities.strategy_context import StrategyContext

    context = StrategyContext()

    with pytest.raises(
        RuntimeError, match="git_service is required but was not provided"
    ):
        _ = context.git_service


def test_github_service_property_returns_value_when_set():
    """Test that github_service property returns the service when set."""
    from github_data.entities.strategy_context import StrategyContext

    mock_github_service = Mock()
    context = StrategyContext(_github_service=mock_github_service)

    assert context.github_service is mock_github_service


def test_github_service_property_raises_when_none():
    """Test that github_service property raises when None."""
    from github_data.entities.strategy_context import StrategyContext

    context = StrategyContext()

    with pytest.raises(
        RuntimeError, match="github_service is required but was not provided"
    ):
        _ = context.github_service


def test_conflict_strategy_property_returns_value_when_set():
    """Test that conflict_strategy property returns the strategy when set."""
    from github_data.entities.strategy_context import StrategyContext

    mock_strategy = Mock()
    context = StrategyContext(_conflict_strategy=mock_strategy)

    assert context.conflict_strategy is mock_strategy


def test_conflict_strategy_property_raises_when_none():
    """Test that conflict_strategy property raises when None."""
    from github_data.entities.strategy_context import StrategyContext

    context = StrategyContext()

    with pytest.raises(
        RuntimeError, match="conflict_strategy is required but was not provided"
    ):
        _ = context.conflict_strategy


def test_include_original_metadata_has_default_value():
    """Test that include_original_metadata has a default value."""
    from github_data.entities.strategy_context import StrategyContext

    context = StrategyContext()

    assert context.include_original_metadata is True


def test_include_original_metadata_can_be_set():
    """Test that include_original_metadata can be set."""
    from github_data.entities.strategy_context import StrategyContext

    context = StrategyContext(_include_original_metadata=False)

    assert context.include_original_metadata is False


def test_multiple_services_can_be_set():
    """Test that multiple services can be set and accessed."""
    from github_data.entities.strategy_context import StrategyContext

    mock_git = Mock()
    mock_github = Mock()
    mock_conflict = Mock()

    context = StrategyContext(
        _git_service=mock_git,
        _github_service=mock_github,
        _conflict_strategy=mock_conflict,
        _include_original_metadata=False,
    )

    assert context.git_service is mock_git
    assert context.github_service is mock_github
    assert context.conflict_strategy is mock_conflict
    assert context.include_original_metadata is False
