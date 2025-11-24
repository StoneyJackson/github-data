"""Git repository save strategy."""

import time
from pathlib import Path
from typing import List, Dict, Any, TYPE_CHECKING
from github_data.operations.save.strategy import SaveEntityStrategy  # TODO: Will move to github-data-tools
from git_repo_tools.git.protocols import GitRepositoryService
from git_repo_tools.entities.models import GitBackupFormat

if TYPE_CHECKING:
    from github_data_core.storage.protocols import StorageService
    from github_data.github.protocols import RepositoryService  # TODO: Will be split between packages


class GitRepositorySaveStrategy(SaveEntityStrategy):
    """Strategy for saving Git repository data."""

    def __init__(
        self,
        git_service: GitRepositoryService,
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR,
    ):
        self._git_service = git_service
        self._backup_format = backup_format

    def get_entity_name(self) -> str:
        """Return entity name for this strategy."""
        return "git_repository"

    def get_dependencies(self) -> List[str]:
        """Return list of entity dependencies."""
        return []  # Git repository has no dependencies

    def read(
        self, github_service: "RepositoryService", repo_name: str
    ) -> List[Dict[str, Any]]:
        """Read Git repository data."""
        # For Git repositories, we don't collect data through GitHub API
        # Instead, we prepare repository URL
        repo_url = f"https://github.com/{repo_name}.git"

        return [
            {
                "repo_name": repo_name,
                "repo_url": repo_url,
                "backup_format": self._backup_format.value,
            }
        ]

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        # Git repository strategy doesn't use standard converter pattern
        raise NotImplementedError(
            "Git repository strategy uses custom collection pattern"
        )

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        # Git repository strategy doesn't use standard service method pattern
        raise NotImplementedError(
            "Git repository strategy uses custom collection pattern"
        )

    def transform(
        self, entities: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process Git repository data."""
        # No processing needed for Git repositories
        return entities

    def write(
        self,
        entities: List[Dict[str, Any]],
        output_path: str,
        storage_service: "StorageService",
    ) -> Dict[str, Any]:
        """Save Git repository data."""
        start_time = time.time()

        if not entities:
            return {
                "saved_repositories": 0,
                "total_repositories": 0,
                "duration_seconds": time.time() - start_time,
            }

        results = []

        for entity in entities:
            repo_name = entity["repo_name"]
            repo_url = entity["repo_url"]

            # Create Git repository directory using simple filesystem operations
            git_repo_dir = Path(output_path) / "git-repo"
            git_repo_dir.mkdir(parents=True, exist_ok=True)

            # Determine backup destination - flatten directly to git-repo
            # (mirror format only)
            backup_path = git_repo_dir

            # Perform Git backup
            result = self._git_service.clone_repository(
                repo_url, backup_path, self._backup_format
            )

            results.append(
                {
                    "repo_name": repo_name,
                    "backup_path": str(backup_path),
                    "success": result.success,
                    "error": result.error,
                    "size_bytes": result.size_bytes,
                    "backup_format": result.backup_format,
                }
            )

        successful_backups = sum(1 for r in results if r.get("success", False))
        duration = time.time() - start_time

        return {
            "saved_repositories": successful_backups,
            "total_repositories": len(entities),
            "results": results,
            "duration_seconds": duration,
        }
