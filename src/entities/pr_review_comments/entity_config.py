"""PR review comments entity configuration for EntityRegistry."""


class PrReviewCommentsEntityConfig:
    """Configuration for pr_review_comments entity.

    PR review comments depend on pr_reviews (inline code comments).
    """

    name = "pr_review_comments"
    env_var = "INCLUDE_PR_REVIEW_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["pr_reviews"]  # Review comments belong to reviews
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Code review inline comments"
