"""Git command executor implementation."""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional
from .protocols import GitCommandExecutor


class GitCommandExecutorImpl(GitCommandExecutor):
    """Implementation of Git command executor."""

    def __init__(self, auth_token: Optional[str] = None, git_timeout: int = 300):
        self._auth_token = auth_token
        self._git_timeout = git_timeout

    def execute_clone_mirror(self, repo_url: str, destination: Path) -> Dict[str, Any]:
        """Execute git clone --mirror command."""
        # Prepare authenticated URL if token provided
        auth_url = self._prepare_authenticated_url(repo_url)

        cmd = ["git", "clone", "--mirror", auth_url, str(destination)]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=self._git_timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed: {result.stderr}")

        # Get repository statistics
        repo_info = self._get_mirror_info(destination)

        return {
            "success": True,
            "method": "mirror",
            "destination": str(destination),
            "size_bytes": self.get_directory_size(destination),
            **repo_info,
        }


    def execute_remote_update(self, repo_path: Path) -> Dict[str, Any]:
        """Execute git remote update command."""
        cmd = ["git", "-C", str(repo_path), "remote", "update"]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=self._git_timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"Git mirror update failed: {result.stderr}")

        return {
            "success": True,
            "method": "remote_update",
            "path": str(repo_path),
            "size_bytes": self.get_directory_size(repo_path),
        }

    def execute_fsck(self, repo_path: Path) -> Dict[str, Any]:
        """Execute git fsck command."""
        # Check if it's a valid git repository
        cmd = ["git", "-C", str(repo_path), "rev-parse", "--git-dir"]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return {"valid": False, "error": "Not a valid git repository"}

        # Run git fsck for integrity check
        fsck_cmd = ["git", "-C", str(repo_path), "fsck", "--full"]

        fsck_result = subprocess.run(
            fsck_cmd, capture_output=True, text=True, timeout=120
        )

        return {
            "valid": fsck_result.returncode == 0,
            "fsck_output": (
                fsck_result.stdout
                if fsck_result.returncode == 0
                else fsck_result.stderr
            ),
        }

    def get_repository_stats(self, repo_path: Path) -> Dict[str, Any]:
        """Get repository statistics via Git commands."""
        info: Dict[str, Any] = {}

        try:
            # Get commit count
            count_cmd = ["git", "-C", str(repo_path), "rev-list", "--all", "--count"]
            count_result = subprocess.run(
                count_cmd, capture_output=True, text=True, timeout=30
            )
            if count_result.returncode == 0:
                info["commit_count"] = int(count_result.stdout.strip())

            # Get branch count
            branch_cmd = ["git", "-C", str(repo_path), "branch", "-r"]
            branch_result = subprocess.run(
                branch_cmd, capture_output=True, text=True, timeout=30
            )
            if branch_result.returncode == 0:
                branches = branch_result.stdout.strip()
                info["branch_count"] = len(branches.split("\n")) if branches else 0

            # Get tag count
            tag_cmd = ["git", "-C", str(repo_path), "tag"]
            tag_result = subprocess.run(
                tag_cmd, capture_output=True, text=True, timeout=30
            )
            if tag_result.returncode == 0:
                tags = tag_result.stdout.strip()
                info["tag_count"] = len(tags.split("\n")) if tags else 0

        except Exception as e:
            info["info_error"] = str(e)

        return info

    def _prepare_authenticated_url(self, repo_url: str) -> str:
        """Prepare repository URL with authentication if token provided."""
        if not self._auth_token:
            return repo_url

        # Handle GitHub URLs
        if "github.com" in repo_url:
            if repo_url.startswith("https://"):
                return repo_url.replace("https://", f"https://{self._auth_token}@")
            elif repo_url.startswith("git@"):
                # Convert SSH to HTTPS with token
                repo_path = repo_url.replace("git@github.com:", "")
                return f"https://{self._auth_token}@github.com/{repo_path}"

        return repo_url

    def _get_mirror_info(self, mirror_path: Path) -> Dict[str, Any]:
        """Get mirror repository information."""
        return self.get_repository_stats(mirror_path)

    def get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                try:
                    total_size += filepath.stat().st_size
                except (OSError, FileNotFoundError):
                    continue
        return total_size
