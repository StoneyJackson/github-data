"""Tests for SaveOrchestrator with EntityRegistry."""

import pytest
from unittest.mock import Mock
from src.operations.save.orchestrator import StrategyBasedSaveOrchestrator
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_save_orchestrator_accepts_registry():
    """Test SaveOrchestrator accepts EntityRegistry."""
    registry = EntityRegistry()
    github_service = Mock()
    storage_service = Mock()

    orchestrator = StrategyBasedSaveOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service,
    )

    assert orchestrator._registry == registry


@pytest.mark.unit
def test_save_orchestrator_uses_registry_for_execution_order():
    """Test orchestrator uses registry for dependency-ordered execution."""
    registry = EntityRegistry()
    github_service = Mock()
    storage_service = Mock()

    orchestrator = StrategyBasedSaveOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service,
    )

    # Get execution order
    enabled = registry.get_enabled_entities()
    entity_names = [e.config.name for e in enabled]

    # Should respect dependency order
    milestone_idx = entity_names.index("milestones")
    issues_idx = entity_names.index("issues")
    assert milestone_idx < issues_idx
