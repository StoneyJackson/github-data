"""Pull requests entity configuration for EntityRegistry."""

from typing import Union, Set, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.strategy_context import StrategyContext
    from src.entities.pull_requests.save_strategy import PullRequestsSaveStrategy
    from src.entities.pull_requests.restore_strategy import PullRequestsRestoreStrategy


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
    description = "Pull requests with milestone references"

    # Service requirements
    required_services_save: List[str] = []  # No services needed
    required_services_restore: List[str] = []  # No services needed

    @staticmethod
    def create_save_strategy(context: "StrategyContext") -> Optional["PullRequestsSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            PullRequestsSaveStrategy instance
        """
        from src.entities.pull_requests.save_strategy import PullRequestsSaveStrategy

        return PullRequestsSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["PullRequestsRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            PullRequestsRestoreStrategy instance
        """
        from src.entities.pull_requests.restore_strategy import (
            PullRequestsRestoreStrategy,
            DefaultPullRequestConflictStrategy,
        )

        # Access conflict_strategy from context if available, else use default
        conflict_strategy = getattr(context, "_conflict_strategy", None)
        if conflict_strategy is None:
            conflict_strategy = DefaultPullRequestConflictStrategy()

        # Access include_pull_requests from context if available, else use default
        include_pull_requests = getattr(context, "_include_pull_requests", True)

        return PullRequestsRestoreStrategy(
            conflict_strategy=conflict_strategy,
            include_original_metadata=context.include_original_metadata,
            include_pull_requests=include_pull_requests,
        )
