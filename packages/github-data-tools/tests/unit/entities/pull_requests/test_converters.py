# tests/unit/entities/pull_requests/test_converters.py
"""Unit tests for pull requests converters."""
import pytest


@pytest.mark.unit
def test_convert_to_pull_request_loads_from_pull_requests_entity():
    """convert_to_pull_request should load from pull_requests entity package."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    assert "convert_to_pull_request" in registry.list_converters()

    metadata = registry._converter_metadata["convert_to_pull_request"]
    assert metadata["entity"] == "pull_requests"
    assert "entities.pull_requests.converters" in metadata["module"]


@pytest.mark.unit
def test_convert_to_pull_request_transforms_data_with_all_fields():
    """convert_to_pull_request should handle all fields including merge data."""
    from github_data.github.converter_registry import get_converter
    from github_data.entities.pull_requests.models import PullRequest

    converter = get_converter("convert_to_pull_request")

    raw_data = {
        "id": 555666,
        "number": 99,
        "title": "Test Pull Request",
        "body": "PR description",
        "state": "closed",
        "user": {
            "id": 1,
            "login": "testuser",
            "type": "User",
        },
        "assignees": [
            {
                "id": 2,
                "login": "reviewer1",
                "type": "User",
            },
        ],
        "labels": [
            {
                "id": 100,
                "name": "enhancement",
                "color": "a2eeef",
                "description": "New feature or request",
                "url": "https://api.github.com/repos/owner/repo/labels/enhancement",
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
        "closed_at": "2024-01-03T00:00:00Z",
        "merged_at": "2024-01-03T00:00:00Z",
        "merge_commit_sha": "abc123def456",
        "base_ref": "main",
        "head_ref": "feature-branch",
        "html_url": "https://github.com/owner/repo/pull/99",
        "comments": 3,
    }

    result = converter(raw_data)

    assert isinstance(result, PullRequest)
    assert result.id == 555666
    assert result.number == 99
    assert result.title == "Test Pull Request"
    assert result.state == "closed"
    assert result.user.login == "testuser"
    assert len(result.assignees) == 1
    assert result.assignees[0].login == "reviewer1"
    assert len(result.labels) == 1
    assert result.labels[0].name == "enhancement"
    assert result.milestone is not None
    assert result.milestone.title == "Version 1.0"
    assert result.merged_at is not None
    assert result.merge_commit_sha == "abc123def456"
    assert result.base_ref == "main"
    assert result.head_ref == "feature-branch"
    assert result.comments_count == 3


@pytest.mark.unit
def test_convert_to_pull_request_handles_minimal_data():
    """convert_to_pull_request should handle minimal required data."""
    from github_data.github.converter_registry import get_converter
    from github_data.entities.pull_requests.models import PullRequest

    converter = get_converter("convert_to_pull_request")

    raw_data = {
        "id": 123,
        "number": 1,
        "title": "Minimal PR",
        "state": "open",
        "user": {
            "id": 1,
            "login": "testuser",
            "type": "User",
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "html_url": "https://github.com/owner/repo/pull/1",
    }

    result = converter(raw_data)

    assert isinstance(result, PullRequest)
    assert result.id == 123
    assert result.number == 1
    assert result.assignees == []
    assert result.labels == []
    assert result.milestone is None
    assert result.merged_at is None
    assert result.merge_commit_sha is None
    assert result.comments_count == 0
