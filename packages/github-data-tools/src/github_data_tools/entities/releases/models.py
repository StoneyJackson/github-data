"""GitHub release entity models."""

from datetime import datetime
from typing import Optional, Union, List
from pydantic import BaseModel, ConfigDict
from github_data_tools.entities.users.models import GitHubUser


class ReleaseAsset(BaseModel):
    """Release asset (binary attachment)."""

    id: Union[int, str]
    name: str
    content_type: str
    size: int
    download_count: int
    browser_download_url: str
    created_at: datetime
    updated_at: datetime
    uploader: GitHubUser
    local_path: Optional[str] = None  # Path when downloaded

    model_config = ConfigDict(populate_by_name=True)


class Release(BaseModel):
    """GitHub release entity."""

    id: Union[int, str]
    tag_name: str
    target_commitish: str  # Branch or commit SHA
    name: Optional[str] = None
    body: Optional[str] = None  # Release notes (markdown)
    draft: bool = False
    prerelease: bool = False
    immutable: bool = False  # New 2025 GitHub feature
    created_at: datetime
    published_at: Optional[datetime] = None
    author: GitHubUser
    assets: List[ReleaseAsset] = []
    html_url: str

    model_config = ConfigDict(populate_by_name=True)
