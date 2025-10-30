"""Tests for RestoreOrchestrator with EntityRegistry."""

import pytest
from unittest.mock import Mock
from github_data.operations.restore.orchestrator import StrategyBasedRestoreOrchestrator
from github_data.entities.registry import EntityRegistry


@pytest.mark.unit
def test_restore_orchestrator_accepts_registry():
    """Test RestoreOrchestrator accepts EntityRegistry."""
    registry = EntityRegistry()
    github_service = Mock()
    storage_service = Mock()
    git_service = Mock()

    orchestrator = StrategyBasedRestoreOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service,
        git_service=git_service,
    )

    assert orchestrator._registry == registry
