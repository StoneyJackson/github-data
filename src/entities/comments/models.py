"""Comment entity models."""

from datetime import datetime
from typing import Union
from pydantic import BaseModel

from ..users.models import GitHubUser


class Comment(BaseModel):
    """GitHub issue comment."""

    id: Union[int, str]
    body: str
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    html_url: str
    issue_url: str

    @property
    def issue_number(self) -> int:
        """Extract issue number from issue_url."""
        return int(self.issue_url.split("/")[-1])
