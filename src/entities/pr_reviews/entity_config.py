"""PR reviews entity configuration for EntityRegistry."""


class PrReviewsEntityConfig:
    """Configuration for pr_reviews entity.

    PR reviews depend on pull_requests (belong to PRs).
    """

    name = "pr_reviews"
    env_var = "INCLUDE_PR_REVIEWS"
    default_value = True
    value_type = bool
    dependencies = ["pull_requests"]  # Reviews belong to PRs
    save_strategy_class = "PullRequestReviewsSaveStrategy"
    restore_strategy_class = "PullRequestReviewsRestoreStrategy"
    storage_filename = None
    description = "Pull request code reviews"
