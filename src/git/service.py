"""Git repository service implementation."""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from .protocols import GitRepositoryService, GitCommandExecutor
from .command_executor import GitCommandExecutorImpl
from src.entities.git_repositories.models import (
    GitBackupFormat,
    GitOperationResult,
    GitRepositoryInfo,
)


class GitRepositoryServiceImpl(GitRepositoryService):
    """High-level Git repository operations orchestration."""

    def __init__(
        self,
        command_executor: Optional[GitCommandExecutor] = None,
        auth_token: Optional[str] = None,
    ):
        self._command_executor = command_executor or GitCommandExecutorImpl(auth_token)
        self._auth_token = auth_token
        self._git_timeout = 300

    def clone_repository(
        self,
        repo_url: str,
        destination: Path,
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR,
    ) -> GitOperationResult:
        """Clone repository to destination path using mirror format."""
        try:
            # Ensure destination parent exists
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Only mirror format is supported
            result = self._clone_mirror(repo_url, destination)

            return GitOperationResult(
                success=result.get("success", True),
                backup_format=GitBackupFormat.MIRROR.value,
                destination=result.get("destination"),
                size_bytes=result.get("size_bytes"),
                metadata=result,
            )

        except Exception as e:
            return GitOperationResult(
                success=False, backup_format=backup_format.value, error=str(e)
            )

    def _clone_mirror(self, repo_url: str, destination: Path) -> Dict[str, Any]:
        """Create mirror clone of repository."""
        return self._command_executor.execute_clone_mirror(repo_url, destination)


    def update_repository(
        self, repo_path: Path, backup_format: GitBackupFormat = GitBackupFormat.MIRROR
    ) -> GitOperationResult:
        """Update existing repository backup using mirror format."""
        if not repo_path.exists():
            return GitOperationResult(
                success=False,
                backup_format=GitBackupFormat.MIRROR.value,
                error=f"Repository backup not found: {repo_path}",
            )

        try:
            # Only mirror format is supported
            result = self._update_mirror(repo_path)

            return GitOperationResult(
                success=result.get("success", True),
                backup_format=GitBackupFormat.MIRROR.value,
                destination=result.get("path"),
                size_bytes=result.get("size_bytes"),
                metadata=result,
            )

        except Exception as e:
            return GitOperationResult(
                success=False, backup_format=GitBackupFormat.MIRROR.value, error=str(e)
            )

    def _update_mirror(self, mirror_path: Path) -> Dict[str, Any]:
        """Update mirror clone."""
        result = self._command_executor.execute_remote_update(mirror_path)
        repo_stats = self._command_executor.get_repository_stats(mirror_path)
        result.update(repo_stats)
        return result

    def validate_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Validate repository integrity using mirror format."""
        try:
            if not repo_path.exists():
                return {"valid": False, "error": "Repository path does not exist"}

            # Only mirror format is supported
            return self._command_executor.execute_fsck(repo_path)

        except Exception as e:
            return {"valid": False, "error": str(e)}


    def get_repository_info(self, repo_path: Path) -> GitRepositoryInfo:
        """Get repository metadata and statistics using mirror format."""
        # Only mirror format is supported
        info = self._command_executor.get_repository_stats(repo_path)
        return GitRepositoryInfo(
            repo_name=repo_path.name,
            repo_url="",
            backup_format=GitBackupFormat.MIRROR,
            size_bytes=self._command_executor.get_directory_size(repo_path),
            commit_count=info.get("commit_count"),
            branch_count=info.get("branch_count"),
            tag_count=info.get("tag_count"),
        )


    def restore_repository(
        self,
        backup_path: Path,
        destination: Path,
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR,
    ) -> GitOperationResult:
        """Restore repository from backup using mirror format."""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Only mirror format is supported
            result = self._restore_from_mirror(backup_path, destination)

            return GitOperationResult(
                success=result.get("success", True),
                backup_format=GitBackupFormat.MIRROR.value,
                destination=result.get("destination"),
                size_bytes=result.get("size_bytes"),
                metadata=result,
            )

        except Exception as e:
            return GitOperationResult(
                success=False, backup_format=GitBackupFormat.MIRROR.value, error=str(e)
            )

    def _restore_from_mirror(
        self, mirror_path: Path, destination: Path
    ) -> Dict[str, Any]:
        """Restore from mirror backup."""
        # Clone from local mirror
        cmd = ["git", "clone", str(mirror_path), str(destination)]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=self._git_timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"Git restore from mirror failed: {result.stderr}")

        return {
            "success": True,
            "method": "restore_from_mirror",
            "destination": str(destination),
            "size_bytes": self._command_executor.get_directory_size(destination),
        }

