"""Sub-issues entity configuration for EntityRegistry."""

from typing import Optional, Any


class SubIssuesEntityConfig:
    """Configuration for sub_issues entity.

    Sub-issues depend on issues (hierarchical relationships).
    """

    name = "sub_issues"
    env_var = "INCLUDE_SUB_ISSUES"
    default_value = True
    value_type = bool
    dependencies = ["issues"]  # Sub-issues are hierarchical issues
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Hierarchical sub-issue relationships"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused)

        Returns:
            SubIssuesSaveStrategy instance
        """
        from src.entities.sub_issues.save_strategy import SubIssuesSaveStrategy

        return SubIssuesSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - include_original_metadata: Preserve original metadata (default: True)

        Returns:
            SubIssuesRestoreStrategy instance
        """
        from src.entities.sub_issues.restore_strategy import SubIssuesRestoreStrategy

        include_original_metadata = context.get("include_original_metadata", True)
        return SubIssuesRestoreStrategy(
            include_original_metadata=include_original_metadata
        )
