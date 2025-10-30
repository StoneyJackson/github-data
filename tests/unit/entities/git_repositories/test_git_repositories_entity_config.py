"""Tests for git_repositories entity configuration."""

from unittest.mock import Mock
from github_data.entities.git_repositories.entity_config import GitRepositoryEntityConfig
from github_data.entities.strategy_context import StrategyContext


def test_git_repository_create_save_strategy_without_git_service():
    """Test that save strategy is created with git_service from context."""
    mock_service = Mock()
    context = StrategyContext(_git_service=mock_service)
    strategy = GitRepositoryEntityConfig.create_save_strategy(context)
    assert strategy is not None
    assert strategy._git_service is mock_service


def test_git_repository_create_save_strategy_with_service():
    """Test save strategy creation with git_service."""
    mock_service = Mock()
    context = StrategyContext(_git_service=mock_service)
    strategy = GitRepositoryEntityConfig.create_save_strategy(context)
    assert strategy is not None
    assert strategy._git_service is mock_service


def test_git_repository_create_restore_strategy_without_git_service():
    """Test that restore strategy is created with git_service from context."""
    mock_service = Mock()
    context = StrategyContext(_git_service=mock_service)
    strategy = GitRepositoryEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy._git_service is mock_service


def test_git_repository_create_restore_strategy_with_service():
    """Test restore strategy creation with git_service."""
    mock_service = Mock()
    context = StrategyContext(_git_service=mock_service)
    strategy = GitRepositoryEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy._git_service is mock_service


def test_git_repository_factory_ignores_other_context():
    """Test that factory ignores irrelevant context keys."""
    mock_service = Mock()
    context = StrategyContext(
        _git_service=mock_service,
        _include_original_metadata=True,
        _conflict_strategy="skip",
    )
    strategy = GitRepositoryEntityConfig.create_restore_strategy(context)
    assert strategy is not None
