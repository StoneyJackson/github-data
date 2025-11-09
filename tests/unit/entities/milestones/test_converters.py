# tests/unit/entities/milestones/test_converters.py
"""Unit tests for milestones converters."""
import pytest


@pytest.mark.unit
def test_convert_to_milestone_loads_from_milestones_entity():
    """convert_to_milestone should load from milestones entity package."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    assert "convert_to_milestone" in registry.list_converters()

    metadata = registry._converter_metadata["convert_to_milestone"]
    assert metadata["entity"] == "milestones"
    assert "entities.milestones.converters" in metadata["module"]


@pytest.mark.unit
def test_convert_to_milestone_transforms_data():
    """convert_to_milestone should transform raw data to Milestone model."""
    from github_data.github.converter_registry import get_converter
    from github_data.entities.milestones.models import Milestone

    converter = get_converter("convert_to_milestone")

    raw_data = {
        "id": 789,
        "number": 1,
        "title": "Version 1.0",
        "description": "First release",
        "state": "open",
        "open_issues": 5,
        "closed_issues": 10,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "due_on": "2024-12-31T00:00:00Z",
        "closed_at": None,
        "creator": {
            "id": 1,
            "login": "testuser",
            "type": "User",
        },
    }

    result = converter(raw_data)

    assert isinstance(result, Milestone)
    assert result.id == 789
    assert result.number == 1
    assert result.title == "Version 1.0"
