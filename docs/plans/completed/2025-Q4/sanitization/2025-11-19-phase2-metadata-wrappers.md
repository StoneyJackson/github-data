# Phase 2: Metadata Wrappers Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add wrapper functions to `metadata.py` that combine metadata footer generation with mention sanitization, providing a single entry point for restore strategies.

**Architecture:** Six wrapper functions following the naming pattern `prepare_*_body_for_restore()` that call existing `add_*_metadata_footer()` functions then apply `sanitize_mentions()`. Each wrapper accepts an `include_metadata` flag to optionally skip metadata footer generation.

**Tech Stack:** Python 3, pytest, type hints

---

## Task 1: Add Import for Sanitizers Module

**Files:**
- Modify: `/workspaces/github-data/github_data/github/metadata.py:8-17`

**Step 1: Add the import**

Add the import for `sanitize_mentions` after the existing imports.

Edit `/workspaces/github-data/github_data/github/metadata.py`:

Change:
```python
from datetime import datetime

from ..entities import (
```

To:
```python
from datetime import datetime

from .sanitizers import sanitize_mentions
from ..entities import (
```

**Step 2: Run type check to verify import is valid**

Run: `pdm run mypy github_data/github/metadata.py`
Expected: No errors related to the import

**Step 3: Commit**

```bash
git add github_data/github/metadata.py
git commit -s -m "refactor(metadata): add sanitize_mentions import"
```

---

## Task 2: Add prepare_issue_body_for_restore Function

**Files:**
- Modify: `/workspaces/github-data/github_data/github/metadata.py` (after line 36)
- Create: `/workspaces/github-data/tests/unit/github/test_metadata.py`

**Step 1: Write the failing test**

Create `/workspaces/github-data/tests/unit/github/test_metadata.py`:

```python
"""Unit tests for metadata utilities."""

from datetime import datetime, timezone

import pytest

from github_data.entities import Issue
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
        locked=False,
        labels=[],
        user=_create_test_user(user_login),
        assignees=[],
        milestone=None,
        created_at=now,
        updated_at=now,
        closed_at=None,
        closed_by=None,
        html_url=f"https://github.com/test/repo/issues/{number}",
        repository_url="https://api.github.com/repos/test/repo",
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
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/github/test_metadata.py -v`
Expected: FAIL with "cannot import name 'prepare_issue_body_for_restore'"

**Step 3: Write minimal implementation**

Add the function to `/workspaces/github-data/github_data/github/metadata.py` after `add_issue_metadata_footer` (after line 36):

```python


def prepare_issue_body_for_restore(
    issue: Issue,
    include_metadata: bool = True,
) -> str:
    """
    Prepare issue body for restore with optional metadata and sanitization.

    Args:
        issue: The issue to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized issue body ready for restore operation
    """
    if include_metadata:
        body = add_issue_metadata_footer(issue)
    else:
        body = issue.body or ""

    return sanitize_mentions(body) or ""
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/github/test_metadata.py::TestPrepareIssueBodyForRestore -v`
Expected: PASS (all 4 tests)

**Step 5: Run type check**

Run: `pdm run mypy github_data/github/metadata.py`
Expected: No errors

**Step 6: Commit**

```bash
git add github_data/github/metadata.py tests/unit/github/test_metadata.py
git commit -s -m "feat(metadata): add prepare_issue_body_for_restore function"
```

---

## Task 3: Add prepare_comment_body_for_restore Function

**Files:**
- Modify: `/workspaces/github-data/github_data/github/metadata.py` (after prepare_issue_body_for_restore)
- Modify: `/workspaces/github-data/tests/unit/github/test_metadata.py`

**Step 1: Write the failing test**

Add to `/workspaces/github-data/tests/unit/github/test_metadata.py`:

```python
from github_data.entities import Comment


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
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/github/test_metadata.py::TestPrepareCommentBodyForRestore -v`
Expected: FAIL with "cannot import name 'prepare_comment_body_for_restore'"

**Step 3: Write minimal implementation**

Add to `/workspaces/github-data/github_data/github/metadata.py` after `prepare_issue_body_for_restore`:

```python


def prepare_comment_body_for_restore(
    comment: Comment,
    include_metadata: bool = True,
) -> str:
    """
    Prepare comment body for restore with optional metadata and sanitization.

    Args:
        comment: The comment to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized comment body ready for restore operation
    """
    if include_metadata:
        body = add_comment_metadata_footer(comment)
    else:
        body = comment.body

    return sanitize_mentions(body) or ""
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/github/test_metadata.py::TestPrepareCommentBodyForRestore -v`
Expected: PASS (all 3 tests)

**Step 5: Commit**

```bash
git add github_data/github/metadata.py tests/unit/github/test_metadata.py
git commit -s -m "feat(metadata): add prepare_comment_body_for_restore function"
```

---

