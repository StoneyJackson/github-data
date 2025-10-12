"""Pull request review comment entity models."""

from datetime import datetime
from typing import Union, Optional
from pydantic import BaseModel

from ..users.models import GitHubUser


class PullRequestReviewComment(BaseModel):
    """GitHub pull request review comment."""

    id: Union[int, str]
    review_id: Union[int, str]
    pr_number: int
    diff_hunk: str
    path: str
    line: Optional[int] = None
    body: str
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    html_url: str
    pull_request_url: str
    in_reply_to_id: Optional[Union[int, str]] = None

    @property
    def pull_request_number(self) -> int:
        """Extract PR number from pull_request_url."""
        return int(self.pull_request_url.split("/")[-1])