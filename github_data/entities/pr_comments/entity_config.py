"""PR comments entity configuration for EntityRegistry."""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from github_data.entities.strategy_context import StrategyContext
    from github_data.entities.pr_comments.save_strategy import (
        PullRequestCommentsSaveStrategy,
    )
    from github_data.entities.pr_comments.restore_strategy import (
        PullRequestCommentsRestoreStrategy,
    )


class PrCommentsEntityConfig:
    """Configuration for pr_comments entity.

    PR comments depend on pull_requests (conversation comments).
    """

    name = "pr_comments"
    env_var = "INCLUDE_PULL_REQUEST_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["pull_requests"]  # PR comments belong to PRs
    description = "Pull request conversation comments"

    # Service requirements
    required_services_save: List[str] = []  # No services needed
    required_services_restore: List[str] = []  # No services needed

    # Converter declarations
    converters = {
        "convert_to_pr_comment": {
            "module": "github_data.entities.pr_comments.converters",
            "function": "convert_to_pr_comment",
            "target_model": "PullRequestComment",
        },
    }

    # GitHub API operations
    github_api_operations = {
        "get_all_pull_request_comments": {
            "boundary_method": "get_all_pull_request_comments",
            "converter": "convert_to_pr_comment",
        },
    }

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["PullRequestCommentsSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            PullRequestCommentsSaveStrategy instance
        """
        from github_data.entities.pr_comments.save_strategy import (
            PullRequestCommentsSaveStrategy,
        )

        return PullRequestCommentsSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["PullRequestCommentsRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            PullRequestCommentsRestoreStrategy instance
        """
        from github_data.entities.pr_comments.restore_strategy import (
            PullRequestCommentsRestoreStrategy,
            DefaultPRCommentConflictStrategy,
        )

        # Access conflict_strategy from context if available, else use default
        conflict_strategy = getattr(context, "_conflict_strategy", None)
        if conflict_strategy is None:
            conflict_strategy = DefaultPRCommentConflictStrategy()

        return PullRequestCommentsRestoreStrategy(
            conflict_strategy=conflict_strategy,
            include_original_metadata=context.include_original_metadata,
        )
