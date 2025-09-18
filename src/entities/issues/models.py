"""Issue entity models."""

from datetime import datetime
from typing import List, Union, Optional
from pydantic import BaseModel, Field, ConfigDict

from ..base.models import GitHubUser
from ..labels.models import Label


class SubIssue(BaseModel):
    """GitHub sub-issue relationship."""

    sub_issue_id: Union[int, str]
    sub_issue_number: int
    parent_issue_id: Union[int, str]
    parent_issue_number: int
    position: int


class Issue(BaseModel):
    """GitHub repository issue."""

    id: Union[int, str]
    number: int
    title: str
    body: Optional[str] = None
    state: str
    user: GitHubUser
    assignees: List[GitHubUser] = Field(default_factory=list)
    labels: List[Label] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    closed_by: Optional[GitHubUser] = None
    state_reason: Optional[str] = None
    html_url: str
    comments_count: int = Field(alias="comments")
    sub_issues: List["SubIssue"] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)
