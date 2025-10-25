"""PR comments entity configuration for EntityRegistry."""


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
