"""Labels entity configuration for EntityRegistry."""

from typing import Optional, Any, List


class LabelsEntityConfig:
    """Configuration for labels entity.

    Labels have no dependencies and are enabled by default.
    Uses convention-based strategy loading.
    """

    name = "labels"
    env_var = "INCLUDE_LABELS"
    default_value = True
    value_type = bool
    dependencies: List[str] = []
    save_strategy_class = None  # Use convention
    restore_strategy_class = None  # Use convention
    storage_filename = None  # Use convention (labels.json)
    description = "Repository labels for issue/PR categorization"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused)

        Returns:
            LabelsSaveStrategy instance
        """
        from src.entities.labels.save_strategy import LabelsSaveStrategy
        return LabelsSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - conflict_strategy: How to handle label conflicts (default: SKIP)

        Returns:
            LabelsRestoreStrategy instance
        """
        from src.entities.labels.restore_strategy import LabelsRestoreStrategy, create_conflict_strategy
        from src.entities.labels.conflict_strategies import LabelConflictStrategy

        conflict_strategy = context.get('conflict_strategy', LabelConflictStrategy.SKIP)

        # Convert enum to strategy object if needed
        if isinstance(conflict_strategy, LabelConflictStrategy):
            # Convert enum to strategy object
            github_service = context.get('github_service')
            conflict_strategy_obj = create_conflict_strategy(conflict_strategy.value, github_service)
        else:
            # Assume it's already a strategy object
            conflict_strategy_obj = conflict_strategy

        return LabelsRestoreStrategy(conflict_strategy_obj)
