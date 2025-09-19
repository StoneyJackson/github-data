"""Comments restore strategy implementation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
from urllib.parse import urlparse

from ...operations.restore.strategy import RestoreEntityStrategy
from .models import Comment

if TYPE_CHECKING:
    from ...storage.protocols import StorageService
    from ...github.protocols import RepositoryService


class CommentsRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring GitHub issue comments."""

    def __init__(self, include_original_metadata: bool = True):
        self._include_original_metadata = include_original_metadata

    def get_entity_name(self) -> str:
        return "comments"

    def get_dependencies(self) -> List[str]:
        return ["issues"]  # Comments depend on issues

    def load_data(
        self, input_path: str, storage_service: "StorageService"
    ) -> List[Comment]:
        comments_file = Path(input_path) / "comments.json"
        comments = storage_service.load_data(comments_file, Comment)
        # Sort by creation time for chronological order
        return sorted(comments, key=lambda c: c.created_at)

    def transform_for_creation(
        self, comment: Comment, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Get issue number mapping from context
        issue_mapping = context.get("issue_number_mapping", {})
        original_issue_number = self._extract_issue_number_from_url(comment.issue_url)
        new_issue_number = issue_mapping.get(original_issue_number)

        if new_issue_number is None:
            print(
                f"Warning: Skipping comment for unmapped issue "
                f"#{original_issue_number}"
            )
            return None  # Skip this comment

        # Prepare comment body
        if self._include_original_metadata:
            from ...github.metadata import add_comment_metadata_footer

            comment_body = add_comment_metadata_footer(comment)
        else:
            comment_body = comment.body

        return {
            "body": comment_body,
            "issue_number": new_issue_number,
            "original_issue_number": original_issue_number,
        }

    def create_entity(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        github_service.create_issue_comment(
            repo_name, entity_data["issue_number"], entity_data["body"]
        )
        return {"issue_number": entity_data["issue_number"]}

    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: Comment,
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        # Comments don't need post-creation actions beyond the print statement
        print(f"Created comment for issue #{created_data['issue_number']}")

    def _extract_issue_number_from_url(self, issue_url: str) -> int:
        """Extract issue number from GitHub issue URL."""
        try:
            parsed_url = urlparse(issue_url)
            path_parts = parsed_url.path.strip("/").split("/")
            issues_index = path_parts.index("issues")
            return int(path_parts[issues_index + 1])
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid issue URL format: {issue_url}") from e
