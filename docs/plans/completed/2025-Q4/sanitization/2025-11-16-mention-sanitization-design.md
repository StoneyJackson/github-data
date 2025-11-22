# GitHub Mention Sanitization Design

**Date:** 2025-11-16
**Status:** Approved for Implementation
**Scope:** Disable @mention autolinks in restored content (Phase 1 of autolink sanitization)

## Problem Statement

When restoring GitHub repository data (issues, PRs, comments, etc.), text content containing `@username` mentions creates GitHub autolinks that:
1. Send notifications to mentioned users
2. Create reverse links from external resources back to the restored content

This causes notification spam and unwanted cross-repository linkage. The solution must:
- Disable mention autolinks and notifications
- Preserve the original username text in its original location
- Apply consistently across all entity types

## Solution Architecture

### Three-Layer Design

1. **Core Sanitization Library** (`github_data/github/sanitizers.py`)
   - Centralized pattern matching and transformation logic
   - Single source of truth for mention detection
   - Extensible for future autolink types (issues, PRs, commits, repos)

2. **Metadata Preparation Wrappers** (`github_data/github/metadata.py`)
   - One wrapper function per entity type
   - Couples metadata addition with sanitization
   - Guarantees sanitization is always applied
   - Single entry point for restore strategies

3. **Entity Restore Strategies** (entity-specific)
   - Call the appropriate metadata preparation wrapper
   - No direct sanitization logic
   - Consistent behavior across all entities

### Why This Architecture?

**Centralized Library:** Avoids pattern drift, easy to test in isolation, simple to extend

**Wrapper Functions:** Makes sanitization impossible to forget - it's coupled with metadata preparation at a single decision point

**Separation of Concerns:**
- `sanitizers.py` knows HOW to sanitize
- `metadata.py` knows WHAT to prepare for restore
- Restore strategies know WHEN to prepare content

## Component Design

### 1. Sanitizers Module

**File:** `github_data/github/sanitizers.py`

```python
"""
Text sanitization utilities for disabling GitHub autolinks.

Provides functions to sanitize user-generated content before restoring
to prevent unwanted notifications and cross-repository links.
"""

import re


def sanitize_mentions(text: str) -> str:
    """
    Disable GitHub user mention autolinks by wrapping in backticks.

    Transforms @username to `@username` to prevent notifications
    and autolink creation. Preserves the username text in its
    original location.

    Args:
        text: Text content that may contain @mentions

    Returns:
        Text with all @mentions wrapped in backticks

    Examples:
        >>> sanitize_mentions("Thanks @john for the review")
        "Thanks `@john` for the review"

        >>> sanitize_mentions("cc @alice @bob-123")
        "cc `@alice` `@bob-123`"
    """
    if not text:
        return text

    # Pattern: @ followed by valid GitHub username
    # Only matches when @ is at line start or preceded by whitespace
    # to avoid breaking URLs like https://github.com/@user
    # GitHub usernames: alphanumeric start, then alphanumeric/hyphens,
    # must end with alphanumeric (no trailing hyphen)
    # Max length 39 chars
    pattern = r'(^|\s)(@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?)'

    return re.sub(pattern, r'\1`\2`', text, flags=re.MULTILINE)
```

**Key Design Decisions:**
- Regex pattern matches GitHub's username validation rules
- Boundary check ensures @ is at line start or preceded by whitespace
- Prevents breaking URLs and email addresses
- Handles edge cases: single char usernames, hyphens, max length
- Returns input unchanged if None/empty for safety
- Backtick wrapping creates inline code formatting (visible but acceptable)
- Uses `re.MULTILINE` flag to allow ^ to match start of any line

### 2. Metadata Preparation Wrappers

**File:** `github_data/github/metadata.py` (additions)

Add these wrapper functions to the existing metadata.py module:

