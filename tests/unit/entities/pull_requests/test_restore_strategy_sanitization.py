"""Test mention sanitization in pull requests restore strategy."""

import pytest
from github_data.entities.pull_requests.restore_strategy import (
    PullRequestsRestoreStrategy,
)
from github_data.entities.pull_requests.models import PullRequest
from github_data.entities.users.models import GitHubUser
from github_data.operations.restore.strategy import RestoreConflictStrategy


class MockConflictStrategy(RestoreConflictStrategy):
    """Mock conflict strategy for testing."""

    def resolve_conflicts(self, existing, to_restore):
        return to_restore


@pytest.mark.unit
def test_prepare_pr_body_sanitizes_mentions_when_metadata_enabled():
    """Test that _prepare_pr_body sanitizes mentions when metadata enabled."""
    # Arrange
    strategy = PullRequestsRestoreStrategy(
        conflict_strategy=MockConflictStrategy(), include_original_metadata=True
    )
    pr = PullRequest(
        id=2001,
        number=10,
        title="Test PR",
        body="Thanks @contributor for the PR",
        state="open",
        user=GitHubUser(
            login="author",
            id=200,
            avatar_url="https://github.com/author.png",
            html_url="https://github.com/author",
        ),
        head_ref="feature",
        base_ref="main",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/test/repo/pulls/10",
        comments=0,
    )

    # Act
    result = strategy._prepare_pr_body(pr)

    # Assert
    assert "`@contributor`" in result


@pytest.mark.unit
def test_prepare_pr_body_sanitizes_mentions_when_metadata_disabled():
    """Test that _prepare_pr_body sanitizes mentions when metadata disabled."""
    # Arrange
    strategy = PullRequestsRestoreStrategy(
        conflict_strategy=MockConflictStrategy(), include_original_metadata=False
    )
    pr = PullRequest(
        id=2002,
        number=10,
        title="Test PR",
        body="cc @alice @bob-dev",
        state="open",
        user=GitHubUser(
            login="author",
            id=200,
            avatar_url="https://github.com/author.png",
            html_url="https://github.com/author",
        ),
        head_ref="feature",
        base_ref="main",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/test/repo/pulls/10",
        comments=0,
    )

    # Act
    result = strategy._prepare_pr_body(pr)

    # Assert
    assert "`@alice`" in result
    assert "`@bob-dev`" in result
