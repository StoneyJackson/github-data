"""Pull request entity models."""

from datetime import datetime
from typing import List, Union, Optional
from pydantic import BaseModel, Field, ConfigDict

from ..users.models import GitHubUser
from ..labels.models import Label


class PullRequest(BaseModel):
    """GitHub repository pull request."""

    id: Union[int, str]
    number: int
    title: str
    body: Optional[str] = None
    state: str  # OPEN, CLOSED, MERGED
    user: GitHubUser  # author
    assignees: List[GitHubUser] = Field(default_factory=list)
    labels: List[Label] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    merge_commit_sha: Optional[str] = None
    base_ref: str  # base branch
    head_ref: str  # head branch
    html_url: str
    comments_count: int = Field(alias="comments")

    model_config = ConfigDict(populate_by_name=True)


class PullRequestComment(BaseModel):
    """GitHub pull request comment."""

    id: Union[int, str]
    body: str
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    html_url: str
    pull_request_url: str

    @property
    def pull_request_number(self) -> int:
        """Extract pull request number from pull_request_url."""
        return int(self.pull_request_url.split("/")[-1])
