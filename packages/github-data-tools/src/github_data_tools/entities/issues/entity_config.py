"""Issues entity configuration for EntityRegistry."""

from typing import Union, Set, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from github_data_core.entities.strategy_context import StrategyContext
    from github_data_tools.entities.issues.save_strategy import IssuesSaveStrategy
    from github_data_tools.entities.issues.restore_strategy import IssuesRestoreStrategy


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

    # Converter declarations
    converters = {
        "convert_to_issue": {
            "module": "github_data_tools.entities.issues.converters",
            "function": "convert_to_issue",
            "target_model": "Issue",
        },
    }

    # GitHub API operations
    github_api_operations = {
        "get_repository_issues": {
            "boundary_method": "get_repository_issues",
            "converter": "convert_to_issue",
        },
        "create_issue": {
            "boundary_method": "create_issue",
            "converter": "convert_to_issue",
        },
        "close_issue": {
            "boundary_method": "close_issue",
        },
    }

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
        from github_data_tools.entities.issues.save_strategy import IssuesSaveStrategy

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
        from github_data_tools.entities.issues.restore_strategy import (
            IssuesRestoreStrategy,
        )

        return IssuesRestoreStrategy(
            include_original_metadata=context.include_original_metadata
        )
