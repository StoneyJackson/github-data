"""Pull request comment entity models."""

from datetime import datetime
from typing import Union
from pydantic import BaseModel, computed_field

from ..users.models import GitHubUser


class PullRequestComment(BaseModel):
    """GitHub pull request comment."""

    id: Union[int, str]
    body: str
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    html_url: str
    pull_request_url: str

    @computed_field
    @property
    def pull_request_number(self) -> int:
        """Extract pull request number from pull_request_url."""
        return int(self.pull_request_url.split("/")[-1])
