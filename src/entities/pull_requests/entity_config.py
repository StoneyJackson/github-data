"""Pull requests entity configuration for EntityRegistry."""

from typing import Union, Set


class PullRequestsEntityConfig:
    """Configuration for pull_requests entity.

    Pull requests depend on milestones (can reference milestones).
    Supports selective PR numbers via Set[int].
    """

    name = "pull_requests"
    env_var = "INCLUDE_PULL_REQUESTS"
    default_value = True
    value_type = Union[bool, Set[int]]
    dependencies = ["milestones"]  # PRs can reference milestones
    save_strategy_class = "PullRequestsSaveStrategy"
    restore_strategy_class = "PullRequestsRestoreStrategy"
    storage_filename = None
    description = "Pull requests with milestone references"
