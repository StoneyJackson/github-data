"""Milestones entity configuration for EntityRegistry."""

from typing import Optional, Any


class MilestonesEntityConfig:
    """Configuration for milestones entity.

    Milestones have no dependencies and are enabled by default.
    Uses convention-based strategy loading.
    """

    name = "milestones"
    env_var = "INCLUDE_MILESTONES"
    default_value = True
    value_type = bool
    dependencies = []
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Project milestones for issue/PR organization"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused for milestones)

        Returns:
            MilestonesSaveStrategy instance
        """
        from src.entities.milestones.save_strategy import MilestonesSaveStrategy
        return MilestonesSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies (unused for milestones)

        Returns:
            MilestonesRestoreStrategy instance
        """
        from src.entities.milestones.restore_strategy import MilestonesRestoreStrategy
        return MilestonesRestoreStrategy()
