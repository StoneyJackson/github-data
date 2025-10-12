"""Pull request review entity models."""

from datetime import datetime
from typing import Union, Optional
from pydantic import BaseModel

from ..users.models import GitHubUser


class PullRequestReview(BaseModel):
    """GitHub pull request review."""

    id: Union[int, str]
    pr_number: int
    user: GitHubUser
    body: Optional[str] = None
    state: str  # PENDING, APPROVED, CHANGES_REQUESTED, DISMISSED
    html_url: str
    pull_request_url: str
    author_association: str
    submitted_at: Optional[datetime] = None
    commit_id: Optional[str] = None

    @property
    def pull_request_number(self) -> int:
        """Extract PR number from pull_request_url."""
        return int(self.pull_request_url.split("/")[-1])
