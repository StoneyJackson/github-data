"""Comments entity configuration for EntityRegistry."""


class CommentsEntityConfig:
    """Configuration for comments entity.

    Comments depend on issues (belong to issues).
    """

    name = "comments"
    env_var = "INCLUDE_ISSUE_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["issues"]  # Comments belong to issues
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Issue comments and discussions"