```python
def prepare_issue_body_for_restore(
    issue: Issue,
    include_metadata: bool = True
) -> str:
    """
    Prepare issue body for restore with optional metadata and sanitization.

    Args:
        issue: The issue to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized issue body ready for restore operation
    """
    from github_data.github.sanitizers import sanitize_mentions

    if include_metadata:
        body = add_issue_metadata_footer(issue)
    else:
        body = issue.body or ""

    return sanitize_mentions(body)


def prepare_comment_body_for_restore(
    comment: Comment,
    include_metadata: bool = True
) -> str:
    """
    Prepare comment body for restore with optional metadata and sanitization.

    Args:
        comment: The comment to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized comment body ready for restore operation
    """
    from github_data.github.sanitizers import sanitize_mentions

    if include_metadata:
        body = add_comment_metadata_footer(comment)
    else:
        body = comment.body

    return sanitize_mentions(body)


def prepare_pr_body_for_restore(
    pr: PullRequest,
    include_metadata: bool = True
) -> str:
    """
    Prepare pull request body for restore with optional metadata and sanitization.

    Args:
        pr: The pull request to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized PR body ready for restore operation
    """
    from github_data.github.sanitizers import sanitize_mentions

    if include_metadata:
        body = add_pr_metadata_footer(pr)
    else:
        body = pr.body or ""

    return sanitize_mentions(body)


def prepare_pr_comment_body_for_restore(
    comment: PullRequestComment,
    include_metadata: bool = True
) -> str:
    """
    Prepare PR comment body for restore with optional metadata and sanitization.

    Args:
        comment: The PR comment to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized PR comment body ready for restore operation
    """
    from github_data.github.sanitizers import sanitize_mentions

    if include_metadata:
        body = add_pr_comment_metadata_footer(comment)
    else:
        body = comment.body

    return sanitize_mentions(body)


def prepare_pr_review_body_for_restore(
    review: PullRequestReview,
    include_metadata: bool = True
) -> str:
    """
    Prepare PR review body for restore with optional metadata and sanitization.

    Args:
        review: The PR review to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized PR review body ready for restore operation
    """
    from github_data.github.sanitizers import sanitize_mentions

    if include_metadata:
        body = add_pr_review_metadata_footer(review)
    else:
        body = review.body or ""

    return sanitize_mentions(body)


def prepare_pr_review_comment_body_for_restore(
    comment: PullRequestReviewComment,
    include_metadata: bool = True
) -> str:
    """
    Prepare PR review comment body for restore with optional metadata and sanitization.

    Args:
        comment: The PR review comment to prepare
        include_metadata: Whether to append original metadata footer

    Returns:
        Sanitized PR review comment body ready for restore operation
    """
    from github_data.github.sanitizers import sanitize_mentions

    if include_metadata:
        body = add_pr_review_comment_metadata_footer(comment)
    else:
        body = comment.body

    return sanitize_mentions(body)
```

**Pattern:**
- Each wrapper follows same structure
- Takes entity and include_metadata flag
- Returns fully prepared, sanitized text
- Single responsibility: orchestrate metadata + sanitization

### 3. Restore Strategy Updates

Each restore strategy's `transform()` method updates to use the new wrappers.

**Example: Issues Restore Strategy**

`github_data/entities/issues/restore_strategy.py`:

```python
def transform(self, issue: Issue, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Prepare issue body with metadata and sanitization
    from github_data.github.metadata import prepare_issue_body_for_restore

    issue_body = prepare_issue_body_for_restore(
        issue,
        include_metadata=self._include_original_metadata
    )

    # Convert label objects to names
    label_names = [label.name for label in issue.labels]

    # ... rest of transform logic unchanged
```

**Affected Restore Strategies:**
1. `github_data/entities/issues/restore_strategy.py`
2. `github_data/entities/comments/restore_strategy.py`
3. `github_data/entities/pull_requests/restore_strategy.py`
4. `github_data/entities/pr_comments/restore_strategy.py`
5. `github_data/entities/pr_reviews/restore_strategy.py`
6. `github_data/entities/pr_review_comments/restore_strategy.py`

**Change Pattern:**
- Replace direct calls to `add_*_metadata_footer()` functions
- Replace with calls to `prepare_*_body_for_restore()` wrappers
- Pass through the `include_metadata` parameter
- No other logic changes required

