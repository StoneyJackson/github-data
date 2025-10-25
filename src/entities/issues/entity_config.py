"""Issues entity configuration for EntityRegistry."""

from typing import Union, Set


class IssuesEntityConfig:
    """Configuration for issues entity.

    Issues depend on milestones (can reference milestones).
    Supports selective issue numbers via Set[int].
    """

    name = "issues"
    env_var = "INCLUDE_ISSUES"
    default_value = True
    value_type = Union[bool, Set[int]]
    dependencies = ["milestones"]  # Issues can reference milestones
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Repository issues with milestone references"
