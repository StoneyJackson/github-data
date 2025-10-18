"""Pull request entity models."""

from datetime import datetime
from typing import List, Union, Optional
from pydantic import BaseModel, Field, ConfigDict

from ..users.models import GitHubUser
from ..labels.models import Label
from ..milestones.models import Milestone


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
    milestone: Optional[Milestone] = None
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