## Testing Strategy

### 1. Unit Tests for Sanitizers

**File:** `tests/unit/github/test_sanitizers.py`

Test cases:
- Single mention: `"Thanks @john"` → `"Thanks \`@john\`"`
- Multiple mentions: `"@alice and @bob"` → `"\`@alice\` and \`@bob\`"`
- Mention at line start: `"@alice\nhello"` → `"\`@alice\`\nhello"`
- Mentions with hyphens: `"@user-name-123"` → `"\`@user-name-123\`"`
- Single character username: `"@x"` → `"\`@x\`"`
- Maximum length username (39 chars)
- Already in code blocks: `` "`@john`" `` (may double-wrap, acceptable)
- No mentions: `"Hello world"` → `"Hello world"` (unchanged)
- Empty/None input: returns safely
- Mentions in URLs: `"https://github.com/@user"` → unchanged (not preceded by whitespace)
- Email addresses: `"test@example.com"` → unchanged (not preceded by whitespace)

### 2. Unit Tests for Metadata Wrappers

**File:** `tests/unit/github/test_metadata.py` (additions)

Test each `prepare_*_body_for_restore()` function:
- With metadata enabled: verify metadata footer included AND sanitized
- With metadata disabled: verify only original body sanitized
- Verify mentions in original body are sanitized
- Verify mentions in generated metadata footer are sanitized
- Empty body handling

### 3. Integration Tests for Restore Strategies

**Files:** `tests/integration/test_*_save_restore_integration.py`

Existing integration tests should verify:
- Issues with @mentions restore without triggering autolinks
- Comments with @mentions preserve username text
- PR descriptions, reviews, and comments all sanitized
- End-to-end workflow: save → restore → verify sanitization

### 4. Preview Testing (No Restore Required)

Use the sanitization preview utility for quick feedback:

```bash
# After saving repository data
python scripts/preview_sanitization.py ./save
```

The preview utility:
- Reads saved JSON files
- Shows what sanitization will occur during restore
- Highlights fields that contain @mentions
- Requires no GitHub token or restore operation
- Safe to run on any saved data directory

### 5. Manual Testing Checklist

Before marking complete:
- [ ] Create test issue with @mentions in body
- [ ] Create test comment with multiple @mentions
- [ ] Save repository data
- [ ] Run preview utility: `python scripts/preview_sanitization.py ./save`
- [ ] Verify preview shows expected sanitization
- [ ] Restore to test repository
- [ ] Verify mentions appear as `` `@username` `` (backtick-wrapped)
- [ ] Verify NO notifications sent to mentioned users
- [ ] Verify usernames still readable and in original locations

## Edge Cases and Error Handling

### Edge Cases to Handle

1. **Already sanitized content**: If content contains `` `@username` ``, will become `` `\`@username\`` `` (acceptable, over-sanitization safe)

2. **Mentions in code blocks**: Will double-wrap (acceptable, maintains safety)

3. **Mentions in URLs**: `https://github.com/@user` remains unchanged (@ not preceded by whitespace, correctly ignored)

4. **Partial usernames**: `@a` (single char) is valid and sanitized correctly

5. **Invalid patterns**: `@@user`, `@-user`, `@user-` won't match pattern (correct behavior)

6. **None/empty bodies**: Handled gracefully by sanitizer

### Error Handling

