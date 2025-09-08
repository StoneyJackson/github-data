"""
Data models for GitHub entities.

These Pydantic models provide type-safe representations of GitHub data
that will be serialized to/from JSON files.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class GitHubUser(BaseModel):
    """GitHub user information."""

    login: str
    id: int
    avatar_url: str
    html_url: str


class Label(BaseModel):
    """GitHub repository label."""

    name: str
    color: str
    description: Optional[str] = None
    url: str
    id: int


class Comment(BaseModel):
    """GitHub issue or pull request comment."""

    id: int
    body: str
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    html_url: str
    issue_url: str


class Issue(BaseModel):
    """GitHub repository issue."""

    id: int
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
    html_url: str
    comments_count: int = Field(alias="comments")

    model_config = ConfigDict(populate_by_name=True)


class RepositoryData(BaseModel):
    """Complete repository data for backup/restore."""

    repository_name: str
    exported_at: datetime
    labels: List[Label] = Field(default_factory=list)
    issues: List[Issue] = Field(default_factory=list)
    comments: List[Comment] = Field(default_factory=list)
