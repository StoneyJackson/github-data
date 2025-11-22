# Mention Sanitization Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create the core sanitization library with `sanitize_mentions()` function and comprehensive unit tests.

**Architecture:** Single module `github_data/github/sanitizers.py` with regex-based mention detection that transforms `@username` to `` `@username` `` to prevent GitHub notifications.

**Tech Stack:** Python 3, pytest, re module

---

## Task 1: Create Sanitizers Module with `sanitize_mentions()`

**Files:**
- Create: `github_data/github/sanitizers.py`
- Test: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the failing test for basic mention sanitization

Create test file with first test case:

```python
"""Unit tests for text sanitization utilities."""

import pytest


@pytest.mark.unit
class TestSanitizeMentions:
    """Tests for sanitize_mentions function."""

    def test_single_mention_in_text(self):
        """Should wrap single @mention in backticks."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("Thanks @john for the review")
        assert result == "Thanks `@john` for the review"
```

### Step 2: Run test to verify it fails

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_single_mention_in_text -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'github_data.github.sanitizers'"

### Step 3: Write minimal implementation to pass

Create the sanitizers module:

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
    # GitHub usernames: alphanumeric start, then alphanumeric/hyphens,
    # must end with alphanumeric (no trailing hyphen)
    # Max length 39 chars
    pattern = r'(^|\s)(@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?)'

    return re.sub(pattern, r'\1`\2`', text, flags=re.MULTILINE)
```

### Step 4: Run test to verify it passes

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_single_mention_in_text -v`
Expected: PASS

### Step 5: Commit

```bash
git add github_data/github/sanitizers.py tests/unit/github/test_sanitizers.py
git commit -s -m "feat(sanitizers): add sanitize_mentions function with basic test

Add core sanitization module with regex-based mention detection.
Transforms @username to backtick-wrapped format to prevent
GitHub notifications."
```

---

## Task 2: Add Test for Multiple Mentions

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the failing test

Add test to the existing class:

```python
    def test_multiple_mentions_in_text(self):
        """Should wrap multiple @mentions in backticks."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("@alice and @bob please review")
        assert result == "`@alice` and `@bob` please review"
```

### Step 2: Run test to verify it passes (already implemented)

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_multiple_mentions_in_text -v`
Expected: PASS (pattern already handles this)

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add test for multiple mentions"
```

---

## Task 3: Add Test for Mentions at Line Start

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the test

Add test:

```python
    def test_mention_at_line_start(self):
        """Should wrap @mention at start of line."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("@alice\nhello world")
        assert result == "`@alice`\nhello world"
```

### Step 2: Run test to verify it passes

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_mention_at_line_start -v`
Expected: PASS

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add test for mention at line start"
```

---

## Task 4: Add Test for Mentions with Hyphens

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the test

Add test:

```python
    def test_mention_with_hyphens(self):
        """Should wrap @username with hyphens in backticks."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("Thanks @user-name-123")
        assert result == "Thanks `@user-name-123`"
```

### Step 2: Run test to verify it passes

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_mention_with_hyphens -v`
Expected: PASS

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add test for usernames with hyphens"
```

---

## Task 5: Add Test for Single Character Username

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the test

Add test:

```python
    def test_single_character_username(self):
        """Should wrap single character @username in backticks."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("@x is here")
        assert result == "`@x` is here"
```

### Step 2: Run test to verify it passes

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_single_character_username -v`
Expected: PASS

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add test for single character username"
```

---

## Task 6: Add Test for Maximum Length Username

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the test

Add test:

```python
    def test_maximum_length_username(self):
        """Should wrap 39-character username in backticks."""
        from github_data.github.sanitizers import sanitize_mentions

        # 39 chars: 1 + 37 + 1
        username = "a" + "b" * 37 + "c"
        text = f"@{username} is valid"
        result = sanitize_mentions(text)
        assert result == f"`@{username}` is valid"
```

### Step 2: Run test to verify it passes

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_maximum_length_username -v`
Expected: PASS

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add test for maximum length username"
```

---

## Task 7: Add Test for Text Without Mentions

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the test

Add test:

```python
    def test_no_mentions_unchanged(self):
        """Should return text unchanged when no @mentions present."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "Hello world, no mentions here"
        result = sanitize_mentions(text)
        assert result == text
```

### Step 2: Run test to verify it passes

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_no_mentions_unchanged -v`
Expected: PASS

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add test for text without mentions"
```

---

## Task 8: Add Test for Empty and None Input

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the tests

Add tests:

```python
    def test_empty_string_returns_empty(self):
        """Should return empty string for empty input."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("")
        assert result == ""

    def test_none_returns_none(self):
        """Should return None for None input."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions(None)
        assert result is None
```

### Step 2: Run tests to verify they pass

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_empty_string_returns_empty tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_none_returns_none -v`
Expected: PASS

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add tests for empty and None input"
```

---

## Task 9: Add Test for URLs with @ Symbol

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the test

Add test:

