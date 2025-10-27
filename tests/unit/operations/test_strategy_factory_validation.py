"""Tests for StrategyFactory service requirement validation."""

import pytest
from unittest.mock import Mock
from src.operations.strategy_factory import StrategyFactory
from src.entities.strategy_context import StrategyContext


def test_validate_requirements_passes_when_service_available():
    """Test that validation passes when required service is available."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "test_entity"
    mock_config.required_services_save = ["git_service"]

    mock_git_service = Mock()
    context = StrategyContext(_git_service=mock_git_service)

    # Should not raise
    factory._validate_requirements(mock_config, context, "save")


def test_validate_requirements_raises_when_service_missing():
    """Test that validation raises RuntimeError when service missing."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "git_repository"
    mock_config.required_services_save = ["git_service"]

    context = StrategyContext()  # No services

    with pytest.raises(
        RuntimeError,
        match="Entity 'git_repository' requires 'git_service' for save operation",
    ):
        factory._validate_requirements(mock_config, context, "save")


def test_validate_requirements_checks_restore_requirements():
    """Test that validation checks restore-specific requirements."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "labels"
    mock_config.required_services_restore = ["conflict_strategy"]

    context = StrategyContext()  # No conflict_strategy

    with pytest.raises(
        RuntimeError,
        match="Entity 'labels' requires 'conflict_strategy' for restore operation",
    ):
        factory._validate_requirements(mock_config, context, "restore")


def test_validate_requirements_handles_missing_attribute():
    """Test backward compatibility when config has no requirements."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "legacy_entity"
    # No required_services_save attribute
    del mock_config.required_services_save

    context = StrategyContext()

    # Should not raise - defaults to empty list
    factory._validate_requirements(mock_config, context, "save")


def test_validate_requirements_checks_multiple_services():
    """Test that validation checks all required services."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "complex_entity"
    mock_config.required_services_save = ["git_service", "github_service"]

    mock_git = Mock()
    context = StrategyContext(_git_service=mock_git)  # Missing github_service

    with pytest.raises(
        RuntimeError,
        match="Entity 'complex_entity' requires 'github_service' for save operation",
    ):
        factory._validate_requirements(mock_config, context, "save")


def test_validate_requirements_passes_with_all_services():
    """Test that validation passes when all required services present."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "complex_entity"
    mock_config.required_services_restore = ["github_service", "conflict_strategy"]

    mock_github = Mock()
    mock_conflict = Mock()
    context = StrategyContext(
        _github_service=mock_github, _conflict_strategy=mock_conflict
    )

    # Should not raise
    factory._validate_requirements(mock_config, context, "restore")
