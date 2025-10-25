"""Sub-issues entity configuration for EntityRegistry."""


class SubIssuesEntityConfig:
    """Configuration for sub_issues entity.

    Sub-issues depend on issues (hierarchical relationships).
    """

    name = "sub_issues"
    env_var = "INCLUDE_SUB_ISSUES"
    default_value = True
    value_type = bool
    dependencies = ["issues"]  # Sub-issues are hierarchical issues
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Hierarchical sub-issue relationships"
