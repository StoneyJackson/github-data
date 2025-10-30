"""Git repository restore strategy."""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from github_data.operations.restore.strategy import RestoreEntityStrategy
from github_data.git.protocols import GitRepositoryService
from github_data.entities.git_repositories.models import GitBackupFormat

if TYPE_CHECKING:
    from github_data.storage.protocols import StorageService
    from github_data.github.protocols import RepositoryService


class GitRepositoryRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring Git repository data."""

    def __init__(self, git_service: GitRepositoryService):
        self._git_service = git_service

    def get_entity_name(self) -> str:
        """Return entity name for this strategy."""
        return "git_repository"

    def get_dependencies(self) -> List[str]:
        """Return list of entity dependencies."""
        return []  # Git repository has no dependencies

    def read(
        self, input_path: str, storage_service: "StorageService"
    ) -> List[Dict[str, Any]]:
        """Load Git repository backup data."""
        git_repo_dir = Path(input_path) / "git-repo"

        if not git_repo_dir.exists():
            return []

        repositories = []

        # Check if git-repo contains a Git repository (mirror format only)
        if (git_repo_dir / ".git").exists():
            # Direct git repository in git-repo directory
            repositories.append(
                {
                    "backup_path": str(git_repo_dir),
                    "backup_format": GitBackupFormat.MIRROR.value,
                    "repo_name": "repository",  # Generic name for flattened structure
                }
            )

        return repositories

    def transform(
        self, entity: Dict[str, Any], context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Transform entity for GitHub API creation."""
        # Git repositories don't need transformation for GitHub API creation
        # They are restored directly to filesystem
        return entity

    def write(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create entity via GitHub API."""
        # Git repositories don't create GitHub API entities
        # The restoration happens directly to filesystem
        # Return the entity data as-is for processing in restore_data
        return entity_data

    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: Dict[str, Any],
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """Post-creation actions."""
        # No post-creation actions needed for Git repositories
        pass

    def resolve_conflicts(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entities_to_restore: List[Any],
    ) -> List[Any]:
        """Resolve conflicts between existing and restored entities."""
        # Git repository restore doesn't have conflicts in the same way
        # It's a filesystem operation
        return entities_to_restore

    def restore_data(
        self, entities: List[Dict[str, Any]], destination_path: str
    ) -> Dict[str, Any]:
        """Restore Git repository data."""
        start_time = time.time()

        if not entities:
            return {
                "restored_repositories": 0,
                "total_repositories": 0,
                "duration_seconds": time.time() - start_time,
            }

        results = []

        for entity in entities:
            backup_path = Path(entity["backup_path"])
            repo_name = entity["repo_name"]
            backup_format = GitBackupFormat(entity["backup_format"])

            # Create restore destination
            restore_path = (
                Path(destination_path)
                / "restored-repositories"
                / repo_name.replace("/", "_")
            )

            # Perform Git restore
            result = self._git_service.restore_repository(
                backup_path, restore_path, backup_format
            )

            results.append(
                {
                    "repo_name": repo_name,
                    "restore_path": str(restore_path),
                    "success": result.success,
                    "error": result.error,
                    "size_bytes": result.size_bytes,
                    "backup_format": result.backup_format,
                }
            )

        successful_restores = sum(1 for r in results if r.get("success", False))
        duration = time.time() - start_time

        return {
            "restored_repositories": successful_restores,
            "total_repositories": len(entities),
            "results": results,
            "duration_seconds": duration,
        }
