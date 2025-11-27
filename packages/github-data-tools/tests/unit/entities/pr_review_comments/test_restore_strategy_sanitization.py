"""Test mention sanitization in PR review comments restore strategy."""

import pytest
from github_data_tools.entities.pr_review_comments.restore_strategy import (
    PullRequestReviewCommentsRestoreStrategy,
)
from github_data_tools.entities.pr_review_comments.models import (
    PullRequestReviewComment,
)
from github_data_tools.entities.users.models import GitHubUser


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_enabled():
    """Test that transform sanitizes mentions when include_original_metadata=True."""
    # Arrange
    strategy = PullRequestReviewCommentsRestoreStrategy(include_original_metadata=True)
    comment = PullRequestReviewComment(
        id=999,
        body="Great suggestion @maintainer",
        review_id=789,
        pr_number=10,
        diff_hunk="@@ -1,3 +1,3 @@",
        path="src/main.py",
        line=42,
        user=GitHubUser(login="testuser"),
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/test/repo/pull/10#discussion_r999",
        pull_request_url="https://api.github.com/repos/test/repo/pulls/10",
    )
    context = {"review_id_mapping": {"789": 456}}

    # Act
    result = strategy.transform(comment, context)

    # Assert
    assert result is not None
    assert "`@maintainer`" in result["body"]


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_disabled():
    """Test that transform sanitizes mentions when include_original_metadata=False."""
    # Arrange
    strategy = PullRequestReviewCommentsRestoreStrategy(include_original_metadata=False)
    comment = PullRequestReviewComment(
        id=999,
        body="cc @alice @bob-reviewer",
        review_id=789,
        pr_number=10,
        diff_hunk="@@ -1,3 +1,3 @@",
        path="src/main.py",
        line=42,
        user=GitHubUser(login="testuser"),
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/test/repo/pull/10#discussion_r999",
        pull_request_url="https://api.github.com/repos/test/repo/pulls/10",
    )
    context = {"review_id_mapping": {"789": 456}}

    # Act
    result = strategy.transform(comment, context)

    # Assert
    assert result is not None
    assert "`@alice`" in result["body"]
    assert "`@bob-reviewer`" in result["body"]
