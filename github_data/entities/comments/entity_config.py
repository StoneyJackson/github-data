"""Comments entity configuration for EntityRegistry."""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.strategy_context import StrategyContext
    from src.entities.comments.save_strategy import CommentsSaveStrategy
    from src.entities.comments.restore_strategy import CommentsRestoreStrategy


class CommentsEntityConfig:
    """Configuration for comments entity.

    Comments depend on issues (belong to issues).
    """

    name = "comments"
    env_var = "INCLUDE_ISSUE_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["issues"]  # Comments belong to issues
    description = "Issue comments and discussions"

    # Service requirements
    required_services_save: List[str] = []
    required_services_restore: List[str] = []  # No services needed

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["CommentsSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            CommentsSaveStrategy instance
        """
        from src.entities.comments.save_strategy import CommentsSaveStrategy

        return CommentsSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["CommentsRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            CommentsRestoreStrategy instance
        """
        from src.entities.comments.restore_strategy import CommentsRestoreStrategy

        return CommentsRestoreStrategy(
            include_original_metadata=context.include_original_metadata
        )
