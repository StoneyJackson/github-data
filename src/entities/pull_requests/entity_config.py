"""Pull requests entity configuration for EntityRegistry."""

from typing import Union, Set, Optional, Any


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

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused for pull_requests)

        Returns:
            PullRequestsSaveStrategy instance
        """
        from src.entities.pull_requests.save_strategy import PullRequestsSaveStrategy

        return PullRequestsSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - conflict_strategy: Strategy for handling conflicts (default: DefaultPullRequestConflictStrategy)
                - include_original_metadata: Preserve original metadata (default: True)
                - include_pull_requests: Boolean or Set[int] for selective filtering (default: True)

        Returns:
            PullRequestsRestoreStrategy instance
        """
        from src.entities.pull_requests.restore_strategy import (
            PullRequestsRestoreStrategy,
            DefaultPullRequestConflictStrategy,
        )

        conflict_strategy = context.get(
            "conflict_strategy", DefaultPullRequestConflictStrategy()
        )
        include_original_metadata = context.get("include_original_metadata", True)
        include_pull_requests = context.get("include_pull_requests", True)

        return PullRequestsRestoreStrategy(
            conflict_strategy=conflict_strategy,
            include_original_metadata=include_original_metadata,
            include_pull_requests=include_pull_requests,
        )
