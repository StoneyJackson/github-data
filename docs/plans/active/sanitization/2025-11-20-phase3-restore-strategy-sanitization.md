# Phase 3: Restore Strategy Sanitization Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Update all restore strategies to use the new metadata preparation wrappers with built-in sanitization

**Architecture:** Replace direct calls to `add_*_metadata_footer()` functions in restore strategies with calls to `prepare_*_body_for_restore()` wrappers. This guarantees sanitization is always applied to restored content.

**Tech Stack:** Python, pytest, existing restore strategy framework

---

## Task 1: Update Issues Restore Strategy

**Files:**
- Modify: `github_data/entities/issues/restore_strategy.py:73-82`

**Step 1: Write the failing test**

Create test file: `tests/unit/entities/issues/test_restore_strategy_sanitization.py`

```python
"""Test mention sanitization in issues restore strategy."""

import pytest
from github_data.entities.issues.restore_strategy import IssuesRestoreStrategy
from github_data.entities.issues.models import Issue


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_enabled():
    """Test that transform sanitizes mentions when include_original_metadata=True."""
    # Arrange
    strategy = IssuesRestoreStrategy(include_original_metadata=True)
    issue = Issue(
        number=42,
        title="Test Issue",
        body="Thanks @john for the review",
        state="open",
        labels=[],
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        url="https://api.github.com/repos/test/repo/issues/42",
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
        number=42,
        title="Test Issue",
        body="cc @alice and @bob-123",
        state="open",
        labels=[],
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        url="https://api.github.com/repos/test/repo/issues/42",
    )
    context = {}

    # Act
    result = strategy.transform(issue, context)

    # Assert
    assert "`@alice`" in result["body"]
    assert "`@bob-123`" in result["body"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/entities/issues/test_restore_strategy_sanitization.py -v`

