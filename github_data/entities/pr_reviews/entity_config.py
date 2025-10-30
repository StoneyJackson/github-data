"""PR reviews entity configuration for EntityRegistry."""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from github_data.entities.strategy_context import StrategyContext
    from github_data.entities.pr_reviews.save_strategy import PullRequestReviewsSaveStrategy
    from github_data.entities.pr_reviews.restore_strategy import (
        PullRequestReviewsRestoreStrategy,
    )


class PrReviewsEntityConfig:
    """Configuration for pr_reviews entity.

    PR reviews depend on pull_requests (belong to PRs).
    """

    name = "pr_reviews"
    env_var = "INCLUDE_PR_REVIEWS"
    default_value = True
    value_type = bool
    dependencies = ["pull_requests"]  # Reviews belong to PRs
    description = "Pull request code reviews"

    # Service requirements
    required_services_save: List[str] = []  # No services needed
    required_services_restore: List[str] = []  # No services needed

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["PullRequestReviewsSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            PullRequestReviewsSaveStrategy instance
        """
        from github_data.entities.pr_reviews.save_strategy import PullRequestReviewsSaveStrategy

        return PullRequestReviewsSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["PullRequestReviewsRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            PullRequestReviewsRestoreStrategy instance
        """
        from github_data.entities.pr_reviews.restore_strategy import (
            PullRequestReviewsRestoreStrategy,
        )

        return PullRequestReviewsRestoreStrategy(
            include_original_metadata=context.include_original_metadata
        )
