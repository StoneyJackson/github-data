"""Tests for SaveOrchestrator with EntityRegistry."""

import pytest
from unittest.mock import Mock
from github_data_tools.operations.save.orchestrator import StrategyBasedSaveOrchestrator
from github_data_core.entities.registry import EntityRegistry


@pytest.mark.unit
def test_save_orchestrator_accepts_registry():
    """Test SaveOrchestrator accepts EntityRegistry."""
    registry = EntityRegistry()
    github_service = Mock()
    storage_service = Mock()
    git_service = Mock()

    orchestrator = StrategyBasedSaveOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service,
        git_service=git_service,
    )

    assert orchestrator._registry == registry


@pytest.mark.unit
def test_save_orchestrator_uses_registry_for_execution_order():
    """Test orchestrator uses registry for dependency-ordered execution."""
    registry = EntityRegistry()
    github_service = Mock()
    storage_service = Mock()
    git_service = Mock()

    StrategyBasedSaveOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service,
        git_service=git_service,
    )

    # Get execution order
    enabled = registry.get_enabled_entities()
    entity_names = [e.config.name for e in enabled]

    # Should respect dependency order
    milestone_idx = entity_names.index("milestones")
    issues_idx = entity_names.index("issues")
    assert milestone_idx < issues_idx


@pytest.mark.unit
def test_save_orchestrator_returns_failure_status_on_error():
    """Test orchestrator returns success=False when entity save fails."""
    registry = EntityRegistry()

    # Enable only milestones for simpler test
    registry.get_entity("milestones").enabled = True

    # Disable all other entities (ignore if they don't exist in this package)
    for entity_name in [
        "git_repository",
        "labels",
        "issues",
        "comments",
        "pull_requests",
        "pr_comments",
        "pr_reviews",
        "pr_review_comments",
        "sub_issues",
        "releases",
    ]:
        try:
            registry.get_entity(entity_name).enabled = False
        except ValueError:
            # Entity doesn't exist in this package (e.g., git_repository)
            pass

    github_service = Mock()
    storage_service = Mock()

    # Make github_service raise an exception when calling get_repository_milestones
    github_service.get_repository_milestones.side_effect = Exception(
        "API Error: 401 Unauthorized"
    )

    orchestrator = StrategyBasedSaveOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service,
    )

    # Execute save - should not raise, but should return failure status
    results = orchestrator.execute("owner/repo", "/tmp/test")

    assert len(results) == 1
    assert results[0]["entity_name"] == "milestones"
    assert results[0]["success"] is False
    assert "API Error: 401 Unauthorized" in results[0]["error"]
