"""PR review comments restore strategy implementation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
from urllib.parse import urlparse

from src.operations.restore.strategy import RestoreEntityStrategy
from src.entities.pr_review_comments.models import PullRequestReviewComment

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class PullRequestReviewCommentsRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring GitHub pull request review comments."""

    def __init__(self, include_original_metadata: bool = True):
        self._include_original_metadata = include_original_metadata

    def get_entity_name(self) -> str:
        return "pr_review_comments"

    def get_dependencies(self) -> List[str]:
        return ["pr_reviews"]  # PR review comments depend on PR reviews

    def read(
        self, input_path: str, storage_service: "StorageService"
    ) -> List[PullRequestReviewComment]:
        comments_file = Path(input_path) / "pr_review_comments.json"
        if not comments_file.exists():
            return []  # Return empty list if file doesn't exist
        comments = storage_service.read(comments_file, PullRequestReviewComment)
        # Sort by creation time for chronological order
        return sorted(comments, key=lambda c: c.created_at)

    def transform(
        self, comment: PullRequestReviewComment, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Get review ID mapping from context
        review_mapping = context.get("review_id_mapping", {})
        original_review_id = str(comment.review_id)
        new_review_id = review_mapping.get(original_review_id)

        if new_review_id is None:
            print(
                f"Warning: Skipping review comment for unmapped review "
                f"#{original_review_id}"
            )
            return None  # Skip this comment

        # Prepare comment body
        if self._include_original_metadata:
            from src.github.metadata import add_pr_review_comment_metadata_footer

            comment_body = add_pr_review_comment_metadata_footer(comment)
        else:
            comment_body = comment.body

        return {
            "body": comment_body,
            "review_id": new_review_id,
            "original_review_id": original_review_id,
        }

    def write(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        github_service.create_pull_request_review_comment(
            repo_name, entity_data["review_id"], entity_data["body"]
        )
        return {"review_id": entity_data["review_id"]}

    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: PullRequestReviewComment,
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        # PR review comments don't need post-creation actions beyond the print statement
        print(f"Created review comment for review #{created_data['review_id']}")

    def _extract_pr_number_from_url(self, pr_url: str) -> int:
        """Extract pull request number from GitHub pull request URL."""
        try:
            parsed_url = urlparse(pr_url)
            path_parts = parsed_url.path.strip("/").split("/")
            pulls_index = path_parts.index("pull")
            return int(path_parts[pulls_index + 1])
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid pull request URL format: {pr_url}") from e
