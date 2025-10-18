"""GitHub milestone entity model."""

from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, ConfigDict
from src.entities.users.models import GitHubUser


class Milestone(BaseModel):
    """GitHub milestone entity following established entity patterns."""

    id: Union[int, str]
    number: int
    title: str
    description: Optional[str] = None
    state: str  # "open" | "closed"
    creator: GitHubUser
    created_at: datetime
    updated_at: datetime
    due_on: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    open_issues: int = 0
    closed_issues: int = 0
    html_url: str

    model_config = ConfigDict(populate_by_name=True)
