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
        """Clone repository to destination path."""
        try:
            # Ensure destination parent exists
            destination.parent.mkdir(parents=True, exist_ok=True)

            if backup_format == GitBackupFormat.MIRROR:
                result = self._clone_mirror(repo_url, destination)
            elif backup_format == GitBackupFormat.BUNDLE:
                result = self._create_bundle(repo_url, destination)
            elif backup_format == GitBackupFormat.BOTH:
                # Create both mirror and bundle
                mirror_result = self._clone_mirror(repo_url, destination)
                bundle_path = destination.with_suffix(".bundle")
                bundle_result = self._create_bundle(repo_url, bundle_path)

                result = {
                    "success": True,
                    "backup_format": backup_format.value,
                    "mirror": mirror_result,
                    "bundle": bundle_result,
                }
            else:
                raise ValueError(f"Unsupported backup format: {backup_format}")

            return GitOperationResult(
                success=result.get("success", True),
                backup_format=backup_format.value,
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

    def _create_bundle(self, repo_url: str, bundle_path: Path) -> Dict[str, Any]:
        """Create bundle backup of repository."""
        return self._command_executor.execute_clone_bundle(repo_url, bundle_path)

    def update_repository(
        self, repo_path: Path, backup_format: GitBackupFormat = GitBackupFormat.MIRROR
    ) -> GitOperationResult:
        """Update existing repository backup."""
        if not repo_path.exists():
            return GitOperationResult(
                success=False,
                backup_format=backup_format.value,
                error=f"Repository backup not found: {repo_path}",
            )

        try:
            if backup_format == GitBackupFormat.MIRROR:
                result = self._update_mirror(repo_path)
            elif backup_format == GitBackupFormat.BUNDLE:
                # For bundles, we need to recreate from original URL
                # This would require storing metadata about original URL
                raise NotImplementedError("Bundle updates require original URL")
            else:
                raise ValueError(f"Unsupported backup format: {backup_format}")

            return GitOperationResult(
                success=result.get("success", True),
                backup_format=backup_format.value,
                destination=result.get("path"),
                size_bytes=result.get("size_bytes"),
                metadata=result,
            )

        except Exception as e:
            return GitOperationResult(
                success=False, backup_format=backup_format.value, error=str(e)
            )

    def _update_mirror(self, mirror_path: Path) -> Dict[str, Any]:
        """Update mirror clone."""
        result = self._command_executor.execute_remote_update(mirror_path)
        repo_stats = self._command_executor.get_repository_stats(mirror_path)
        result.update(repo_stats)
        return result

    def validate_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Validate repository integrity."""
        try:
            if not repo_path.exists():
                return {"valid": False, "error": "Repository path does not exist"}

            if repo_path.suffix == ".bundle":
                return self._validate_bundle(repo_path)
            else:
                return self._command_executor.execute_fsck(repo_path)

        except Exception as e:
            return {"valid": False, "error": str(e)}

    def _validate_bundle(self, bundle_path: Path) -> Dict[str, Any]:
        """Validate bundle file."""
        cmd = ["git", "bundle", "verify", str(bundle_path)]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        return {
            "valid": result.returncode == 0,
            "verify_output": result.stdout if result.returncode == 0 else result.stderr,
        }

    def get_repository_info(self, repo_path: Path) -> GitRepositoryInfo:
        """Get repository metadata and statistics."""
        if repo_path.suffix == ".bundle":
            info = self._get_bundle_info(repo_path)
            return GitRepositoryInfo(
                repo_name=repo_path.stem,
                repo_url="",
                backup_format=GitBackupFormat.BUNDLE,
                size_bytes=info.get("file_size"),
            )
        else:
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

    def _get_bundle_info(self, bundle_path: Path) -> Dict[str, Any]:
        """Get bundle file information."""
        return {"file_size": bundle_path.stat().st_size, "is_bundle": True}

    def restore_repository(
        self,
        backup_path: Path,
        destination: Path,
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR,
    ) -> GitOperationResult:
        """Restore repository from backup."""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)

            if backup_format == GitBackupFormat.MIRROR:
                result = self._restore_from_mirror(backup_path, destination)
            elif backup_format == GitBackupFormat.BUNDLE:
                result = self._restore_from_bundle(backup_path, destination)
            else:
                raise ValueError(f"Unsupported backup format: {backup_format}")

            return GitOperationResult(
                success=result.get("success", True),
                backup_format=backup_format.value,
                destination=result.get("destination"),
                size_bytes=result.get("size_bytes"),
                metadata=result,
            )

        except Exception as e:
            return GitOperationResult(
                success=False, backup_format=backup_format.value, error=str(e)
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

    def _restore_from_bundle(
        self, bundle_path: Path, destination: Path
    ) -> Dict[str, Any]:
        """Restore from bundle backup."""
        # Initialize new repository
        init_cmd = ["git", "init", str(destination)]
        init_result = subprocess.run(
            init_cmd, capture_output=True, text=True, timeout=30
        )

        if init_result.returncode != 0:
            raise RuntimeError(f"Git init failed: {init_result.stderr}")

        # Pull from bundle
        pull_cmd = ["git", "-C", str(destination), "pull", str(bundle_path), "main"]
        pull_result = subprocess.run(
            pull_cmd, capture_output=True, text=True, timeout=self._git_timeout
        )

        if pull_result.returncode != 0:
            raise RuntimeError(f"Git restore from bundle failed: {pull_result.stderr}")

        return {
            "success": True,
            "method": "restore_from_bundle",
            "destination": str(destination),
            "size_bytes": self._command_executor.get_directory_size(destination),
        }
