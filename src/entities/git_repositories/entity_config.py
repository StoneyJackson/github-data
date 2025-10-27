"""Git repository entity configuration for EntityRegistry."""

from typing import Optional, Any


class GitRepositoryEntityConfig:
    """Configuration for git_repository entity.

    Git repository backup has no dependencies and is enabled by default.
    Uses convention-based strategy loading.
    """

    name = "git_repository"
    env_var = "INCLUDE_GIT_REPO"
    default_value = True
    value_type = bool
    dependencies: list = []
    description = "Git repository clone for full backup"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies
                - git_service: GitRepositoryService instance (REQUIRED)

        Returns:
            GitRepositorySaveStrategy instance, or None if git_service not provided
        """
        from src.entities.git_repositories.save_strategy import (
            GitRepositorySaveStrategy,
        )

        git_service = context.get("git_service")
        if git_service is None:
            return None  # Skip when git_service not available
        return GitRepositorySaveStrategy(git_service)

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - git_service: GitRepositoryService instance (REQUIRED)

        Returns:
            GitRepositoryRestoreStrategy instance, or None if git_service not provided
        """
        from src.entities.git_repositories.restore_strategy import (
            GitRepositoryRestoreStrategy,
        )

        git_service = context.get("git_service")
        if git_service is None:
            return None  # Skip when git_service not available
        return GitRepositoryRestoreStrategy(git_service)
