"""
Metadata formatting utilities for preserving original issue/comment information.

Provides functions to append original author and timestamp metadata to
issue and comment bodies during restore operations.
"""

from datetime import datetime

from ..entities import (
    Issue,
    Comment,
    PullRequest,
    PullRequestComment,
    PullRequestReview,
    PullRequestReviewComment,
)


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


def add_pr_metadata_footer(pr: PullRequest) -> str:
    """
    Add original metadata footer to a pull request body.

    Args:
        pr: The original pull request with metadata to preserve

    Returns:
        The PR body with metadata footer appended
    """
    original_body = pr.body or ""
    metadata_footer = _format_pr_metadata(pr)

    if original_body:
        return f"{original_body}\n\n{metadata_footer}"
    else:
        return metadata_footer


def add_pr_comment_metadata_footer(comment: PullRequestComment) -> str:
    """
    Add original metadata footer to a PR comment body.

    Args:
        comment: The original PR comment with metadata to preserve

    Returns:
        The PR comment body with metadata footer appended
    """
    original_body = comment.body
    metadata_footer = _format_pr_comment_metadata(comment)

    return f"{original_body}\n\n{metadata_footer}"


def _format_pr_metadata(pr: PullRequest) -> str:
    """Format PR metadata into a readable footer."""
    author = pr.user.login
    created_at = _format_datetime(pr.created_at)
    updated_at = _format_datetime(pr.updated_at)

    metadata_lines = ["---", f"*Originally created by @{author} on {created_at}*"]

    # Only add update time if different from creation time
    if pr.updated_at != pr.created_at:
        metadata_lines.append(f"*Last updated on {updated_at}*")

    # Add closed/merged time if PR was closed
    if pr.closed_at:
        closed_at = _format_datetime(pr.closed_at)

        if pr.merged_at:
            merged_at = _format_datetime(pr.merged_at)
            metadata_lines.append(f"*Merged on {merged_at}*")
        else:
            metadata_lines.append(f"*Closed on {closed_at}*")

    # Add original branch info
    metadata_lines.append(f"*Original branches: {pr.head_ref} → {pr.base_ref}*")

    return "\n".join(metadata_lines)


def _format_pr_comment_metadata(comment: PullRequestComment) -> str:
    """Format PR comment metadata into a readable footer."""
    author = comment.user.login
    created_at = _format_datetime(comment.created_at)
    updated_at = _format_datetime(comment.updated_at)

    metadata_lines = ["---", f"*Originally posted by @{author} on {created_at}*"]

    # Only add update time if different from creation time
    if comment.updated_at != comment.created_at:
        metadata_lines.append(f"*Last updated on {updated_at}*")

    return "\n".join(metadata_lines)


def add_pr_review_metadata_footer(review: PullRequestReview) -> str:
    """
    Add original metadata footer to a pull request review body.

    Args:
        review: The original pull request review with metadata to preserve

    Returns:
        The review body with metadata footer appended
    """
    original_body = review.body or ""
    metadata_footer = _format_pr_review_metadata(review)

    if original_body:
        return f"{original_body}\n\n{metadata_footer}"
    else:
        return metadata_footer


def add_pr_review_comment_metadata_footer(comment: PullRequestReviewComment) -> str:
    """
    Add original metadata footer to a pull request review comment body.

    Args:
        comment: The original pull request review comment with metadata to preserve

    Returns:
        The review comment body with metadata footer appended
    """
    original_body = comment.body
    metadata_footer = _format_pr_review_comment_metadata(comment)

    return f"{original_body}\n\n{metadata_footer}"


def _format_pr_review_metadata(review: PullRequestReview) -> str:
    """Format PR review metadata into a readable footer."""
    author = review.user.login
    submitted_at = (
        _format_datetime(review.submitted_at) if review.submitted_at else "Unknown"
    )

    metadata_lines = [
        "",
        "---",
        "*Original Review Metadata:*",
        f"- **Original ID:** {review.id}",
        f"- **Original Reviewer:** @{author}",
        f"- **Original State:** {review.state}",
        f"- **Original Submitted:** {submitted_at}",
        f"- **Original URL:** {review.html_url}",
    ]

    return "\n".join(metadata_lines)


def _format_pr_review_comment_metadata(comment: PullRequestReviewComment) -> str:
    """Format PR review comment metadata into a readable footer."""
    author = comment.user.login
    created_at = _format_datetime(comment.created_at)

    metadata_lines = [
        "",
        "---",
        "*Original Review Comment Metadata:*",
        f"- **Original ID:** {comment.id}",
        f"- **Original Author:** @{author}",
        f"- **Original Path:** {comment.path}",
    ]

    if comment.line:
        metadata_lines.append(f"- **Original Line:** {comment.line}")

    metadata_lines.extend(
        [
            f"- **Original Created:** {created_at}",
            f"- **Original URL:** {comment.html_url}",
        ]
    )

    return "\n".join(metadata_lines)


def _format_datetime(dt: datetime) -> str:
    """Format datetime for display in metadata footer."""
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
