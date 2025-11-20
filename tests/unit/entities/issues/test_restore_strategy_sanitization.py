"""Test mention sanitization in issues restore strategy."""

import pytest
from github_data.entities.issues.restore_strategy import IssuesRestoreStrategy
from github_data.entities.issues.models import Issue
from github_data.entities.users.models import GitHubUser


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_enabled():
    """Test that transform sanitizes mentions when include_original_metadata=True."""
    # Arrange
    strategy = IssuesRestoreStrategy(include_original_metadata=True)
    issue = Issue(
        id=1001,
        number=42,
        title="Test Issue",
        body="Thanks @john for the review",
        state="open",
        user=GitHubUser(
            login="testuser",
            id=100,
            avatar_url="https://github.com/testuser.png",
            html_url="https://github.com/testuser",
        ),
        labels=[],
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/test/repo/issues/42",
        comments=0,
    )
    context = {}

    # Act
    result = strategy.transform(issue, context)

    # Assert
    assert "`@john`" in result["body"]
    assert "@john" not in result["body"] or "`@john`" in result["body"]


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_disabled():
    """Test that transform sanitizes mentions when include_original_metadata=False."""
    # Arrange
    strategy = IssuesRestoreStrategy(include_original_metadata=False)
    issue = Issue(
        id=1002,
        number=42,
        title="Test Issue",
        body="cc @alice and @bob-123",
        state="open",
        user=GitHubUser(
            login="testuser",
            id=100,
            avatar_url="https://github.com/testuser.png",
            html_url="https://github.com/testuser",
        ),
        labels=[],
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/test/repo/issues/42",
        comments=0,
    )
    context = {}

    # Act
    result = strategy.transform(issue, context)

    # Assert
    assert "`@alice`" in result["body"]
    assert "`@bob-123`" in result["body"]
