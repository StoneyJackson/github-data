"""
Text sanitization utilities for disabling GitHub autolinks.

Provides functions to sanitize user-generated content before restoring
to prevent unwanted notifications and cross-repository links.
"""

import re
from typing import Optional


def sanitize_mentions(text: Optional[str]) -> Optional[str]:
    """
    Disable GitHub user mention autolinks by wrapping in backticks.

    Transforms @username to `@username` to prevent notifications
    and autolink creation. Preserves the username text in its
    original location.

    Args:
        text: Text content that may contain @mentions, or None

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
    pattern = r"(^|\s)(@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?)"

    return re.sub(pattern, r"\1`\2`", text, flags=re.MULTILINE)
