"""Issues entity configuration for EntityRegistry."""

from typing import Union, Set, Optional, Any


class IssuesEntityConfig:
    """Configuration for issues entity.

    Issues depend on milestones (can reference milestones).
    Supports selective issue numbers via Set[int].
    """

    name = "issues"
    env_var = "INCLUDE_ISSUES"
    default_value = True
    value_type = Union[bool, Set[int]]
    dependencies = ["milestones"]  # Issues can reference milestones
    description = "Repository issues with milestone references"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused)

        Returns:
            IssuesSaveStrategy instance
        """
        from src.entities.issues.save_strategy import IssuesSaveStrategy

        return IssuesSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - include_original_metadata: Preserve original metadata (default: True)

        Returns:
            IssuesRestoreStrategy instance
        """
        from src.entities.issues.restore_strategy import IssuesRestoreStrategy

        include_original_metadata = context.get("include_original_metadata", True)
        return IssuesRestoreStrategy(
            include_original_metadata=include_original_metadata
        )
