"""Labels entity configuration for EntityRegistry."""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from github_data_core.entities.strategy_context import StrategyContext
    from github_data_tools.entities.labels.save_strategy import LabelsSaveStrategy
    from github_data_tools.entities.labels.restore_strategy import LabelsRestoreStrategy


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
    description = "Repository labels for issue/PR categorization"

    # Service requirements (NEW)
    required_services_save: List[str] = []  # No services needed for save
    required_services_restore = [
        "github_service"
    ]  # Need GitHub API for conflict resolution

    # Converter declarations
    converters = {
        "convert_to_label": {
            "module": "github_data_tools.entities.labels.converters",
            "function": "convert_to_label",
            "target_model": "Label",
        },
    }

    # GitHub API operations
    github_api_operations = {
        "get_repository_labels": {
            "boundary_method": "get_repository_labels",
            "converter": "convert_to_label",
        },
        "create_label": {
            "boundary_method": "create_label",
        },
        "update_label": {
            "boundary_method": "update_label",
        },
        "delete_label": {
            "boundary_method": "delete_label",
        },
    }

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["LabelsSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            LabelsSaveStrategy instance
        """
        from github_data_tools.entities.labels.save_strategy import LabelsSaveStrategy

        return LabelsSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["LabelsRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            LabelsRestoreStrategy instance

        Note:
            Conflict strategy resolution handled internally with github_service
        """
        from github_data_tools.entities.labels.restore_strategy import (
            LabelsRestoreStrategy,
            create_conflict_strategy,
        )
        from github_data_tools.entities.labels.conflict_strategies import (
            LabelConflictStrategy,
        )

        # Access conflict_strategy from context if available
        conflict_strategy = getattr(context, "_conflict_strategy", None)
        if conflict_strategy is None:
            conflict_strategy = LabelConflictStrategy.SKIP

        # Convert enum to strategy object if needed
        if isinstance(conflict_strategy, LabelConflictStrategy):
            # Get github_service from context for conflict resolution
            github_service = context.github_service
            conflict_strategy_obj = create_conflict_strategy(
                conflict_strategy.value, github_service
            )
        else:
            # Assume it's already a strategy object
            conflict_strategy_obj = conflict_strategy

        return LabelsRestoreStrategy(conflict_strategy_obj)
