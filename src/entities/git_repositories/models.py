"""Git repository data models and enums."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class GitBackupFormat(Enum):
    """Git backup format options."""

    MIRROR = "mirror"


class GitAuthMethod(Enum):
    """Git authentication method options."""

    TOKEN = "token"
    SSH = "ssh"


@dataclass
class GitRepositoryInfo:
    """Git repository information model."""

    repo_name: str
    repo_url: str
    backup_format: GitBackupFormat
    size_bytes: Optional[int] = None
    commit_count: Optional[int] = None
    branch_count: Optional[int] = None
    tag_count: Optional[int] = None


@dataclass
class GitOperationResult:
    """Result of a Git operation."""

    success: bool
    backup_format: str
    destination: Optional[str] = None
    size_bytes: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
