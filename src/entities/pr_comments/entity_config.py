"""PR comments entity configuration for EntityRegistry."""

from typing import Optional, Any


class PrCommentsEntityConfig:
    """Configuration for pr_comments entity.

    PR comments depend on pull_requests (conversation comments).
    """

    name = "pr_comments"
    env_var = "INCLUDE_PULL_REQUEST_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["pull_requests"]  # PR comments belong to PRs
    save_strategy_class = "PullRequestCommentsSaveStrategy"
    restore_strategy_class = "PullRequestCommentsRestoreStrategy"
    storage_filename = None
    description = "Pull request conversation comments"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused for pr_comments)

        Returns:
            PullRequestCommentsSaveStrategy instance
        """
        from src.entities.pr_comments.save_strategy import (
            PullRequestCommentsSaveStrategy,
        )

        return PullRequestCommentsSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - conflict_strategy: Strategy for handling conflicts
                  (default: DefaultPRCommentConflictStrategy)
                - include_original_metadata: Preserve original metadata
                  (default: True)

        Returns:
            PullRequestCommentsRestoreStrategy instance
        """
        from src.entities.pr_comments.restore_strategy import (
            PullRequestCommentsRestoreStrategy,
            DefaultPRCommentConflictStrategy,
        )

        conflict_strategy = context.get(
            "conflict_strategy", DefaultPRCommentConflictStrategy()
        )
        include_original_metadata = context.get("include_original_metadata", True)

        return PullRequestCommentsRestoreStrategy(
            conflict_strategy=conflict_strategy,
            include_original_metadata=include_original_metadata,
        )