- Sanitizer returns input unchanged if None or empty
- Regex errors: Pattern is static and tested, no runtime regex failures expected
- Wrapper functions: Let metadata footer functions raise their own errors (don't suppress)

## Future Extensibility

This design supports future sanitization types:

### Phase 2: Issue/PR References

Add to `sanitizers.py`:
```python
def sanitize_issue_references(text: str) -> str:
    """Disable #123 issue reference autolinks."""
    # Implementation TBD
```

Update wrapper functions to chain sanitizers:
```python
def prepare_issue_body_for_restore(...):
    # ...
    body = sanitize_mentions(body)
    body = sanitize_issue_references(body)
    return body
```

### Phase 3: Repository References

```python
def sanitize_repo_references(text: str) -> str:
    """Disable owner/repo#123 cross-repository autolinks."""
```

### Phase 4: Commit References

```python
def sanitize_commit_references(text: str) -> str:
    """Disable SHA commit autolinks."""
```

### Implementation Pattern

Each new sanitization type:
1. Add function to `sanitizers.py` with tests
2. Update wrapper functions in `metadata.py` to chain the new sanitizer
3. No changes needed in restore strategies (automatic)

## Implementation Checklist

### Phase 1: Core Sanitization

- [x] Create `github_data/github/sanitizers.py` with `sanitize_mentions()`
- [x] Add unit tests in `tests/unit/github/test_sanitizers.py`
- [x] Verify regex pattern handles all username formats

### Phase 2: Metadata Wrappers

- [x] Add `prepare_issue_body_for_restore()` to metadata.py
- [x] Add `prepare_comment_body_for_restore()` to metadata.py
- [x] Add `prepare_pr_body_for_restore()` to metadata.py
- [x] Add `prepare_pr_comment_body_for_restore()` to metadata.py
- [x] Add `prepare_pr_review_body_for_restore()` to metadata.py
- [x] Add `prepare_pr_review_comment_body_for_restore()` to metadata.py
- [x] Add unit tests for each wrapper function

### Phase 3: Restore Strategy Updates

- [x] Update `issues/restore_strategy.py` to use new wrapper
- [x] Update `comments/restore_strategy.py` to use new wrapper
- [x] Update `pull_requests/restore_strategy.py` to use new wrapper
- [x] Update `pr_comments/restore_strategy.py` to use new wrapper
- [x] Update `pr_reviews/restore_strategy.py` to use new wrapper
- [x] Update `pr_review_comments/restore_strategy.py` to use new wrapper

### Phase 4: Integration Testing

- [x] Run existing integration tests, verify they pass
- [x] Add integration test cases with @mentions in content
- [x] Verify sanitization in end-to-end workflows

### Phase 5: Manual Verification

- [x] Create test repository with @mention content
- [x] Save repository data
- [x] Run preview utility to verify sanitization detection
- [ ] Restore to new repository
- [ ] Verify mentions sanitized correctly
- [ ] Verify no notifications triggered
- [ ] Document any issues or edge cases discovered

**Testing Utility:**
```bash
# Quick preview without restore
python scripts/preview_sanitization.py ./save

# Example output:
# Issue #42 - body:
#   Original:  Thanks @john for reviewing this PR
#   Sanitized: Thanks `@john` for reviewing this PR
```

## Success Criteria

1. All @mentions in restored content are wrapped in backticks
2. No GitHub notifications sent to mentioned users
3. Original usernames preserved and readable
4. All tests pass (unit, integration, container)
5. No regression in existing restore functionality
6. Code follows project standards (Clean Code, type hints, docstrings)

## Non-Goals (Future Work)

- Issue reference sanitization (#123)
- PR reference sanitization
- Commit SHA sanitization
- Repository reference sanitization (owner/repo#123)
- Configurable sanitization (all-or-nothing for now)

## Implementation Notes - Phase 3

**Completed:** 2025-11-20

**Changes Made:**
1. Updated 6 restore strategy files to use metadata preparation wrappers
2. Added 6 new unit test files for sanitization verification
3. All existing integration tests continue to pass (634 tests)
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

**Commits:**
- `31bc575` - feat(issues): integrate mention sanitization in restore strategy
- `46add02` - feat(comments): integrate mention sanitization in restore strategy
- `e2373c0` - feat(pull_requests): integrate mention sanitization in restore strategy
- `d1080ea` - feat(pr_comments): integrate mention sanitization in restore strategy
- `d135df4` - feat(pr_reviews): integrate mention sanitization in restore strategy
- `7232970` - feat(pr_review_comments): integrate mention sanitization in restore strategy
- `66ab21f` - style: apply black formatting to sanitization test files

**Test Results:**
- All 564 unit tests pass
- All 634 fast tests pass (unit + integration)
- Code coverage: 68.15%
- No regressions detected
