"""PR review comments entity configuration for EntityRegistry."""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from github_data.entities.strategy_context import StrategyContext
    from github_data.entities.pr_review_comments.save_strategy import (
        PullRequestReviewCommentsSaveStrategy,
    )
    from github_data.entities.pr_review_comments.restore_strategy import (
        PullRequestReviewCommentsRestoreStrategy,
    )


class PrReviewCommentsEntityConfig:
    """Configuration for pr_review_comments entity.

    PR review comments depend on pr_reviews (inline code comments).
    """

    name = "pr_review_comments"
    env_var = "INCLUDE_PR_REVIEW_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["pr_reviews"]  # Review comments belong to reviews
    description = "Code review inline comments"

    # Service requirements
    required_services_save: List[str] = []  # No services needed
    required_services_restore: List[str] = []  # No services needed

    # Converter declarations
    converters = {
        "convert_to_pr_review_comment": {
            "module": "github_data.entities.pr_review_comments.converters",
            "function": "convert_to_pr_review_comment",
            "target_model": "PullRequestReviewComment",
        },
    }

    # GitHub API operations
    github_api_operations = {
        "get_all_pull_request_review_comments": {
            "boundary_method": "get_all_pull_request_review_comments",
            "converter": "convert_to_pr_review_comment",
        },
    }

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["PullRequestReviewCommentsSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            PullRequestReviewCommentsSaveStrategy instance
        """
        from github_data.entities.pr_review_comments.save_strategy import (
            PullRequestReviewCommentsSaveStrategy,
        )

        return PullRequestReviewCommentsSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["PullRequestReviewCommentsRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            PullRequestReviewCommentsRestoreStrategy instance
        """
        from github_data.entities.pr_review_comments.restore_strategy import (
            PullRequestReviewCommentsRestoreStrategy,
        )

        return PullRequestReviewCommentsRestoreStrategy(
            include_original_metadata=context.include_original_metadata
        )
