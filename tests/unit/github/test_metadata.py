"""Unit tests for metadata utilities."""

from datetime import datetime, timezone

import pytest

from github_data.entities import (
    Comment,
    Issue,
    PullRequest,
    PullRequestComment,
    PullRequestReview,
    PullRequestReviewComment,
)
from github_data.entities.users import GitHubUser


def _create_test_user(login: str = "testuser") -> GitHubUser:
    """Create a test GitHubUser for fixtures."""
    return GitHubUser(
        login=login,
        id=1,
        avatar_url="https://github.com/avatars/1",
        html_url=f"https://github.com/{login}",
    )


def _create_test_issue(
    body: str = "Test body",
    user_login: str = "testuser",
    number: int = 1,
) -> Issue:
    """Create a test Issue for fixtures."""
    now = datetime.now(timezone.utc)
    return Issue(
        id=1,
        number=number,
        title="Test Issue",
        body=body,
        state="open",
        state_reason=None,
        labels=[],
        user=_create_test_user(user_login),
        assignees=[],
        milestone=None,
        created_at=now,
        updated_at=now,
        closed_at=None,
        closed_by=None,
        html_url=f"https://github.com/test/repo/issues/{number}",
        comments=0,
    )


@pytest.mark.unit
class TestPrepareIssueBodyForRestore:
    """Tests for prepare_issue_body_for_restore function."""

    def test_sanitizes_mentions_in_body(self) -> None:
        """Should sanitize @mentions in issue body."""
        from github_data.github.metadata import prepare_issue_body_for_restore

        issue = _create_test_issue(body="Thanks @john for the help")
        result = prepare_issue_body_for_restore(issue, include_metadata=False)
        assert result == "Thanks `@john` for the help"

    def test_sanitizes_mentions_with_metadata(self) -> None:
        """Should sanitize @mentions in both body and metadata footer."""
        from github_data.github.metadata import prepare_issue_body_for_restore

        issue = _create_test_issue(body="Thanks @alice", user_login="bob")
        result = prepare_issue_body_for_restore(issue, include_metadata=True)

        # Body mentions should be sanitized
        assert "`@alice`" in result
        # Metadata author mention should be sanitized
        assert "`@bob`" in result
        # Should not have unsanitized mentions
        assert " @alice" not in result
        assert " @bob" not in result

    def test_empty_body_with_metadata(self) -> None:
        """Should handle empty body and sanitize metadata mentions."""
        from github_data.github.metadata import prepare_issue_body_for_restore

        issue = _create_test_issue(body="", user_login="charlie")
        result = prepare_issue_body_for_restore(issue, include_metadata=True)

        # Should have sanitized metadata author
        assert "`@charlie`" in result

    def test_none_body_with_metadata(self) -> None:
        """Should handle None body and sanitize metadata mentions."""
        from github_data.github.metadata import prepare_issue_body_for_restore

        issue = _create_test_issue(body="")
        issue.body = None
        result = prepare_issue_body_for_restore(issue, include_metadata=True)

        # Should still return metadata with sanitized mentions
        assert result is not None
        assert "---" in result


def _create_test_comment(
    body: str = "Test comment",
    user_login: str = "commenter",
) -> Comment:
    """Create a test Comment for fixtures."""
    now = datetime.now(timezone.utc)
    return Comment(
        id=100,
        body=body,
        user=_create_test_user(user_login),
        created_at=now,
        updated_at=now,
        html_url="https://github.com/test/repo/issues/1#issuecomment-100",
        issue_url="https://api.github.com/repos/test/repo/issues/1",
    )


@pytest.mark.unit
class TestPrepareCommentBodyForRestore:
    """Tests for prepare_comment_body_for_restore function."""

    def test_sanitizes_mentions_in_body(self) -> None:
        """Should sanitize @mentions in comment body."""
        from github_data.github.metadata import prepare_comment_body_for_restore

        comment = _create_test_comment(body="Great work @alice!")
        result = prepare_comment_body_for_restore(comment, include_metadata=False)
        assert result == "Great work `@alice`!"

    def test_sanitizes_mentions_with_metadata(self) -> None:
        """Should sanitize @mentions in both body and metadata footer."""
        from github_data.github.metadata import prepare_comment_body_for_restore

        comment = _create_test_comment(body="Thanks @bob", user_login="alice")
        result = prepare_comment_body_for_restore(comment, include_metadata=True)

        # Body mentions should be sanitized
        assert "`@bob`" in result
        # Metadata author mention should be sanitized
        assert "`@alice`" in result

    def test_multiple_mentions(self) -> None:
        """Should sanitize multiple @mentions."""
        from github_data.github.metadata import prepare_comment_body_for_restore

        comment = _create_test_comment(body="@alice @bob @charlie please review")
        result = prepare_comment_body_for_restore(comment, include_metadata=False)
        assert result == "`@alice` `@bob` `@charlie` please review"


