import pytest
from src.entities.registry import EntityRegistry
from src.entities.base import RegisteredEntity


def test_topological_sort_orders_by_dependencies():
    """Test entities sorted by dependency order."""
    class LabelsConfig:
        name = "labels"
        dependencies = []

    class MilestonesConfig:
        name = "milestones"
        dependencies = []

    class IssuesConfig:
        name = "issues"
        dependencies = ["milestones"]

    class CommentsConfig:
        name = "comments"
        dependencies = ["issues"]

    labels = RegisteredEntity(config=LabelsConfig(), enabled=True)
    milestones = RegisteredEntity(config=MilestonesConfig(), enabled=True)
    issues = RegisteredEntity(config=IssuesConfig(), enabled=True)
    comments = RegisteredEntity(config=CommentsConfig(), enabled=True)

    # Create in random order
    entities = [comments, labels, issues, milestones]

    registry = EntityRegistry.__new__(EntityRegistry)
    sorted_entities = registry._topological_sort(entities)

    names = [e.config.name for e in sorted_entities]

    # milestones must come before issues
    assert names.index("milestones") < names.index("issues")

    # issues must come before comments
    assert names.index("issues") < names.index("comments")


def test_topological_sort_detects_cycles():
    """Test cycle detection in dependencies."""
    class AConfig:
        name = "a"
        dependencies = ["b"]

    class BConfig:
        name = "b"
        dependencies = ["a"]

    a = RegisteredEntity(config=AConfig(), enabled=True)
    b = RegisteredEntity(config=BConfig(), enabled=True)

    registry = EntityRegistry.__new__(EntityRegistry)

    with pytest.raises(ValueError, match="circular dependency"):
        registry._topological_sort([a, b])
