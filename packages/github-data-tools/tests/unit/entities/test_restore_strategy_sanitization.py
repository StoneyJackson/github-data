"""Test mention sanitization in comments restore strategy."""

import pytest
from github_data.entities.comments.restore_strategy import CommentsRestoreStrategy
from github_data.entities.comments.models import Comment
from github_data.entities.users.models import GitHubUser


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_enabled():
    """Test that transform sanitizes mentions when include_original_metadata=True."""
    # Arrange
    strategy = CommentsRestoreStrategy(include_original_metadata=True)
    comment = Comment(
        id=123,
        body="Thanks @alice for helping",
        user=GitHubUser(login="testuser"),
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/test/repo/issues/42#issuecomment-123",
        issue_url="https://api.github.com/repos/test/repo/issues/42",
    )
    context = {"issue_number_mapping": {42: 1}}

    # Act
    result = strategy.transform(comment, context)

    # Assert
    assert result is not None
    assert "`@alice`" in result["body"]


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_disabled():
    """Test that transform sanitizes mentions when include_original_metadata=False."""
    # Arrange
    strategy = CommentsRestoreStrategy(include_original_metadata=False)
    comment = Comment(
        id=123,
        body="cc @bob-123 and @jane",
        user=GitHubUser(login="testuser"),
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/test/repo/issues/42#issuecomment-123",
        issue_url="https://api.github.com/repos/test/repo/issues/42",
    )
    context = {"issue_number_mapping": {42: 1}}

    # Act
    result = strategy.transform(comment, context)

    # Assert
    assert result is not None
    assert "`@bob-123`" in result["body"]
    assert "`@jane`" in result["body"]
