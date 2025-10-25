"""Integration tests for Batch 2 dependency validation."""

import pytest
import os
from src.entities.registry import EntityRegistry


@pytest.mark.integration
def test_batch2_entities_discovered():
    """Test all Batch 2 entities discovered."""
    registry = EntityRegistry()
    names = registry.get_all_entity_names()

    assert "issues" in names
    assert "comments" in names
    assert "sub_issues" in names


@pytest.mark.integration
def test_batch2_dependency_graph():
    """Test Batch 2 dependency relationships."""
    registry = EntityRegistry()

    issues = registry.get_entity("issues")
    comments = registry.get_entity("comments")
    sub_issues = registry.get_entity("sub_issues")

    # Verify dependencies
    assert issues.get_dependencies() == ["milestones"]
    assert comments.get_dependencies() == ["issues"]
    assert sub_issues.get_dependencies() == ["issues"]


@pytest.mark.integration
def test_batch2_topological_sort():
    """Test Batch 1 + 2 entities sort correctly."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    # Verify dependency order
    milestone_idx = enabled_names.index("milestones")
    issues_idx = enabled_names.index("issues")
    comments_idx = enabled_names.index("comments")
    sub_issues_idx = enabled_names.index("sub_issues")

    # Milestones must come before issues
    assert milestone_idx < issues_idx
    # Issues must come before comments and sub_issues
    assert issues_idx < comments_idx
    assert issues_idx < sub_issues_idx


@pytest.mark.integration
def test_batch2_auto_disable_on_missing_dependency():
    """Test auto-disable when dependency is disabled."""
    os.environ["INCLUDE_ISSUES"] = "false"
    os.environ["INCLUDE_ISSUE_COMMENTS"] = "true"
    os.environ["INCLUDE_SUB_ISSUES"] = "true"

    registry = EntityRegistry.from_environment(strict=False)
    enabled_names = [e.config.name for e in registry.get_enabled_entities()]

    # Comments and sub_issues should be auto-disabled
    assert "comments" not in enabled_names
    assert "sub_issues" not in enabled_names

    # Cleanup
    del os.environ["INCLUDE_ISSUES"]
    del os.environ["INCLUDE_ISSUE_COMMENTS"]
    del os.environ["INCLUDE_SUB_ISSUES"]


@pytest.mark.integration
def test_batch2_strict_mode_raises_on_violation():
    """Test strict mode raises error on dependency violation."""
    os.environ["INCLUDE_ISSUES"] = "false"
    os.environ["INCLUDE_ISSUE_COMMENTS"] = "true"

    with pytest.raises(ValueError, match="requires.*INCLUDE_ISSUES"):
        EntityRegistry.from_environment(strict=True)

    # Cleanup
    del os.environ["INCLUDE_ISSUES"]
    del os.environ["INCLUDE_ISSUE_COMMENTS"]
