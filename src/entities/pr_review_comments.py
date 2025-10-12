"""Pull request review comment entity model.

This module defines the PullRequestReviewComment entity model for representing
GitHub pull request review comments (inline code review comments).
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .users import GitHubUser


@dataclass
class PullRequestReviewComment:
    """Represents a GitHub pull request review comment."""

    id: str
    review_id: str
    pr_number: int
    diff_hunk: str
    path: str
    line: Optional[int]
    body: str
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    html_url: str
    pull_request_url: str
    in_reply_to_id: Optional[str] = None