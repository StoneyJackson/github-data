"""Comments entity configuration for EntityRegistry."""

from typing import Optional, Any


class CommentsEntityConfig:
    """Configuration for comments entity.

    Comments depend on issues (belong to issues).
    """

    name = "comments"
    env_var = "INCLUDE_ISSUE_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["issues"]  # Comments belong to issues
    storage_filename = None
    description = "Issue comments and discussions"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused for comments)

        Returns:
            CommentsSaveStrategy instance
        """
        from src.entities.comments.save_strategy import CommentsSaveStrategy

        return CommentsSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - include_original_metadata: Preserve original metadata (default: True)

        Returns:
            CommentsRestoreStrategy instance
        """
        from src.entities.comments.restore_strategy import CommentsRestoreStrategy

        include_original_metadata = context.get("include_original_metadata", True)
        return CommentsRestoreStrategy(
            include_original_metadata=include_original_metadata
        )
