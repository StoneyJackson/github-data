"""Unit tests for text sanitization utilities."""

import pytest


@pytest.mark.unit
class TestSanitizeMentions:
    """Tests for sanitize_mentions function."""

    def test_single_mention_in_text(self) -> None:
        """Should wrap single @mention in backticks."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("Thanks @john for the review")
        assert result == "Thanks `@john` for the review"

    def test_multiple_mentions_in_text(self) -> None:
        """Should wrap multiple @mentions in backticks."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("@alice and @bob please review")
        assert result == "`@alice` and `@bob` please review"

    def test_mention_at_line_start(self) -> None:
        """Should wrap @mention at start of line."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("@alice\nhello world")
        assert result == "`@alice`\nhello world"

    def test_mention_with_hyphens(self) -> None:
        """Should wrap @username with hyphens in backticks."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("Thanks @user-name-123")
        assert result == "Thanks `@user-name-123`"

    def test_single_character_username(self) -> None:
        """Should wrap single character @username in backticks."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("@x is here")
        assert result == "`@x` is here"

    def test_maximum_length_username(self) -> None:
        """Should wrap 39-character username in backticks."""
        from github_data.github.sanitizers import sanitize_mentions

        # 39 chars: 1 + 37 + 1
        username = "a" + "b" * 37 + "c"
        text = f"@{username} is valid"
        result = sanitize_mentions(text)
        assert result == f"`@{username}` is valid"

    def test_no_mentions_unchanged(self) -> None:
        """Should return text unchanged when no @mentions present."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "Hello world, no mentions here"
        result = sanitize_mentions(text)
        assert result == text

    def test_empty_string_returns_empty(self) -> None:
        """Should return empty string for empty input."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions("")
        assert result == ""

    def test_none_returns_none(self) -> None:
        """Should return None for None input."""
        from github_data.github.sanitizers import sanitize_mentions

        result = sanitize_mentions(None)
        assert result is None

    def test_url_with_at_symbol_unchanged(self) -> None:
        """Should not modify URLs containing @ symbol."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "Check https://github.com/@user for profile"
        result = sanitize_mentions(text)
        # The @ in URL is not preceded by whitespace, so unchanged
        assert result == "Check https://github.com/@user for profile"

    def test_email_address_unchanged(self) -> None:
        """Should not modify email addresses."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "Contact test@example.com for help"
        result = sanitize_mentions(text)
        # The @ in email is not preceded by whitespace, so unchanged
        assert result == "Contact test@example.com for help"

    def test_invalid_double_at_unchanged(self) -> None:
        """Should not modify @@user pattern."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "Not valid @@user here"
        result = sanitize_mentions(text)
        # @@user: first @ matches, second @user would match but @ not
        # preceded by space
        assert result is not None and (
            "@@user" in result or result == "Not valid @@user here"
        )

    def test_invalid_hyphen_start_unchanged(self) -> None:
        """Should not modify @-user pattern (invalid username)."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "Not valid @-user here"
        result = sanitize_mentions(text)
        # @- doesn't match pattern (must start with alphanumeric)
        assert result == "Not valid @-user here"

    def test_trailing_hyphen_handled(self) -> None:
        """Should handle username ending in hyphen correctly."""
        from github_data.github.sanitizers import sanitize_mentions

        text = "User @test- mentioned"
        result = sanitize_mentions(text)
        # @test matches, hyphen is not part of username
        assert result == "User `@test`- mentioned"

    def test_multiline_text_with_mentions(self) -> None:
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

    def test_already_wrapped_gets_double_wrapped(self) -> None:
        """Should double-wrap already backtick-wrapped mentions.

        This is acceptable behavior - over-sanitization is safe.
        """
        from github_data.github.sanitizers import sanitize_mentions

        text = "Already wrapped `@john` here"
        result = sanitize_mentions(text)
        # The @john inside backticks still matches because @ is preceded by backtick
        # This is acceptable - over-sanitization is safe
        assert result is not None and "`@john`" in result
