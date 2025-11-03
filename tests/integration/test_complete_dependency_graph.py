"""Integration tests for complete 10-entity dependency graph."""

import pytest
from github_data.entities.registry import EntityRegistry


@pytest.mark.integration
def test_all_10_entities_discovered():
    """Test all 10 entities discovered by registry."""
    registry = EntityRegistry()
    names = registry.get_all_entity_names()

    # Batch 1
    assert "labels" in names
    assert "milestones" in names
    assert "git_repository" in names

    # Batch 2
    assert "issues" in names
    assert "comments" in names
    assert "sub_issues" in names

    # Batch 3
    assert "pull_requests" in names
    assert "pr_reviews" in names
    assert "pr_review_comments" in names
    assert "pr_comments" in names


@pytest.mark.integration
def test_complete_dependency_graph():
    """Test complete dependency relationships for all entities."""
    registry = EntityRegistry()

    # Verify each entity's dependencies
    assert registry.get_entity("labels").get_dependencies() == []
    assert registry.get_entity("milestones").get_dependencies() == []
    assert registry.get_entity("git_repository").get_dependencies() == []

    assert registry.get_entity("issues").get_dependencies() == ["milestones"]
    assert registry.get_entity("comments").get_dependencies() == ["issues"]
    assert registry.get_entity("sub_issues").get_dependencies() == ["issues"]

    assert registry.get_entity("pull_requests").get_dependencies() == ["milestones"]
    assert registry.get_entity("pr_reviews").get_dependencies() == ["pull_requests"]
    assert registry.get_entity("pr_review_comments").get_dependencies() == [
        "pr_reviews"
    ]
    assert registry.get_entity("pr_comments").get_dependencies() == ["pull_requests"]


@pytest.mark.integration
def test_complete_topological_sort():
    """Test topological sort produces valid execution order for all 10 entities."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    # Get indices
    def idx(name):
        return enabled_names.index(name)

    # Verify dependency order constraints
    # Independent entities can appear anywhere, but:
    assert idx("milestones") < idx("issues")
    assert idx("milestones") < idx("pull_requests")
    assert idx("issues") < idx("comments")
    assert idx("issues") < idx("sub_issues")
    assert idx("pull_requests") < idx("pr_reviews")
    assert idx("pull_requests") < idx("pr_comments")
    assert idx("pr_reviews") < idx("pr_review_comments")


@pytest.mark.integration
def test_cascading_dependency_disable():
    """Test cascading disable when root dependency disabled."""
    import os

    # Disable milestones - should cascade to issues and PRs
    os.environ["INCLUDE_MILESTONES"] = "false"

    registry = EntityRegistry.from_environment(strict=False)
    enabled_names = [e.config.name for e in registry.get_enabled_entities()]

    # These should all be disabled due to cascade
    assert "milestones" not in enabled_names
    assert "issues" not in enabled_names
    assert "comments" not in enabled_names
    assert "sub_issues" not in enabled_names
    assert "pull_requests" not in enabled_names
    assert "pr_reviews" not in enabled_names
    assert "pr_review_comments" not in enabled_names
    assert "pr_comments" not in enabled_names

    # These should still be enabled (independent)
    assert "labels" in enabled_names
    assert "git_repository" in enabled_names

    # Cleanup
    del os.environ["INCLUDE_MILESTONES"]


@pytest.mark.integration
def test_pr_branch_independence():
    """Test PR review comments and PR comments are independent branches."""
    import os

    # Disable pr_reviews - should only affect pr_review_comments, not pr_comments
    os.environ["INCLUDE_PR_REVIEWS"] = "false"

    registry = EntityRegistry.from_environment(strict=False)
    enabled_names = [e.config.name for e in registry.get_enabled_entities()]

    # pr_review_comments should be disabled
    assert "pr_review_comments" not in enabled_names

    # pr_comments should still be enabled (different branch)
    assert "pr_comments" in enabled_names
    assert "pull_requests" in enabled_names

    # Cleanup
    del os.environ["INCLUDE_PR_REVIEWS"]


@pytest.mark.integration
def test_no_circular_dependencies():
    """Test no circular dependencies in complete graph."""
    registry = EntityRegistry()

    # get_enabled_entities performs topological sort
    # If there are circular deps, this raises ValueError
    enabled = registry.get_enabled_entities()

    # Should succeed with all 11 entities
    assert len(enabled) == 11