## Task 4: Add prepare_pr_body_for_restore Function

**Files:**
- Modify: `/workspaces/github-data/github_data/github/metadata.py`
- Modify: `/workspaces/github-data/tests/unit/github/test_metadata.py`

**Step 1: Write the failing test**

Add to `/workspaces/github-data/tests/unit/github/test_metadata.py`:

```python
from github_data.entities import PullRequest


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
        locked=False,
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
        head_sha="abc123",
        base_ref="main",
        base_sha="def456",
        html_url=f"https://github.com/test/repo/pull/{number}",
        diff_url=f"https://github.com/test/repo/pull/{number}.diff",
        patch_url=f"https://github.com/test/repo/pull/{number}.patch",
        draft=False,
        maintainer_can_modify=True,
        requested_reviewers=[],
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
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/github/test_metadata.py::TestPreparePrBodyForRestore -v`
Expected: FAIL with "cannot import name 'prepare_pr_body_for_restore'"

**Step 3: Write minimal implementation**

Add to `/workspaces/github-data/github_data/github/metadata.py` after `add_pr_metadata_footer`:

```python


def prepare_pr_body_for_restore(
    pr: PullRequest,
    include_metadata: bool = True,
) -> str:
    """
    Prepare pull request body for restore with optional metadata and sanitization.

    Args:
        pr: The pull request to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized PR body ready for restore operation
    """
    if include_metadata:
        body = add_pr_metadata_footer(pr)
    else:
        body = pr.body or ""

    return sanitize_mentions(body) or ""
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/github/test_metadata.py::TestPreparePrBodyForRestore -v`
Expected: PASS (all 4 tests)

**Step 5: Commit**

```bash
git add github_data/github/metadata.py tests/unit/github/test_metadata.py
git commit -s -m "feat(metadata): add prepare_pr_body_for_restore function"
```

---

## Task 5: Add prepare_pr_comment_body_for_restore Function

**Files:**
- Modify: `/workspaces/github-data/github_data/github/metadata.py`
- Modify: `/workspaces/github-data/tests/unit/github/test_metadata.py`

**Step 1: Write the failing test**

Add to `/workspaces/github-data/tests/unit/github/test_metadata.py`:

```python
from github_data.entities import PullRequestComment


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
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/github/test_metadata.py::TestPreparePrCommentBodyForRestore -v`
Expected: FAIL with "cannot import name 'prepare_pr_comment_body_for_restore'"

**Step 3: Write minimal implementation**

Add to `/workspaces/github-data/github_data/github/metadata.py` after `add_pr_comment_metadata_footer`:

```python


def prepare_pr_comment_body_for_restore(
    comment: PullRequestComment,
    include_metadata: bool = True,
) -> str:
    """
    Prepare PR comment body for restore with optional metadata and sanitization.

    Args:
        comment: The PR comment to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized PR comment body ready for restore operation
    """
    if include_metadata:
        body = add_pr_comment_metadata_footer(comment)
    else:
        body = comment.body

    return sanitize_mentions(body) or ""
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/github/test_metadata.py::TestPreparePrCommentBodyForRestore -v`
Expected: PASS (all 2 tests)

**Step 5: Commit**

```bash
git add github_data/github/metadata.py tests/unit/github/test_metadata.py
git commit -s -m "feat(metadata): add prepare_pr_comment_body_for_restore function"
```

---

## Task 6: Add prepare_pr_review_body_for_restore Function

**Files:**
- Modify: `/workspaces/github-data/github_data/github/metadata.py`
- Modify: `/workspaces/github-data/tests/unit/github/test_metadata.py`

**Step 1: Write the failing test**

Add to `/workspaces/github-data/tests/unit/github/test_metadata.py`:

```python
from github_data.entities import PullRequestReview


def _create_test_pr_review(
    body: str = "Test review",
    user_login: str = "reviewer",
    state: str = "APPROVED",
) -> PullRequestReview:
    """Create a test PullRequestReview for fixtures."""
    now = datetime.now(timezone.utc)
    return PullRequestReview(
        id=400,
        body=body,
        user=_create_test_user(user_login),
        state=state,
        submitted_at=now,
        html_url="https://github.com/test/repo/pull/1#pullrequestreview-400",
        pull_request_url="https://api.github.com/repos/test/repo/pulls/1",
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
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/github/test_metadata.py::TestPreparePrReviewBodyForRestore -v`
Expected: FAIL with "cannot import name 'prepare_pr_review_body_for_restore'"

**Step 3: Write minimal implementation**

Add to `/workspaces/github-data/github_data/github/metadata.py` after `add_pr_review_metadata_footer`:

