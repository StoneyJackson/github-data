"""Tests for RestoreOrchestrator with EntityRegistry."""

import pytest
from unittest.mock import Mock
from src.operations.restore.orchestrator import StrategyBasedRestoreOrchestrator
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_restore_orchestrator_accepts_registry():
    """Test RestoreOrchestrator accepts EntityRegistry."""
    registry = EntityRegistry()
    github_service = Mock()
    storage_service = Mock()

    orchestrator = StrategyBasedRestoreOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service
    )

    assert orchestrator._registry == registry
