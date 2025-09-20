"""Pull requests restore strategy implementation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path

from ..strategy import (
    RestoreEntityStrategy,
    RestoreConflictStrategy,
)
from src.entities.pull_requests.models import PullRequest

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class PullRequestsRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring GitHub pull requests."""

    def __init__(
        self,
        conflict_strategy: RestoreConflictStrategy,
        include_original_metadata: bool = False,
    ):
        self._conflict_strategy = conflict_strategy
        self._include_original_metadata = include_original_metadata

    def get_entity_name(self) -> str:
        return "pull_requests"

    def get_dependencies(self) -> List[str]:
        return ["labels"]  # Pull requests may reference labels

    def load_data(
        self, input_path: str, storage_service: "StorageService"
    ) -> List[PullRequest]:
        pull_requests_file = Path(input_path) / "pull_requests.json"
        return storage_service.load_data(pull_requests_file, PullRequest)

    def transform_for_creation(
        self, pull_request: PullRequest, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Prepare PR body with metadata if requested
        pr_body = self._prepare_pr_body(pull_request)
        return {
            "title": pull_request.title,
            "body": pr_body,
            "head_ref": pull_request.head_ref,
            "base_ref": pull_request.base_ref,
            "original_number": pull_request.number,
            "original_state": pull_request.state,
        }

    def create_entity(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        created_pr = github_service.create_pull_request(
            repo_name,
            entity_data["title"],
            entity_data["body"],
            entity_data["head_ref"],
            entity_data["base_ref"],
        )
        return {
            "number": created_pr["number"],
            "original_number": entity_data["original_number"],
            "original_state": entity_data["original_state"],
        }

    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: PullRequest,
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """Handle PR state changes after creation."""
        pr_number = created_data["number"]
        original_state = created_data["original_state"]
        # Store PR number mapping for comments
        if "pr_number_mapping" not in context:
            context["pr_number_mapping"] = {}
        context["pr_number_mapping"][created_data["original_number"]] = pr_number

        # Handle closed/merged state
        if original_state in ["closed", "merged"]:
            self._handle_pr_state(github_service, repo_name, pr_number, original_state)

    def resolve_conflicts(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entities_to_restore: List[PullRequest],
    ) -> List[PullRequest]:
        """Resolve conflicts and return entities to create."""
        # For pull requests, we typically don't have conflicts since
        # they're created new. But we can still apply the conflict
        # strategy for consistency
        return self._conflict_strategy.resolve_conflicts([], entities_to_restore)

    def _prepare_pr_body(self, pr: PullRequest) -> str:
        """Prepare pull request body with optional metadata."""
        if self._include_original_metadata:
            from src.github.metadata import add_pr_metadata_footer

            return add_pr_metadata_footer(pr)
        return pr.body or ""

    def _handle_pr_state(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        pr_number: int,
        original_state: str,
    ) -> None:
        """Handle pull request state restoration."""
        try:
            if original_state == "closed":
                # Note: close_pull_request method not available in
                # RepositoryService protocol
                print(f"Warning: Cannot restore closed state for PR #{pr_number}")
            elif original_state == "merged":
                # Note: Cannot actually merge PRs via API after creation
                print(f"Warning: Cannot restore merged state for PR #{pr_number}")
        except Exception as e:
            print(f"Warning: Failed to set PR #{pr_number} state: {e}")


class DefaultPullRequestConflictStrategy(RestoreConflictStrategy):
    """Default strategy for pull request conflicts."""

    def resolve_conflicts(
        self,
        existing_entities: List[PullRequest],
        entities_to_restore: List[PullRequest],
    ) -> List[PullRequest]:
        """Pull requests are always created new, so no conflicts to resolve."""
        return entities_to_restore


def create_conflict_strategy() -> RestoreConflictStrategy:
    """Factory function to create pull request conflict resolution strategy."""
    return DefaultPullRequestConflictStrategy()
