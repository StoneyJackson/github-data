"""PR reviews restore strategy implementation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
from urllib.parse import urlparse

from ..strategy import RestoreEntityStrategy
from src.entities.pr_reviews.models import PullRequestReview

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class PullRequestReviewsRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring GitHub pull request reviews."""

    def __init__(self, include_original_metadata: bool = True):
        self._include_original_metadata = include_original_metadata

    def get_entity_name(self) -> str:
        return "pr_reviews"

    def get_dependencies(self) -> List[str]:
        return ["pull_requests"]  # PR reviews depend on pull requests

    def read(
        self, input_path: str, storage_service: "StorageService"
    ) -> List[PullRequestReview]:
        reviews_file = Path(input_path) / "pr_reviews.json"
        if not reviews_file.exists():
            return []  # Return empty list if file doesn't exist
        reviews = storage_service.read(reviews_file, PullRequestReview)
        # Sort by submission time for chronological order
        return sorted(reviews, key=lambda r: r.submitted_at or "")

    def transform(
        self, review: PullRequestReview, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Get pull request number mapping from context
        pr_mapping = context.get("pull_request_number_mapping", {})
        original_pr_number = self._extract_pr_number_from_url(review.pull_request_url)
        new_pr_number = pr_mapping.get(original_pr_number)

        if new_pr_number is None:
            print(
                f"Warning: Skipping review for unmapped pull request "
                f"#{original_pr_number}"
            )
            return None  # Skip this review

        # Prepare review body
        if self._include_original_metadata:
            from src.github.metadata import add_pr_review_metadata_footer

            review_body = add_pr_review_metadata_footer(review)
        else:
            review_body = review.body or ""

        return {
            "body": review_body,
            "state": review.state,
            "pr_number": new_pr_number,
            "original_pr_number": original_pr_number,
        }

    def write(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        github_service.create_pull_request_review(
            repo_name,
            entity_data["pr_number"],
            entity_data["body"],
            entity_data["state"],
        )
        return {"pr_number": entity_data["pr_number"]}

    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: PullRequestReview,
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        # PR reviews don't need post-creation actions beyond the print statement
        print(f"Created review for pull request #{created_data['pr_number']}")

    def _extract_pr_number_from_url(self, pr_url: str) -> int:
        """Extract pull request number from GitHub pull request URL."""
        try:
            parsed_url = urlparse(pr_url)
            path_parts = parsed_url.path.strip("/").split("/")
            pulls_index = path_parts.index("pull")
            return int(path_parts[pulls_index + 1])
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid pull request URL format: {pr_url}") from e
