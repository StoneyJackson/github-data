"""Test mention sanitization in PR reviews restore strategy."""

import pytest
from github_data.entities.pr_reviews.restore_strategy import (
    PullRequestReviewsRestoreStrategy,
)
from github_data.entities.pr_reviews.models import PullRequestReview
from github_data.entities.users.models import GitHubUser


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_enabled():
    """Test that transform sanitizes mentions when include_original_metadata=True."""
    # Arrange
    strategy = PullRequestReviewsRestoreStrategy(include_original_metadata=True)
    review = PullRequestReview(
        id=789,
        pr_number=10,
        user=GitHubUser(login="testuser"),
        body="Looks good @developer",
        state="APPROVED",
        html_url="https://github.com/test/repo/pull/10#pullrequestreview-789",
        pull_request_url="https://api.github.com/repos/test/repo/pull/10",
        author_association="CONTRIBUTOR",
        submitted_at="2023-01-01T00:00:00Z",
    )
    context = {"pull_request_number_mapping": {10: 5}}

    # Act
    result = strategy.transform(review, context)

    # Assert
    assert result is not None
    assert "`@developer`" in result["body"]


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_disabled():
    """Test that transform sanitizes mentions when include_original_metadata=False."""
    # Arrange
    strategy = PullRequestReviewsRestoreStrategy(include_original_metadata=False)
    review = PullRequestReview(
        id=789,
        pr_number=10,
        user=GitHubUser(login="testuser"),
        body="@alice @bob-123 please review",
        state="COMMENTED",
        html_url="https://github.com/test/repo/pull/10#pullrequestreview-789",
        pull_request_url="https://api.github.com/repos/test/repo/pull/10",
        author_association="CONTRIBUTOR",
        submitted_at="2023-01-01T00:00:00Z",
    )
    context = {"pull_request_number_mapping": {10: 5}}

    # Act
    result = strategy.transform(review, context)

    # Assert
    assert result is not None
    assert "`@alice`" in result["body"]
    assert "`@bob-123`" in result["body"]
