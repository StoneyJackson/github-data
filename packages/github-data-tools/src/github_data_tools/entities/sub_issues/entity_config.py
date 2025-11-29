"""Sub-issues entity configuration for EntityRegistry."""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from github_data_core.entities.strategy_context import StrategyContext
    from github_data_tools.entities.sub_issues.save_strategy import (
        SubIssuesSaveStrategy,
    )
    from github_data_tools.entities.sub_issues.restore_strategy import (
        SubIssuesRestoreStrategy,
    )


class SubIssuesEntityConfig:
    """Configuration for sub_issues entity.

    Sub-issues depend on issues (hierarchical relationships).
    """

    name = "sub_issues"
    env_var = "INCLUDE_SUB_ISSUES"
    default_value = True
    value_type = bool
    dependencies = ["issues"]  # Sub-issues are hierarchical issues
    description = "Hierarchical sub-issue relationships"

    # Service requirements
    required_services_save: List[str] = []
    required_services_restore: List[str] = []  # No services needed

    # Converter declarations
    converters = {
        "convert_to_sub_issue": {
            "module": "github_data_tools.entities.sub_issues.converters",
            "function": "convert_to_sub_issue",
            "target_model": "SubIssue",
        },
    }

    # GitHub API operations
    github_api_operations = {
        "get_repository_sub_issues": {
            "boundary_method": "get_repository_sub_issues",
            "converter": "convert_to_sub_issue",
        },
        "get_issue_sub_issues": {
            "boundary_method": "get_issue_sub_issues",
        },
        "add_sub_issue": {
            "boundary_method": "add_sub_issue",
        },
        "remove_sub_issue": {
            "boundary_method": "remove_sub_issue",
        },
        "reprioritize_sub_issue": {
            "boundary_method": "reprioritize_sub_issue",
        },
    }

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["SubIssuesSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            SubIssuesSaveStrategy instance
        """
        from github_data_tools.entities.sub_issues.save_strategy import (
            SubIssuesSaveStrategy,
        )

        return SubIssuesSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["SubIssuesRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            SubIssuesRestoreStrategy instance
        """
        from github_data_tools.entities.sub_issues.restore_strategy import (
            SubIssuesRestoreStrategy,
        )

        return SubIssuesRestoreStrategy(
            include_original_metadata=context.include_original_metadata
        )
