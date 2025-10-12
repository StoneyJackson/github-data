"""Pull request review entity model.

This module defines the PullRequestReview entity model for representing
GitHub pull request reviews.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .users import GitHubUser


@dataclass
class PullRequestReview:
    """Represents a GitHub pull request review."""

    id: str
    pr_number: int
    user: GitHubUser
    body: str
    state: str  # APPROVED, CHANGES_REQUESTED, COMMENTED, PENDING
    html_url: str
    pull_request_url: str
    author_association: str
    submitted_at: Optional[datetime] = None
    commit_id: Optional[str] = None