"""Pull request comments restore strategy implementation."""

import logging
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path

from github_data.operations.restore.strategy import (
    RestoreEntityStrategy,
    RestoreConflictStrategy,
)
from github_data.entities.pr_comments.models import PullRequestComment

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from github_data.storage.protocols import StorageService
    from github_data.github.protocols import RepositoryService


class PullRequestCommentsRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring GitHub pull request comments."""

    def __init__(
        self,
        conflict_strategy: RestoreConflictStrategy,
        include_original_metadata: bool = False,
    ):
        self._conflict_strategy = conflict_strategy
        self._include_original_metadata = include_original_metadata

    def get_entity_name(self) -> str:
        return "pr_comments"

    def get_dependencies(self) -> List[str]:
        return ["pull_requests"]  # Comments depend on pull requests existing

    def read(
        self, input_path: str, storage_service: "StorageService"
    ) -> List[PullRequestComment]:
        pr_comments_file = Path(input_path) / "pr_comments.json"
        try:
            return storage_service.read(pr_comments_file, PullRequestComment)
        except FileNotFoundError:
            logger.info(f"PR comments file not found: {pr_comments_file}")
            return []  # Return empty list if file doesn't exist

    def transform(
        self, comment: PullRequestComment, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Get the new PR number from the mapping created during PR restoration
        pr_number_mapping = context.get("pr_number_mapping", {})
        original_pr_number = comment.pull_request_number

        if original_pr_number not in pr_number_mapping:
            logger.warning(
                f"No mapping found for PR #{original_pr_number}, " f"skipping comment"
            )
            return None

        new_pr_number = pr_number_mapping[original_pr_number]

        # Prepare comment body with metadata if requested
        comment_body = self._prepare_comment_body(comment)

        return {
            "body": comment_body,
            "pr_number": new_pr_number,
            "original_pr_number": original_pr_number,
        }

    def write(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        created_comment = github_service.create_pull_request_comment(
            repo_name,
            entity_data["pr_number"],
            entity_data["body"],
        )
        return {"id": created_comment.get("id", "unknown")}

    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: PullRequestComment,
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """No post-creation actions needed for PR comments."""
        pass

    def resolve_conflicts(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entities_to_restore: List[PullRequestComment],
    ) -> List[PullRequestComment]:
        """Resolve conflicts and return entities to create."""
        # For PR comments, we typically don't have conflicts since
        # they're created new
        return self._conflict_strategy.resolve_conflicts([], entities_to_restore)

    def _prepare_comment_body(self, comment: PullRequestComment) -> str:
        """Prepare comment body with optional metadata and sanitization."""
        from github_data.github.metadata import prepare_pr_comment_body_for_restore

        return prepare_pr_comment_body_for_restore(
            comment, include_metadata=self._include_original_metadata
        )


class DefaultPRCommentConflictStrategy(RestoreConflictStrategy):
    """Default strategy for PR comment conflicts."""

    def resolve_conflicts(
        self,
        existing_entities: List[PullRequestComment],
        entities_to_restore: List[PullRequestComment],
    ) -> List[PullRequestComment]:
        """PR comments are always created new, so no conflicts to resolve."""
        return entities_to_restore


def create_conflict_strategy() -> RestoreConflictStrategy:
    """Factory function to create PR comment conflict resolution strategy."""
    return DefaultPRCommentConflictStrategy()