def _create_test_pr(
    body: str = "Test PR body",
    user_login: str = "prauthor",
    number: int = 1,
) -> PullRequest:
    """Create a test PullRequest for fixtures."""
    now = datetime.now(timezone.utc)
    return PullRequest(
        id=200,
        number=number,
        title="Test PR",
        body=body,
        state="open",
        user=_create_test_user(user_login),
        labels=[],
        assignees=[],
        milestone=None,
        created_at=now,
        updated_at=now,
        closed_at=None,
        merged_at=None,
        merge_commit_sha=None,
        head_ref="feature-branch",
        base_ref="main",
        html_url=f"https://github.com/test/repo/pull/{number}",
        comments=0,
    )


@pytest.mark.unit
class TestPreparePrBodyForRestore:
    """Tests for prepare_pr_body_for_restore function."""

    def test_sanitizes_mentions_in_body(self) -> None:
        """Should sanitize @mentions in PR body."""
        from github_data.github.metadata import prepare_pr_body_for_restore

        pr = _create_test_pr(body="Fixes issue reported by @alice")
        result = prepare_pr_body_for_restore(pr, include_metadata=False)
        assert result == "Fixes issue reported by `@alice`"

    def test_sanitizes_mentions_with_metadata(self) -> None:
        """Should sanitize @mentions in both body and metadata footer."""
        from github_data.github.metadata import prepare_pr_body_for_restore

        pr = _create_test_pr(body="Review needed @bob", user_login="alice")
        result = prepare_pr_body_for_restore(pr, include_metadata=True)

        # Body mentions should be sanitized
        assert "`@bob`" in result
        # Metadata author mention should be sanitized
        assert "`@alice`" in result

    def test_empty_body_with_metadata(self) -> None:
        """Should handle empty body and sanitize metadata mentions."""
        from github_data.github.metadata import prepare_pr_body_for_restore

        pr = _create_test_pr(body="", user_login="charlie")
        result = prepare_pr_body_for_restore(pr, include_metadata=True)

        # Should have sanitized metadata author
        assert "`@charlie`" in result

    def test_none_body_with_metadata(self) -> None:
        """Should handle None body and sanitize metadata mentions."""
        from github_data.github.metadata import prepare_pr_body_for_restore

        pr = _create_test_pr(body="")
        pr.body = None
        result = prepare_pr_body_for_restore(pr, include_metadata=True)

        # Should still return metadata with sanitized mentions
        assert result is not None
        assert "---" in result


def _create_test_pr_comment(
    body: str = "Test PR comment",
    user_login: str = "prcommenter",
) -> PullRequestComment:
    """Create a test PullRequestComment for fixtures."""
    now = datetime.now(timezone.utc)
    return PullRequestComment(
        id=300,
        body=body,
        user=_create_test_user(user_login),
        created_at=now,
        updated_at=now,
        html_url="https://github.com/test/repo/pull/1#issuecomment-300",
        pull_request_url="https://api.github.com/repos/test/repo/pulls/1",
    )


@pytest.mark.unit
class TestPreparePrCommentBodyForRestore:
    """Tests for prepare_pr_comment_body_for_restore function."""

    def test_sanitizes_mentions_in_body(self) -> None:
        """Should sanitize @mentions in PR comment body."""
        from github_data.github.metadata import prepare_pr_comment_body_for_restore

        comment = _create_test_pr_comment(body="LGTM @alice")
        result = prepare_pr_comment_body_for_restore(comment, include_metadata=False)
        assert result == "LGTM `@alice`"

    def test_sanitizes_mentions_with_metadata(self) -> None:
        """Should sanitize @mentions in both body and metadata footer."""
        from github_data.github.metadata import prepare_pr_comment_body_for_restore

        comment = _create_test_pr_comment(body="Thanks @bob", user_login="alice")
        result = prepare_pr_comment_body_for_restore(comment, include_metadata=True)

        # Body mentions should be sanitized
        assert "`@bob`" in result
        # Metadata author mention should be sanitized
        assert "`@alice`" in result


