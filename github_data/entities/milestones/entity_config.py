"""Milestones entity configuration for EntityRegistry."""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from github_data.entities.strategy_context import StrategyContext
    from github_data.entities.milestones.save_strategy import MilestonesSaveStrategy
    from github_data.entities.milestones.restore_strategy import (
        MilestonesRestoreStrategy,
    )


class MilestonesEntityConfig:
    """Configuration for milestones entity.

    Milestones have no dependencies and are enabled by default.
    Uses convention-based strategy loading.
    """

    name = "milestones"
    env_var = "INCLUDE_MILESTONES"
    default_value = True
    value_type = bool
    dependencies: List[str] = []
    description = "Project milestones for issue/PR organization"

    # Service requirements
    required_services_save: List[str] = []
    required_services_restore: List[str] = []  # No services needed

    # GitHub API operations
    github_api_operations = {
        "get_repository_milestones": {
            "boundary_method": "get_repository_milestones",
            "converter": "convert_to_milestone",
        },
        "create_milestone": {
            "boundary_method": "create_milestone",
            "converter": "convert_to_milestone",
        },
    }

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["MilestonesSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            MilestonesSaveStrategy instance
        """
        from github_data.entities.milestones.save_strategy import MilestonesSaveStrategy

        return MilestonesSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["MilestonesRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            MilestonesRestoreStrategy instance
        """
        from github_data.entities.milestones.restore_strategy import (
            MilestonesRestoreStrategy,
        )

        return MilestonesRestoreStrategy()
