"""Integration tests for StrategyContext validation."""

import pytest
from src.entities.registry import EntityRegistry
from src.operations.strategy_factory import StrategyFactory
from src.entities.strategy_context import StrategyContext


@pytest.mark.integration
def test_git_repository_requires_git_service_for_save():
    """Test that git_repository entity validation fails without git_service."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)

    # git_repository entity is enabled by default
    # Disable all other entities to isolate the test
    for entity_name in registry.get_all_entity_names():
        entity = registry.get_entity(entity_name)
        if entity_name != "git_repository":
            entity.enabled = False

    # Try to create save strategies without git_service
    with pytest.raises(
        RuntimeError,
        match="Entity 'git_repository' requires 'git_service' for save operation",
    ):
        factory.create_save_strategies()


@pytest.mark.integration
def test_labels_requires_github_service_for_restore():
    """Test that labels entity validation fails without github_service."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)

    # labels entity is enabled by default
    # Disable all other entities to isolate the test
    for entity_name in registry.get_all_entity_names():
        entity = registry.get_entity(entity_name)
        if entity_name != "labels":
            entity.enabled = False

    # Try to create restore strategies without github_service
    with pytest.raises(
        RuntimeError,
        match="Entity 'labels' requires 'github_service' for restore operation",
    ):
        factory.create_restore_strategies()


@pytest.mark.integration
def test_validation_fails_before_any_strategy_creation():
    """Test that validation fails fast before creating any strategies."""
    from unittest.mock import Mock

    registry = EntityRegistry()
    factory = StrategyFactory(registry)

    # Keep only labels and issues enabled
    for entity_name in registry.get_all_entity_names():
        entity = registry.get_entity(entity_name)
        if entity_name not in ["labels", "issues"]:
            entity.enabled = False

    # Try to create strategies without required services
    # Should fail on first entity that needs github_service
    with pytest.raises(RuntimeError, match="requires 'github_service'"):
        factory.create_restore_strategies()


@pytest.mark.integration
def test_successful_strategy_creation_with_all_services():
    """Test that strategies are created successfully when all services provided."""
    from unittest.mock import Mock

    registry = EntityRegistry()
    factory = StrategyFactory(registry)

    # Keep only labels enabled
    for entity_name in registry.get_all_entity_names():
        entity = registry.get_entity(entity_name)
        if entity_name != "labels":
            entity.enabled = False

    # Create with all required services
    mock_github_service = Mock()
    strategies = factory.create_restore_strategies(
        github_service=mock_github_service,
        conflict_strategy=None,
        include_original_metadata=True,
    )

    # Should succeed
    assert len(strategies) > 0
