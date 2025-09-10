"""
Metadata formatting utilities for preserving original issue/comment information.

Provides functions to append original author and timestamp metadata to
issue and comment bodies during restore operations.
"""

from datetime import datetime

from ..models import Issue, Comment


def add_issue_metadata_footer(issue: Issue) -> str:
    """
    Add original metadata footer to an issue body.

    Args:
        issue: The original issue with metadata to preserve

    Returns:
        The issue body with metadata footer appended
    """
    original_body = issue.body or ""
    metadata_footer = _format_issue_metadata(issue)

    if original_body:
        return f"{original_body}\n\n{metadata_footer}"
    else:
        return metadata_footer


def add_comment_metadata_footer(comment: Comment) -> str:
    """
    Add original metadata footer to a comment body.

    Args:
        comment: The original comment with metadata to preserve

    Returns:
        The comment body with metadata footer appended
    """
    original_body = comment.body
    metadata_footer = _format_comment_metadata(comment)

    return f"{original_body}\n\n{metadata_footer}"


def _format_issue_metadata(issue: Issue) -> str:
    """Format issue metadata into a readable footer."""
    author = issue.user.login
    created_at = _format_datetime(issue.created_at)
    updated_at = _format_datetime(issue.updated_at)

    metadata_lines = ["---", f"*Originally created by @{author} on {created_at}*"]

    # Only add update time if different from creation time
    if issue.updated_at != issue.created_at:
        metadata_lines.append(f"*Last updated on {updated_at}*")

    # Add closed time if issue was closed
    if issue.closed_at:
        closed_at = _format_datetime(issue.closed_at)
        closed_info = f"*Closed on {closed_at}"

        # Add who closed it if available
        if issue.closed_by:
            closed_info += f" by @{issue.closed_by.login}"

        # Add state reason if available
        if issue.state_reason:
            closed_info += f" as {issue.state_reason}"

        closed_info += "*"
        metadata_lines.append(closed_info)

    return "\n".join(metadata_lines)


def _format_comment_metadata(comment: Comment) -> str:
    """Format comment metadata into a readable footer."""
    author = comment.user.login
    created_at = _format_datetime(comment.created_at)
    updated_at = _format_datetime(comment.updated_at)

    metadata_lines = ["---", f"*Originally posted by @{author} on {created_at}*"]

    # Only add update time if different from creation time
    if comment.updated_at != comment.created_at:
        metadata_lines.append(f"*Last updated on {updated_at}*")

    return "\n".join(metadata_lines)


def _format_datetime(dt: datetime) -> str:
    """Format datetime for display in metadata footer."""
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
