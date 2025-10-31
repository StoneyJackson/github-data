"""Abstract protocols for Git repository operations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
from github_data.entities.git_repositories.models import (
    GitBackupFormat,
    GitOperationResult,
    GitRepositoryInfo,
)


class GitRepositoryService(ABC):
    """Abstract interface for Git repository operations."""

    @abstractmethod
    def clone_repository(
        self,
        repo_url: str,
        destination: Path,
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR,
    ) -> GitOperationResult:
        """Clone repository to destination path."""
        pass

    @abstractmethod
    def update_repository(
        self, repo_path: Path, backup_format: GitBackupFormat = GitBackupFormat.MIRROR
    ) -> GitOperationResult:
        """Update existing repository backup."""
        pass

    @abstractmethod
    def validate_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Validate repository integrity."""
        pass

    @abstractmethod
    def get_repository_info(self, repo_path: Path) -> GitRepositoryInfo:
        """Get repository metadata and statistics."""
        pass

    @abstractmethod
    def restore_repository(
        self,
        backup_path: Path,
        destination: Path,
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR,
    ) -> GitOperationResult:
        """Restore repository from backup."""
        pass


class GitCommandExecutor(ABC):
    """Abstract interface for low-level Git command execution."""

    @abstractmethod
    def execute_clone_mirror(self, repo_url: str, destination: Path) -> Dict[str, Any]:
        """Execute git clone --mirror command."""
        pass

    @abstractmethod
    def execute_remote_update(self, repo_path: Path) -> Dict[str, Any]:
        """Execute git remote update command."""
        pass

    @abstractmethod
    def execute_fsck(self, repo_path: Path) -> Dict[str, Any]:
        """Execute git fsck command."""
        pass

    @abstractmethod
    def get_repository_stats(self, repo_path: Path) -> Dict[str, Any]:
        """Get repository statistics via Git commands."""
        pass

    @abstractmethod
    def get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        pass
