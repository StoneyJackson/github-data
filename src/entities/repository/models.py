"""Repository entity models."""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

from ..labels.models import Label
from ..issues.models import Issue, SubIssue
from ..comments.models import Comment
from ..pull_requests.models import PullRequest, PullRequestComment


class RepositoryData(BaseModel):
    """Complete repository data for backup/restore."""

    repository_name: str
    exported_at: datetime
    labels: List[Label] = Field(default_factory=list)
    issues: List[Issue] = Field(default_factory=list)
    comments: List[Comment] = Field(default_factory=list)
    pull_requests: List[PullRequest] = Field(default_factory=list)
    pr_comments: List[PullRequestComment] = Field(default_factory=list)
    sub_issues: List[SubIssue] = Field(default_factory=list)
