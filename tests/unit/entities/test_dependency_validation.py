import pytest
import logging
from github_data.entities.registry import EntityRegistry
from github_data.entities.base import RegisteredEntity


@pytest.fixture
def registry_with_dependencies():
    """Create registry with dependent entities."""

    class IssuesConfig:
        name = "issues"
        env_var = "INCLUDE_ISSUES"
        default_value = True
        value_type = bool
        dependencies = []
        description = ""

    class CommentsConfig:
        name = "comments"
        env_var = "INCLUDE_COMMENTS"
        default_value = True
        value_type = bool
        dependencies = ["issues"]
        description = ""

    registry = EntityRegistry.__new__(EntityRegistry)
    registry._entities = {
        "issues": RegisteredEntity(config=IssuesConfig(), enabled=True),
        "comments": RegisteredEntity(config=CommentsConfig(), enabled=True),
    }
    registry._explicitly_set = set()
    return registry


def test_validate_dependencies_auto_disables_when_parent_disabled(
    registry_with_dependencies, caplog
):
    """Test auto-disable dependent when parent is disabled (non-strict mode)."""
    # Disable parent
    registry_with_dependencies._entities["issues"].enabled = False

    with caplog.at_level(logging.WARNING):
        registry_with_dependencies._validate_dependencies(strict=False)

    # Comments should be auto-disabled
    assert registry_with_dependencies._entities["comments"].enabled is False

    # Should have logged warning
    assert "comments" in caplog.text
    assert "requires" in caplog.text.lower()


def test_validate_dependencies_explicit_conflict_fails_strict(
    registry_with_dependencies,
):
    """Test explicit conflict fails in strict mode."""
    # Disable parent
    registry_with_dependencies._entities["issues"].enabled = False

    # Mark comments as explicitly set (simulate user set INCLUDE_COMMENTS=true)
    registry_with_dependencies._explicitly_set = {"comments"}

    with pytest.raises(ValueError, match="requires"):
        registry_with_dependencies._validate_dependencies(strict=True)


def test_validate_dependencies_passes_when_all_satisfied(registry_with_dependencies):
    """Test validation passes when dependencies satisfied."""
    # Both enabled (default state)
    registry_with_dependencies._validate_dependencies(strict=False)

    # Should still be enabled
    assert registry_with_dependencies._entities["issues"].enabled is True
    assert registry_with_dependencies._entities["comments"].enabled is True
