# tests/unit/entities/issues/test_converters.py
"""Unit tests for issues converters."""
import pytest


@pytest.mark.unit
def test_convert_to_issue_loads_from_issues_entity():
    """convert_to_issue should load from issues entity package."""
    from github_data_tools.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    assert "convert_to_issue" in registry.list_converters()

    metadata = registry._converter_metadata["convert_to_issue"]
    assert metadata["entity"] == "issues"
    assert "entities.issues.converters" in metadata["module"]


@pytest.mark.unit
def test_convert_to_issue_transforms_data_with_all_nested_entities():
    """convert_to_issue should handle all nested entities."""
    from github_data_tools.github.converter_registry import get_converter
    from github_data_tools.entities.issues.models import Issue

    converter = get_converter("convert_to_issue")

    raw_data = {
        "id": 111222,
        "number": 42,
        "title": "Test Issue",
        "body": "Issue description",
        "state": "open",
        "user": {
            "id": 1,
            "login": "testuser",
            "type": "User",
        },
        "assignees": [
            {
                "id": 2,
                "login": "assignee1",
                "type": "User",
            },
            {
                "id": 3,
                "login": "assignee2",
                "type": "User",
            },
        ],
        "labels": [
            {
                "id": 100,
                "name": "bug",
                "color": "d73a4a",
                "description": "Something isn't working",
                "url": "https://api.github.com/repos/owner/repo/labels/bug",
            },
        ],
        "milestone": {
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
            "html_url": "https://github.com/owner/repo/milestone/1",
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "closed_at": None,
        "html_url": "https://github.com/owner/repo/issues/42",
        "comments": 5,
    }

    result = converter(raw_data)

    assert isinstance(result, Issue)
    assert result.id == 111222
    assert result.number == 42
    assert result.title == "Test Issue"
    assert result.state == "open"
    assert result.user.login == "testuser"
    assert len(result.assignees) == 2
    assert result.assignees[0].login == "assignee1"
    assert len(result.labels) == 1
    assert result.labels[0].name == "bug"
    assert result.milestone is not None
    assert result.milestone.title == "Version 1.0"
    assert result.comments_count == 5


@pytest.mark.unit
def test_convert_to_issue_handles_minimal_data():
    """convert_to_issue should handle minimal required data."""
    from github_data_tools.github.converter_registry import get_converter
    from github_data_tools.entities.issues.models import Issue

    converter = get_converter("convert_to_issue")

    raw_data = {
        "id": 999,
        "number": 1,
        "title": "Minimal Issue",
        "state": "closed",
        "user": {
            "id": 1,
            "login": "testuser",
            "type": "User",
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "html_url": "https://github.com/owner/repo/issues/1",
    }

    result = converter(raw_data)

    assert isinstance(result, Issue)
    assert result.id == 999
    assert result.number == 1
    assert result.assignees == []
    assert result.labels == []
    assert result.milestone is None
    assert result.comments_count == 0
