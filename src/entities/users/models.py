"""User entity models."""

from typing import Union
from pydantic import BaseModel


class GitHubUser(BaseModel):
    """GitHub user information."""

    login: str
    id: Union[int, str]
    avatar_url: str
    html_url: str