def _create_test_pr_review(
    body: str = "Test review",
    user_login: str = "reviewer",
    state: str = "APPROVED",
) -> PullRequestReview:
    """Create a test PullRequestReview for fixtures."""
    now = datetime.now(timezone.utc)
    return PullRequestReview(
        id=400,
        pr_number=1,
        body=body,
        user=_create_test_user(user_login),
        state=state,
        submitted_at=now,
        html_url="https://github.com/test/repo/pull/1#pullrequestreview-400",
        pull_request_url="https://api.github.com/repos/test/repo/pulls/1",
        author_association="CONTRIBUTOR",
        commit_id="abc123",
    )


@pytest.mark.unit
class TestPreparePrReviewBodyForRestore:
    """Tests for prepare_pr_review_body_for_restore function."""

    def test_sanitizes_mentions_in_body(self) -> None:
        """Should sanitize @mentions in PR review body."""
        from github_data.github.metadata import prepare_pr_review_body_for_restore

        review = _create_test_pr_review(body="Great work @alice!")
        result = prepare_pr_review_body_for_restore(review, include_metadata=False)
        assert result == "Great work `@alice`!"

    def test_sanitizes_mentions_with_metadata(self) -> None:
        """Should sanitize @mentions in both body and metadata footer."""
        from github_data.github.metadata import prepare_pr_review_body_for_restore

        review = _create_test_pr_review(body="Thanks @bob", user_login="alice")
        result = prepare_pr_review_body_for_restore(review, include_metadata=True)

        # Body mentions should be sanitized
        assert "`@bob`" in result
        # Metadata author mention should be sanitized
        assert "`@alice`" in result

    def test_empty_body_with_metadata(self) -> None:
        """Should handle empty body and sanitize metadata mentions."""
        from github_data.github.metadata import prepare_pr_review_body_for_restore

        review = _create_test_pr_review(body="", user_login="charlie")
        result = prepare_pr_review_body_for_restore(review, include_metadata=True)

        # Should have sanitized metadata author
        assert "`@charlie`" in result

    def test_none_body_with_metadata(self) -> None:
        """Should handle None body and sanitize metadata mentions."""
        from github_data.github.metadata import prepare_pr_review_body_for_restore

        review = _create_test_pr_review(body="")
        review.body = None
        result = prepare_pr_review_body_for_restore(review, include_metadata=True)

        # Should still return metadata with sanitized mentions
        assert result is not None
        assert "---" in result


def _create_test_pr_review_comment(
    body: str = "Test review comment",
    user_login: str = "reviewcommenter",
) -> PullRequestReviewComment:
    """Create a test PullRequestReviewComment for fixtures."""
    now = datetime.now(timezone.utc)
    return PullRequestReviewComment(
        id=500,
        review_id=400,
        pr_number=1,
        body=body,
        user=_create_test_user(user_login),
        created_at=now,
        updated_at=now,
        html_url="https://github.com/test/repo/pull/1#discussion_r500",
        pull_request_url="https://api.github.com/repos/test/repo/pulls/1",
        diff_hunk="@@ -1,3 +1,4 @@",
        path="src/file.py",
        line=10,
    )


@pytest.mark.unit
class TestPreparePrReviewCommentBodyForRestore:
    """Tests for prepare_pr_review_comment_body_for_restore function."""

    def test_sanitizes_mentions_in_body(self) -> None:
        """Should sanitize @mentions in PR review comment body."""
        from github_data.github.metadata import (
            prepare_pr_review_comment_body_for_restore,
        )

        comment = _create_test_pr_review_comment(body="Consider @alice's approach")
        result = prepare_pr_review_comment_body_for_restore(
            comment, include_metadata=False
        )
        assert result == "Consider `@alice`'s approach"

    def test_sanitizes_mentions_with_metadata(self) -> None:
        """Should sanitize @mentions in both body and metadata footer."""
        from github_data.github.metadata import (
            prepare_pr_review_comment_body_for_restore,
        )

        comment = _create_test_pr_review_comment(body="Thanks @bob", user_login="alice")
        result = prepare_pr_review_comment_body_for_restore(
            comment, include_metadata=True
        )

        # Body mentions should be sanitized
        assert "`@bob`" in result
        # Metadata author mention should be sanitized
        assert "`@alice`" in result
