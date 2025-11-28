"""Git repository entity configuration for EntityRegistry."""

from typing import Optional, List, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from github_data_core.entities.strategy_context import StrategyContext
    from github_data_core.entities.base import BaseSaveStrategy, BaseRestoreStrategy


class GitRepositoryEntityConfig:
    """Configuration for git_repository entity.

    Git repository backup has no dependencies and is enabled by default.
    Uses convention-based strategy loading.
    """

    name = "git_repository"
    env_var = "INCLUDE_GIT_REPO"
    default_value = True
    value_type = bool
    dependencies: List[str] = []
    description = "Git repository clone for full backup"

    # Service requirements (NEW)
    required_services_save: List[str] = ["git_service"]
    required_services_restore: List[str] = ["git_service"]

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["BaseSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            GitRepositorySaveStrategy instance

        Note:
            Validation ensures git_service is available, no None check needed
        """
        from git_repo_tools.entities.git_repositories.save_strategy import (
            GitRepositorySaveStrategy,
        )

        return cast("BaseSaveStrategy", GitRepositorySaveStrategy(context.git_service))

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["BaseRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            GitRepositoryRestoreStrategy instance

        Note:
            Validation ensures git_service is available, no None check needed
        """
        from git_repo_tools.entities.git_repositories.restore_strategy import (
            GitRepositoryRestoreStrategy,
        )

        return cast(
            "BaseRestoreStrategy", GitRepositoryRestoreStrategy(context.git_service)
        )
