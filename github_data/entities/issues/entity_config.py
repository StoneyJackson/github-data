"""Issues entity configuration for EntityRegistry."""

from typing import Union, Set, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from github_data.entities.strategy_context import StrategyContext
    from github_data.entities.issues.save_strategy import IssuesSaveStrategy
    from github_data.entities.issues.restore_strategy import IssuesRestoreStrategy


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

    # Service requirements
    required_services_save: List[str] = []  # No services needed
    required_services_restore: List[str] = []  # No services needed

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["IssuesSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            IssuesSaveStrategy instance
        """
        from github_data.entities.issues.save_strategy import IssuesSaveStrategy

        return IssuesSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["IssuesRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            IssuesRestoreStrategy instance
        """
        from github_data.entities.issues.restore_strategy import IssuesRestoreStrategy

        return IssuesRestoreStrategy(
            include_original_metadata=context.include_original_metadata
        )
