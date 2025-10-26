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
    dependencies = []
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Git repository clone for full backup"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies
                - git_service: GitRepositoryService instance (REQUIRED)

        Returns:
            GitRepositorySaveStrategy instance

        Raises:
            ValueError: If git_service not provided
        """
        from src.entities.git_repositories.save_strategy import GitRepositorySaveStrategy

        git_service = context.get('git_service')
        if git_service is None:
            raise ValueError(
                "git_repository save strategy requires 'git_service' in context"
            )
        return GitRepositorySaveStrategy(git_service)

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - git_service: GitRepositoryService instance (REQUIRED)

        Returns:
            GitRepositoryRestoreStrategy instance

        Raises:
            ValueError: If git_service not provided
        """
        from src.entities.git_repositories.restore_strategy import GitRepositoryRestoreStrategy

        git_service = context.get('git_service')
        if git_service is None:
            raise ValueError(
                "git_repository restore strategy requires 'git_service' in context"
            )
        return GitRepositoryRestoreStrategy(git_service)