Expected: FAIL - mentions not sanitized (tests should fail because restore strategy doesn't use wrapper yet)

**Step 3: Update issues restore strategy to use wrapper**

In `github_data/entities/issues/restore_strategy.py`, replace lines 73-82:

```python
    def transform(
        self, issue: Issue, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Prepare issue body with metadata and sanitization
        from github_data.github.metadata import prepare_issue_body_for_restore

        issue_body = prepare_issue_body_for_restore(
            issue,
            include_metadata=self._include_original_metadata
        )

        # Convert label objects to names
        label_names = [label.name for label in issue.labels]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/entities/issues/test_restore_strategy_sanitization.py -v`

Expected: PASS - both tests pass

**Step 5: Commit**

```bash
git add tests/unit/entities/issues/test_restore_strategy_sanitization.py github_data/entities/issues/restore_strategy.py
git commit -s -m "feat(issues): integrate mention sanitization in restore strategy

Replace direct add_issue_metadata_footer() call with
prepare_issue_body_for_restore() wrapper to ensure mentions
are sanitized during restore operations."
```

---

## Task 2: Update Comments Restore Strategy

**Files:**
- Modify: `github_data/entities/comments/restore_strategy.py:33-54`

**Step 1: Write the failing test**

Create test file: `tests/unit/entities/comments/test_restore_strategy_sanitization.py`

```python
"""Test mention sanitization in comments restore strategy."""

import pytest
from github_data.entities.comments.restore_strategy import CommentsRestoreStrategy
from github_data.entities.comments.models import Comment


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_enabled():
    """Test that transform sanitizes mentions when include_original_metadata=True."""
    # Arrange
    strategy = CommentsRestoreStrategy(include_original_metadata=True)
    comment = Comment(
        id=123,
        body="Thanks @alice for helping",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        issue_url="https://api.github.com/repos/test/repo/issues/42",
        url="https://api.github.com/repos/test/repo/issues/comments/123",
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
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        issue_url="https://api.github.com/repos/test/repo/issues/42",
        url="https://api.github.com/repos/test/repo/issues/comments/123",
    )
    context = {"issue_number_mapping": {42: 1}}

    # Act
    result = strategy.transform(comment, context)

    # Assert
    assert result is not None
    assert "`@bob-123`" in result["body"]
    assert "`@jane`" in result["body"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/entities/comments/test_restore_strategy_sanitization.py -v`

Expected: FAIL - mentions not sanitized

**Step 3: Update comments restore strategy to use wrapper**

In `github_data/entities/comments/restore_strategy.py`, replace lines 48-54:

```python
        # Prepare comment body with metadata and sanitization
        from github_data.github.metadata import prepare_comment_body_for_restore

        comment_body = prepare_comment_body_for_restore(
            comment,
            include_metadata=self._include_original_metadata
        )

        return {
            "body": comment_body,
            "issue_number": new_issue_number,
            "original_issue_number": original_issue_number,
        }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/entities/comments/test_restore_strategy_sanitization.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/unit/entities/comments/test_restore_strategy_sanitization.py github_data/entities/comments/restore_strategy.py
git commit -s -m "feat(comments): integrate mention sanitization in restore strategy

Replace direct add_comment_metadata_footer() call with
prepare_comment_body_for_restore() wrapper to ensure mentions
are sanitized during restore operations."
```

---

## Task 3: Update Pull Requests Restore Strategy

**Files:**
- Modify: `github_data/entities/pull_requests/restore_strategy.py:169-175`

**Step 1: Write the failing test**

Create test file: `tests/unit/entities/pull_requests/test_restore_strategy_sanitization.py`

```python
"""Test mention sanitization in pull requests restore strategy."""

import pytest
from github_data.entities.pull_requests.restore_strategy import PullRequestsRestoreStrategy
from github_data.entities.pull_requests.models import PullRequest
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
        conflict_strategy=MockConflictStrategy(),
        include_original_metadata=True
    )
    pr = PullRequest(
        number=10,
        title="Test PR",
        body="Thanks @contributor for the PR",
        state="open",
        head_ref="feature",
        base_ref="main",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        url="https://api.github.com/repos/test/repo/pulls/10",
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
        conflict_strategy=MockConflictStrategy(),
        include_original_metadata=False
    )
    pr = PullRequest(
        number=10,
        title="Test PR",
        body="cc @alice @bob-dev",
        state="open",
        head_ref="feature",
        base_ref="main",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        url="https://api.github.com/repos/test/repo/pulls/10",
    )

    # Act
    result = strategy._prepare_pr_body(pr)

    # Assert
    assert "`@alice`" in result
    assert "`@bob-dev`" in result
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/entities/pull_requests/test_restore_strategy_sanitization.py -v`

Expected: FAIL - mentions not sanitized

**Step 3: Update pull requests restore strategy to use wrapper**

In `github_data/entities/pull_requests/restore_strategy.py`, replace lines 169-175 with:

```python
    def _prepare_pr_body(self, pr: PullRequest) -> str:
        """Prepare pull request body with optional metadata and sanitization."""
        from github_data.github.metadata import prepare_pr_body_for_restore

        return prepare_pr_body_for_restore(
            pr,
            include_metadata=self._include_original_metadata
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/entities/pull_requests/test_restore_strategy_sanitization.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/unit/entities/pull_requests/test_restore_strategy_sanitization.py github_data/entities/pull_requests/restore_strategy.py
git commit -s -m "feat(pull_requests): integrate mention sanitization in restore strategy

Replace direct add_pr_metadata_footer() call with
prepare_pr_body_for_restore() wrapper to ensure mentions
are sanitized during restore operations."
```

---

## Task 4: Update PR Comments Restore Strategy

**Files:**
- Modify: `github_data/entities/pr_comments/restore_strategy.py:106-112`

**Step 1: Write the failing test**

Create test file: `tests/unit/entities/pr_comments/test_restore_strategy_sanitization.py`

```python
"""Test mention sanitization in PR comments restore strategy."""

import pytest
from github_data.entities.pr_comments.restore_strategy import PullRequestCommentsRestoreStrategy
from github_data.entities.pr_comments.models import PullRequestComment
from github_data.operations.restore.strategy import RestoreConflictStrategy


class MockConflictStrategy(RestoreConflictStrategy):
    """Mock conflict strategy for testing."""
    def resolve_conflicts(self, existing, to_restore):
        return to_restore


@pytest.mark.unit
def test_prepare_comment_body_sanitizes_mentions_when_metadata_enabled():
    """Test that _prepare_comment_body sanitizes mentions when metadata enabled."""
    # Arrange
    strategy = PullRequestCommentsRestoreStrategy(
        conflict_strategy=MockConflictStrategy(),
        include_original_metadata=True
    )
    comment = PullRequestComment(
        id=456,
        body="Good catch @reviewer",
        pull_request_number=10,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        url="https://api.github.com/repos/test/repo/pulls/comments/456",
    )

    # Act
    result = strategy._prepare_comment_body(comment)

    # Assert
    assert "`@reviewer`" in result


@pytest.mark.unit
def test_prepare_comment_body_sanitizes_mentions_when_metadata_disabled():
    """Test that _prepare_comment_body sanitizes mentions when metadata disabled."""
    # Arrange
    strategy = PullRequestCommentsRestoreStrategy(
        conflict_strategy=MockConflictStrategy(),
        include_original_metadata=False
    )
    comment = PullRequestComment(
        id=456,
        body="Thanks @alice and @bob-123",
        pull_request_number=10,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        url="https://api.github.com/repos/test/repo/pulls/comments/456",
    )

    # Act
    result = strategy._prepare_comment_body(comment)

    # Assert
    assert "`@alice`" in result
    assert "`@bob-123`" in result
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/entities/pr_comments/test_restore_strategy_sanitization.py -v`

Expected: FAIL - mentions not sanitized

**Step 3: Update PR comments restore strategy to use wrapper**

In `github_data/entities/pr_comments/restore_strategy.py`, replace lines 106-112 with:

```python
    def _prepare_comment_body(self, comment: PullRequestComment) -> str:
        """Prepare comment body with optional metadata and sanitization."""
        from github_data.github.metadata import prepare_pr_comment_body_for_restore

        return prepare_pr_comment_body_for_restore(
            comment,
            include_metadata=self._include_original_metadata
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/entities/pr_comments/test_restore_strategy_sanitization.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/unit/entities/pr_comments/test_restore_strategy_sanitization.py github_data/entities/pr_comments/restore_strategy.py
git commit -s -m "feat(pr_comments): integrate mention sanitization in restore strategy

Replace direct add_pr_comment_metadata_footer() call with
prepare_pr_comment_body_for_restore() wrapper to ensure mentions
are sanitized during restore operations."
```

---

## Task 5: Update PR Reviews Restore Strategy

**Files:**
- Modify: `github_data/entities/pr_reviews/restore_strategy.py:37-58`

**Step 1: Write the failing test**

Create test file: `tests/unit/entities/pr_reviews/test_restore_strategy_sanitization.py`

```python
"""Test mention sanitization in PR reviews restore strategy."""

import pytest
from github_data.entities.pr_reviews.restore_strategy import PullRequestReviewsRestoreStrategy
from github_data.entities.pr_reviews.models import PullRequestReview


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_enabled():
    """Test that transform sanitizes mentions when include_original_metadata=True."""
    # Arrange
    strategy = PullRequestReviewsRestoreStrategy(include_original_metadata=True)
    review = PullRequestReview(
        id=789,
        body="Looks good @developer",
        state="APPROVED",
        submitted_at="2023-01-01T00:00:00Z",
        pull_request_url="https://api.github.com/repos/test/repo/pull/10",
        url="https://api.github.com/repos/test/repo/pulls/10/reviews/789",
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
        body="@alice @bob-123 please review",
        state="COMMENTED",
        submitted_at="2023-01-01T00:00:00Z",
        pull_request_url="https://api.github.com/repos/test/repo/pull/10",
        url="https://api.github.com/repos/test/repo/pulls/10/reviews/789",
    )
    context = {"pull_request_number_mapping": {10: 5}}

    # Act
    result = strategy.transform(review, context)

    # Assert
    assert result is not None
    assert "`@alice`" in result["body"]
    assert "`@bob-123`" in result["body"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/entities/pr_reviews/test_restore_strategy_sanitization.py -v`

Expected: FAIL - mentions not sanitized

**Step 3: Update PR reviews restore strategy to use wrapper**

In `github_data/entities/pr_reviews/restore_strategy.py`, replace lines 52-58 with:

```python
        # Prepare review body with metadata and sanitization
        from github_data.github.metadata import prepare_pr_review_body_for_restore

        review_body = prepare_pr_review_body_for_restore(
            review,
            include_metadata=self._include_original_metadata
        )

        return {
            "body": review_body,
            "state": review.state,
            "pr_number": new_pr_number,
            "original_pr_number": original_pr_number,
        }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/entities/pr_reviews/test_restore_strategy_sanitization.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/unit/entities/pr_reviews/test_restore_strategy_sanitization.py github_data/entities/pr_reviews/restore_strategy.py
git commit -s -m "feat(pr_reviews): integrate mention sanitization in restore strategy

Replace direct add_pr_review_metadata_footer() call with
prepare_pr_review_body_for_restore() wrapper to ensure mentions
are sanitized during restore operations."
```

---

## Task 6: Update PR Review Comments Restore Strategy

**Files:**
- Modify: `github_data/entities/pr_review_comments/restore_strategy.py:37-60`

**Step 1: Write the failing test**

Create test file: `tests/unit/entities/pr_review_comments/test_restore_strategy_sanitization.py`

```python
"""Test mention sanitization in PR review comments restore strategy."""

import pytest
from github_data.entities.pr_review_comments.restore_strategy import PullRequestReviewCommentsRestoreStrategy
from github_data.entities.pr_review_comments.models import PullRequestReviewComment


@pytest.mark.unit
def test_transform_sanitizes_mentions_when_metadata_enabled():
    """Test that transform sanitizes mentions when include_original_metadata=True."""
    # Arrange
    strategy = PullRequestReviewCommentsRestoreStrategy(include_original_metadata=True)
    comment = PullRequestReviewComment(
        id=999,
        body="Great suggestion @maintainer",
        review_id=789,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        url="https://api.github.com/repos/test/repo/pulls/comments/999",
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
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        url="https://api.github.com/repos/test/repo/pulls/comments/999",
    )
    context = {"review_id_mapping": {"789": 456}}

    # Act
    result = strategy.transform(comment, context)

    # Assert
    assert result is not None
    assert "`@alice`" in result["body"]
    assert "`@bob-reviewer`" in result["body"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/entities/pr_review_comments/test_restore_strategy_sanitization.py -v`

Expected: FAIL - mentions not sanitized

**Step 3: Update PR review comments restore strategy to use wrapper**

In `github_data/entities/pr_review_comments/restore_strategy.py`, replace lines 52-60 with:

```python
        # Prepare comment body with metadata and sanitization
        from github_data.github.metadata import prepare_pr_review_comment_body_for_restore

        comment_body = prepare_pr_review_comment_body_for_restore(
            comment,
            include_metadata=self._include_original_metadata
        )

        return {
            "body": comment_body,
            "review_id": new_review_id,
            "original_review_id": original_review_id,
        }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/entities/pr_review_comments/test_restore_strategy_sanitization.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/unit/entities/pr_review_comments/test_restore_strategy_sanitization.py github_data/entities/pr_review_comments/restore_strategy.py
git commit -s -m "feat(pr_review_comments): integrate mention sanitization in restore strategy

Replace direct add_pr_review_comment_metadata_footer() call with
prepare_pr_review_comment_body_for_restore() wrapper to ensure mentions
are sanitized during restore operations."
```

---

## Task 7: Run Full Test Suite

**Step 1: Run all unit tests**

Run: `make test-unit`

Expected: All unit tests pass including new sanitization tests

**Step 2: Run fast test suite**

Run: `make test-fast`

Expected: All tests pass (unit + integration, excluding container tests)

**Step 3: Run full test suite with coverage**

Run: `make test`

Expected: All tests pass with good coverage on modified files

**Step 4: Run quality checks**

Run: `make check`

Expected: All checks pass (lint, format, type-check, tests)

**Step 5: Document completion**

No commit needed - this is verification only

---

## Task 8: Verify Integration Tests Still Pass

**Files:**
- Read: `tests/integration/test_issues_save_restore_integration.py`
- Read: `tests/integration/test_comments_save_restore_integration.py`
- Read: Other integration test files

**Step 1: Run issues integration tests**

Run: `pytest tests/integration/test_issues_save_restore_integration.py -v`

Expected: PASS - existing integration tests work with sanitization

**Step 2: Run comments integration tests**

Run: `pytest tests/integration/test_comments_save_restore_integration.py -v`

Expected: PASS - existing integration tests work with sanitization

**Step 3: Run all integration tests**

Run: `make test-integration`

Expected: PASS - all integration tests compatible with sanitization

**Step 4: Run container tests if Docker available**

Run: `make test-container`

Expected: PASS - full end-to-end workflow works with sanitization

**Step 5: Document any issues**

If any integration tests fail, document the failure and create follow-up tasks

No commit needed - this is verification only

---

## Task 9: Update Documentation

**Files:**
- Modify: `docs/plans/active/sanitization/2025-11-16-mention-sanitization-design.md`

**Step 1: Mark Phase 3 checklist items complete**

Update the implementation checklist in the design document:

```markdown
### Phase 3: Restore Strategy Updates

- [x] Update `issues/restore_strategy.py` to use new wrapper
- [x] Update `comments/restore_strategy.py` to use new wrapper
- [x] Update `pull_requests/restore_strategy.py` to use new wrapper
- [x] Update `pr_comments/restore_strategy.py` to use new wrapper
- [x] Update `pr_reviews/restore_strategy.py` to use new wrapper
- [x] Update `pr_review_comments/restore_strategy.py` to use new wrapper
```

**Step 2: Add implementation notes section**

Add a new section at the end of the document:

```markdown
## Implementation Notes - Phase 3

**Completed:** 2025-11-20

**Changes Made:**
1. Updated 6 restore strategy files to use metadata preparation wrappers
2. Added 6 new unit test files for sanitization verification
3. All existing integration tests continue to pass
4. No breaking changes to public APIs

**Pattern Applied:**
- Each restore strategy now imports and calls `prepare_*_body_for_restore()`
- Removed direct calls to `add_*_metadata_footer()` functions
- Tests verify both metadata-enabled and metadata-disabled paths
- Sanitization is now guaranteed for all restored content

**Files Modified:**
- `github_data/entities/issues/restore_strategy.py`
- `github_data/entities/comments/restore_strategy.py`
- `github_data/entities/pull_requests/restore_strategy.py`
- `github_data/entities/pr_comments/restore_strategy.py`
- `github_data/entities/pr_reviews/restore_strategy.py`
- `github_data/entities/pr_review_comments/restore_strategy.py`

**Test Files Added:**
- `tests/unit/entities/issues/test_restore_strategy_sanitization.py`
- `tests/unit/entities/comments/test_restore_strategy_sanitization.py`
- `tests/unit/entities/pull_requests/test_restore_strategy_sanitization.py`
- `tests/unit/entities/pr_comments/test_restore_strategy_sanitization.py`
- `tests/unit/entities/pr_reviews/test_restore_strategy_sanitization.py`
- `tests/unit/entities/pr_review_comments/test_restore_strategy_sanitization.py`
```

**Step 3: Commit documentation update**

```bash
git add docs/plans/active/sanitization/2025-11-16-mention-sanitization-design.md
git commit -s -m "docs: mark Phase 3 complete in sanitization design

Update implementation checklist and add implementation notes
documenting the completion of restore strategy sanitization
integration."
```

---

## Success Criteria

1. All 6 restore strategies updated to use metadata preparation wrappers
2. All 6 new unit test files created and passing
3. All existing tests continue to pass (no regressions)
4. Code follows project standards (Clean Code, type hints, docstrings)
5. All quality checks pass (make check)
6. Documentation updated to reflect completion
7. Each entity type has 2 tests (metadata enabled/disabled)
8. Mentions are sanitized in all restore operations

## Non-Goals

- Modifying the metadata wrapper functions (already complete in Phase 2)
- Adding new sanitization types (future work)
- Changing restore strategy interfaces or protocols
- Modifying storage or GitHub service layers

## Notes

- Each task follows TDD: test first, implement, verify, commit
- Tests verify both `include_metadata=True` and `include_metadata=False` paths
- Pattern is consistent across all 6 entity types
- No changes to public APIs or interfaces
- All changes are backward compatible
