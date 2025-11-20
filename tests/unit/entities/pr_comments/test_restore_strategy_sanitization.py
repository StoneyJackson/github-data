"""Test mention sanitization in PR comments restore strategy."""

import pytest
from datetime import datetime, timezone

from github_data.entities.pr_comments.restore_strategy import (
    PullRequestCommentsRestoreStrategy,
)
from github_data.entities.pr_comments.models import PullRequestComment
from github_data.entities.users.models import GitHubUser
from github_data.operations.restore.strategy import RestoreConflictStrategy


class MockConflictStrategy(RestoreConflictStrategy):
    """Mock conflict strategy for testing."""

    def resolve_conflicts(self, existing: list, to_restore: list) -> list:
        return to_restore


def _create_test_user(login: str = "testuser") -> GitHubUser:
    """Create a test GitHubUser for fixtures."""
    return GitHubUser(
        login=login,
        id=1,
        avatar_url="https://github.com/avatars/1",
        html_url=f"https://github.com/{login}",
    )


def _create_test_pr_comment(
    body: str = "Test PR comment",
    user_login: str = "prcommenter",
) -> PullRequestComment:
    """Create a test PullRequestComment for fixtures."""
    now = datetime.now(timezone.utc)
    return PullRequestComment(
        id=456,
        body=body,
        user=_create_test_user(user_login),
        created_at=now,
        updated_at=now,
        html_url="https://github.com/test/repo/pull/10#issuecomment-456",
        pull_request_url="https://api.github.com/repos/test/repo/pulls/10",
    )


@pytest.mark.unit
def test_prepare_comment_body_sanitizes_mentions_when_metadata_enabled() -> None:
    """Test that _prepare_comment_body sanitizes mentions when metadata enabled."""
    # Arrange
    strategy = PullRequestCommentsRestoreStrategy(
        conflict_strategy=MockConflictStrategy(), include_original_metadata=True
    )
    comment = _create_test_pr_comment(body="Good catch @reviewer")

    # Act
    result = strategy._prepare_comment_body(comment)

    # Assert
    assert "`@reviewer`" in result


@pytest.mark.unit
def test_prepare_comment_body_sanitizes_mentions_when_metadata_disabled() -> None:
    """Test that _prepare_comment_body sanitizes mentions when metadata disabled."""
    # Arrange
    strategy = PullRequestCommentsRestoreStrategy(
        conflict_strategy=MockConflictStrategy(), include_original_metadata=False
    )
    comment = _create_test_pr_comment(body="Thanks @alice and @bob-123")

    # Act
    result = strategy._prepare_comment_body(comment)

    # Assert
    assert "`@alice`" in result
    assert "`@bob-123`" in result