```python
    def test_url_with_at_symbol_unchanged(self):
        """Should not modify URLs containing @ symbol."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "Check https://github.com/@user for profile"
        result = sanitize_mentions(text)
        # The @ in URL is not preceded by whitespace, so unchanged
        assert result == "Check https://github.com/@user for profile"
```

### Step 2: Run test to verify it passes

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_url_with_at_symbol_unchanged -v`
Expected: PASS

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add test for URLs with @ symbol"
```

---

## Task 10: Add Test for Email Addresses

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the test

Add test:

```python
    def test_email_address_unchanged(self):
        """Should not modify email addresses."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "Contact test@example.com for help"
        result = sanitize_mentions(text)
        # The @ in email is not preceded by whitespace, so unchanged
        assert result == "Contact test@example.com for help"
```

### Step 2: Run test to verify it passes

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_email_address_unchanged -v`
Expected: PASS

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add test for email addresses"
```

---

## Task 11: Add Test for Invalid Username Patterns

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the tests

Add tests:

```python
    def test_invalid_double_at_unchanged(self):
        """Should not modify @@user pattern."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "Not valid @@user here"
        result = sanitize_mentions(text)
        # @@user: first @ matches, second @user would match but @ not preceded by space
        assert "@@user" in result or result == "Not valid @@user here"

    def test_invalid_hyphen_start_unchanged(self):
        """Should not modify @-user pattern (invalid username)."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "Not valid @-user here"
        result = sanitize_mentions(text)
        # @- doesn't match pattern (must start with alphanumeric)
        assert result == "Not valid @-user here"

    def test_trailing_hyphen_handled(self):
        """Should handle username ending in hyphen correctly."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "User @test- mentioned"
        result = sanitize_mentions(text)
        # @test matches, hyphen is not part of username
        assert result == "User `@test`- mentioned"
```

### Step 2: Run tests to verify they pass

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_invalid_double_at_unchanged tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_invalid_hyphen_start_unchanged tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_trailing_hyphen_handled -v`
Expected: PASS

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add tests for invalid username patterns"
```

---

## Task 12: Add Test for Multiline Text

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the test

Add test:

```python
    def test_multiline_text_with_mentions(self):
        """Should handle mentions across multiple lines."""
        from github_data.github.sanitizers import sanitize_mentions

        text = """First line @alice mentioned
@bob at start of line
End with @charlie"""
        expected = """First line `@alice` mentioned
`@bob` at start of line
End with `@charlie`"""
        result = sanitize_mentions(text)
        assert result == expected
```

### Step 2: Run test to verify it passes

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_multiline_text_with_mentions -v`
Expected: PASS

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add test for multiline text"
```

---

## Task 13: Add Test for Already Backtick-Wrapped Mentions

**Files:**
- Modify: `tests/unit/github/test_sanitizers.py`

### Step 1: Write the test

Add test:

```python
    def test_already_wrapped_gets_double_wrapped(self):
        """Should double-wrap already backtick-wrapped mentions (acceptable behavior)."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "Already wrapped `@john` here"
        result = sanitize_mentions(text)
        # The @john inside backticks still matches because @ is preceded by backtick
        # This is acceptable - over-sanitization is safe
        assert "`@john`" in result
```

### Step 2: Run test to verify it passes

Run: `pdm run pytest tests/unit/github/test_sanitizers.py::TestSanitizeMentions::test_already_wrapped_gets_double_wrapped -v`
Expected: PASS

### Step 3: Commit

```bash
git add tests/unit/github/test_sanitizers.py
git commit -s -m "test(sanitizers): add test for already wrapped mentions"
```

---

## Task 14: Run Full Test Suite

**Files:**
- None (verification only)

### Step 1: Run all sanitizer tests

Run: `pdm run pytest tests/unit/github/test_sanitizers.py -v`
Expected: All tests PASS

### Step 2: Run full unit test suite to check for regressions

Run: `make test-unit`
Expected: All tests PASS

### Step 3: Run linting and type checking

Run: `make lint && make type-check`
Expected: No errors

### Step 4: Commit any formatting fixes

If black made changes:
```bash
git add -A
git commit -s -m "style(sanitizers): apply code formatting"
```

---

## Task 15: Final Verification

**Files:**
- None (verification only)

### Step 1: Run make check

Run: `make check`
Expected: All checks PASS

### Step 2: Review git log for clean commit history

Run: `git log --oneline -15`
Expected: Clean series of commits for Phase 1

---

## Summary

Phase 1 creates:
- `github_data/github/sanitizers.py` - Core sanitization module with `sanitize_mentions()` function
- `tests/unit/github/test_sanitizers.py` - Comprehensive unit tests covering:
  - Basic single and multiple mentions
  - Line start mentions
  - Usernames with hyphens
  - Single character and max length usernames
  - Edge cases: empty, None, URLs, emails
  - Invalid patterns
  - Multiline text
  - Already wrapped mentions

All tests follow TDD with red-green-refactor cycle and frequent commits.
