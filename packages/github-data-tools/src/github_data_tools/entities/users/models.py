"""User entity models."""

from typing import Optional, Union
from pydantic import BaseModel


class GitHubUser(BaseModel):
    """GitHub user information."""

    login: str
    id: Optional[Union[int, str]] = None
    avatar_url: Optional[str] = None
    html_url: Optional[str] = None
