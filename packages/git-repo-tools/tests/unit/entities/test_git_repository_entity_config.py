"""Tests for git_repository entity configuration."""

import importlib

import pytest
from github_data.entities.registry import EntityRegistry


@pytest.mark.unit
def test_git_repository_entity_discovered():
    """Test that git_repository entity is discovered by registry."""
    registry = EntityRegistry()
    entity = registry.get_entity("git_repository")

    assert entity.config.name == "git_repository"
    assert entity.config.env_var == "INCLUDE_GIT_REPO"
    assert entity.config.default_value is True
    assert entity.config.value_type == bool
    assert entity.config.dependencies == []
    assert entity.config.description != ""


@pytest.mark.unit
def test_git_repository_entity_no_dependencies():
    """Test that git_repository entity has no dependencies."""
    registry = EntityRegistry()
    entity = registry.get_entity("git_repository")

    assert entity.get_dependencies() == []


@pytest.mark.unit
def test_git_repository_entity_enabled_by_default():
    """Test that git_repository entity is enabled by default."""
    registry = EntityRegistry()
    entity = registry.get_entity("git_repository")

    assert entity.is_enabled() is True


@pytest.mark.unit
def test_git_repository_save_strategy_exists():
    """Test that git_repository save strategy exists at expected location."""
    module = importlib.import_module(
        "github_data.entities.git_repositories.save_strategy"
    )
    strategy_class = getattr(module, "GitRepositorySaveStrategy")
    assert strategy_class is not None


@pytest.mark.unit
def test_git_repository_restore_strategy_exists():
    """Test that git_repository restore strategy exists at expected location."""
    module = importlib.import_module(
        "github_data.entities.git_repositories.restore_strategy"
    )
    strategy_class = getattr(module, "GitRepositoryRestoreStrategy")
    assert strategy_class is not None
