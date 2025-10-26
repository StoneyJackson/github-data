"""Tests for git_repositories entity configuration."""

import pytest
from unittest.mock import Mock
from src.entities.git_repositories.entity_config import GitRepositoryEntityConfig


def test_git_repository_create_save_strategy_requires_git_service():
    """Test that save strategy requires git_service."""
    with pytest.raises(ValueError, match="git_service"):
        GitRepositoryEntityConfig.create_save_strategy()


def test_git_repository_create_save_strategy_with_service():
    """Test save strategy creation with git_service."""
    mock_service = Mock()
    strategy = GitRepositoryEntityConfig.create_save_strategy(git_service=mock_service)
    assert strategy is not None
    assert strategy._git_service is mock_service


def test_git_repository_create_restore_strategy_requires_git_service():
    """Test that restore strategy requires git_service."""
    with pytest.raises(ValueError, match="git_service"):
        GitRepositoryEntityConfig.create_restore_strategy()


def test_git_repository_create_restore_strategy_with_service():
    """Test restore strategy creation with git_service."""
    mock_service = Mock()
    strategy = GitRepositoryEntityConfig.create_restore_strategy(git_service=mock_service)
    assert strategy is not None
    assert strategy._git_service is mock_service


def test_git_repository_factory_ignores_other_context():
    """Test that factory ignores irrelevant context keys."""
    mock_service = Mock()
    strategy = GitRepositoryEntityConfig.create_restore_strategy(
        git_service=mock_service,
        include_original_metadata=True,  # Should be ignored
        conflict_strategy="skip"  # Should be ignored
    )
    assert strategy is not None
