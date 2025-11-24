"""Git repository entity configuration for EntityRegistry."""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from github_data_core.entities.strategy_context import StrategyContext
    from git_repo_tools.entities.save_strategy import (
        GitRepositorySaveStrategy,
    )
    from git_repo_tools.entities.restore_strategy import (
        GitRepositoryRestoreStrategy,
    )


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

    # Service requirements (NEW)
    required_services_save = ["git_service"]
    required_services_restore = ["git_service"]

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["GitRepositorySaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            GitRepositorySaveStrategy instance

        Note:
            Validation ensures git_service is available, no None check needed
        """
        from git_repo_tools.entities.save_strategy import (
            GitRepositorySaveStrategy,
        )

        return GitRepositorySaveStrategy(context.git_service)

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["GitRepositoryRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            GitRepositoryRestoreStrategy instance

        Note:
            Validation ensures git_service is available, no None check needed
        """
        from git_repo_tools.entities.restore_strategy import (
            GitRepositoryRestoreStrategy,
        )

        return GitRepositoryRestoreStrategy(context.git_service)
