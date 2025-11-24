# tests/unit/entities/comments/test_converters.py
"""Unit tests for comments converters."""
import pytest


@pytest.mark.unit
def test_convert_to_comment_loads_from_comments_entity():
    """convert_to_comment should be loadable from comments entity package."""
    from github_data_tools.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    # Should have the converter
    assert "convert_to_comment" in registry.list_converters()

    # Should have metadata showing it's from comments entity
    metadata = registry._converter_metadata["convert_to_comment"]
    assert metadata["entity"] == "comments"
    assert "entities.comments.converters" in metadata["module"]


@pytest.mark.unit
def test_convert_to_comment_transforms_raw_data_correctly():
    """convert_to_comment should transform raw GitHub API data to Comment model."""
    from github_data_tools.github.converter_registry import get_converter
    from github_data_tools.entities.comments.models import Comment

    converter = get_converter("convert_to_comment")

    raw_data = {
        "id": 987654,
        "body": "This is a test comment",
        "user": {
            "id": 1,
            "login": "testuser",
            "type": "User",
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "html_url": "https://github.com/owner/repo/issues/123#issuecomment-987654",
        "issue_url": "https://api.github.com/repos/owner/repo/issues/123",
    }

    result = converter(raw_data)

    assert isinstance(result, Comment)
    assert result.id == 987654
    assert result.body == "This is a test comment"
    assert (
        result.html_url
        == "https://github.com/owner/repo/issues/123#issuecomment-987654"
    )
    assert result.issue_url == "https://api.github.com/repos/owner/repo/issues/123"
    assert result.issue_number == 123
