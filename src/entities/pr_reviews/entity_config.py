"""PR reviews entity configuration for EntityRegistry."""

from typing import Optional, Any


class PrReviewsEntityConfig:
    """Configuration for pr_reviews entity.

    PR reviews depend on pull_requests (belong to PRs).
    """

    name = "pr_reviews"
    env_var = "INCLUDE_PR_REVIEWS"
    default_value = True
    value_type = bool
    dependencies = ["pull_requests"]  # Reviews belong to PRs
    storage_filename = None
    description = "Pull request code reviews"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused for pr_reviews)

        Returns:
            PullRequestReviewsSaveStrategy instance
        """
        from src.entities.pr_reviews.save_strategy import PullRequestReviewsSaveStrategy

        return PullRequestReviewsSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - include_original_metadata: Preserve original metadata (default: True)

        Returns:
            PullRequestReviewsRestoreStrategy instance
        """
        from src.entities.pr_reviews.restore_strategy import (
            PullRequestReviewsRestoreStrategy,
        )

        include_original_metadata = context.get("include_original_metadata", True)
        return PullRequestReviewsRestoreStrategy(
            include_original_metadata=include_original_metadata
        )
