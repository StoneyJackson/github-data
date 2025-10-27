"""PR review comments entity configuration for EntityRegistry."""

from typing import Optional, Any


class PrReviewCommentsEntityConfig:
    """Configuration for pr_review_comments entity.

    PR review comments depend on pr_reviews (inline code comments).
    """

    name = "pr_review_comments"
    env_var = "INCLUDE_PR_REVIEW_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["pr_reviews"]  # Review comments belong to reviews
    storage_filename = None
    description = "Code review inline comments"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused for pr_review_comments)

        Returns:
            PullRequestReviewCommentsSaveStrategy instance
        """
        from src.entities.pr_review_comments.save_strategy import (
            PullRequestReviewCommentsSaveStrategy,
        )

        return PullRequestReviewCommentsSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - include_original_metadata: Preserve original metadata (default: True)

        Returns:
            PullRequestReviewCommentsRestoreStrategy instance
        """
        from src.entities.pr_review_comments.restore_strategy import (
            PullRequestReviewCommentsRestoreStrategy,
        )

        include_original_metadata = context.get("include_original_metadata", True)
        return PullRequestReviewCommentsRestoreStrategy(
            include_original_metadata=include_original_metadata
        )