```python


def prepare_pr_review_body_for_restore(
    review: PullRequestReview,
    include_metadata: bool = True,
) -> str:
    """
    Prepare PR review body for restore with optional metadata and sanitization.

    Args:
        review: The PR review to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized PR review body ready for restore operation
    """
    if include_metadata:
        body = add_pr_review_metadata_footer(review)
    else:
        body = review.body or ""

    return sanitize_mentions(body) or ""
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/github/test_metadata.py::TestPreparePrReviewBodyForRestore -v`
Expected: PASS (all 4 tests)

**Step 5: Commit**

```bash
git add github_data/github/metadata.py tests/unit/github/test_metadata.py
git commit -s -m "feat(metadata): add prepare_pr_review_body_for_restore function"
```

---

## Task 7: Add prepare_pr_review_comment_body_for_restore Function

**Files:**
- Modify: `/workspaces/github-data/github_data/github/metadata.py`
- Modify: `/workspaces/github-data/tests/unit/github/test_metadata.py`

**Step 1: Write the failing test**

Add to `/workspaces/github-data/tests/unit/github/test_metadata.py`:

```python
from github_data.entities import PullRequestReviewComment


def _create_test_pr_review_comment(
    body: str = "Test review comment",
    user_login: str = "reviewcommenter",
) -> PullRequestReviewComment:
    """Create a test PullRequestReviewComment for fixtures."""
    now = datetime.now(timezone.utc)
    return PullRequestReviewComment(
        id=500,
        body=body,
        user=_create_test_user(user_login),
        created_at=now,
        updated_at=now,
        html_url="https://github.com/test/repo/pull/1#discussion_r500",
        pull_request_url="https://api.github.com/repos/test/repo/pulls/1",
        pull_request_review_id=400,
        diff_hunk="@@ -1,3 +1,4 @@",
        path="src/file.py",
        position=None,
        original_position=None,
        commit_id="abc123",
        original_commit_id="abc123",
        in_reply_to_id=None,
        line=10,
        original_line=10,
        side="RIGHT",
        original_side=None,
        start_line=None,
        original_start_line=None,
        start_side=None,
        subject_type="line",
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
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/github/test_metadata.py::TestPreparePrReviewCommentBodyForRestore -v`
Expected: FAIL with "cannot import name 'prepare_pr_review_comment_body_for_restore'"

**Step 3: Write minimal implementation**

Add to `/workspaces/github-data/github_data/github/metadata.py` after `add_pr_review_comment_metadata_footer`:

```python


def prepare_pr_review_comment_body_for_restore(
    comment: PullRequestReviewComment,
    include_metadata: bool = True,
) -> str:
    """
    Prepare PR review comment body for restore with optional metadata and sanitization.

    Args:
        comment: The PR review comment to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized PR review comment body ready for restore operation
    """
    if include_metadata:
        body = add_pr_review_comment_metadata_footer(comment)
    else:
        body = comment.body

    return sanitize_mentions(body) or ""
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/github/test_metadata.py::TestPreparePrReviewCommentBodyForRestore -v`
Expected: PASS (all 2 tests)

**Step 5: Commit**

```bash
git add github_data/github/metadata.py tests/unit/github/test_metadata.py
git commit -s -m "feat(metadata): add prepare_pr_review_comment_body_for_restore function"
```

---

## Task 8: Run Full Test Suite and Quality Checks

**Files:**
- No modifications

**Step 1: Run all metadata tests**

Run: `pdm run pytest tests/unit/github/test_metadata.py -v`
Expected: All 19 tests PASS

**Step 2: Run type checking**

Run: `pdm run mypy github_data/github/metadata.py`
Expected: No errors

**Step 3: Run linting**

Run: `pdm run flake8 github_data/github/metadata.py tests/unit/github/test_metadata.py`
Expected: No errors

**Step 4: Run formatting**

Run: `pdm run black github_data/github/metadata.py tests/unit/github/test_metadata.py`
Expected: Files formatted (or already formatted)

**Step 5: Run fast test suite**

Run: `make test-fast`
Expected: All tests PASS

**Step 6: Final commit if formatting changed**

```bash
git add github_data/github/metadata.py tests/unit/github/test_metadata.py
git commit -s -m "style(metadata): apply formatting"
```

---

## Summary

This plan adds 6 wrapper functions to `metadata.py`:
1. `prepare_issue_body_for_restore`
2. `prepare_comment_body_for_restore`
3. `prepare_pr_body_for_restore`
4. `prepare_pr_comment_body_for_restore`
5. `prepare_pr_review_body_for_restore`
6. `prepare_pr_review_comment_body_for_restore`

Each function:
- Accepts an entity and `include_metadata` boolean
- Calls the corresponding `add_*_metadata_footer` function if metadata is enabled
- Applies `sanitize_mentions` to the result
- Returns the sanitized text ready for restore

**Total commits:** 8
**Total tests added:** 19

After completion, proceed to Phase 3 (Restore Strategy Updates) which will update each entity's restore strategy to use these new wrapper functions.
