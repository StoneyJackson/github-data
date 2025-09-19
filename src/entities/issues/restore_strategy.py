"""Issues restore strategy implementation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path

from ...strategies.restore_strategy import RestoreEntityStrategy
from .models import Issue

if TYPE_CHECKING:
    from ...storage.protocols import StorageService
    from ...github.protocols import RepositoryService


class IssuesRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring GitHub issues."""

    def __init__(self, include_original_metadata: bool = True):
        self._include_original_metadata = include_original_metadata

    def get_entity_name(self) -> str:
        return "issues"

    def get_dependencies(self) -> List[str]:
        return ["labels"]  # Issues depend on labels

    def load_data(
        self, input_path: str, storage_service: "StorageService"
    ) -> List[Issue]:
        issues_file = Path(input_path) / "issues.json"
        return storage_service.load_data(issues_file, Issue)

    def transform_for_creation(
        self, issue: Issue, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Prepare issue body with metadata if needed
        if self._include_original_metadata:
            from ..github.metadata import add_issue_metadata_footer

            issue_body = add_issue_metadata_footer(issue)
        else:
            issue_body = issue.body or ""

        # Convert label objects to names
        label_names = [label.name for label in issue.labels]

        return {
            "title": issue.title,
            "body": issue_body,
            "labels": label_names,
            "original_number": issue.number,
            "original_state": issue.state,
            "state_reason": issue.state_reason,
        }

    def create_entity(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        created_issue = github_service.create_issue(
            repo_name, entity_data["title"], entity_data["body"], entity_data["labels"]
        )
        return {
            "number": created_issue["number"],
            "original_number": entity_data["original_number"],
            "original_state": entity_data["original_state"],
            "state_reason": entity_data.get("state_reason"),
        }

    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: Issue,
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        # Close issue if it was originally closed
        if created_data["original_state"] == "closed":
            try:
                github_service.close_issue(
                    repo_name, created_data["number"], created_data.get("state_reason")
                )
                reason_text = (
                    f"with reason: {created_data['state_reason']}"
                    if created_data.get("state_reason")
                    else ""
                )
                print(f"Closed issue #{created_data['number']} {reason_text}")
            except Exception as e:
                print(
                    f"Warning: Failed to close issue " f"#{created_data['number']}: {e}"
                )

        # Store number mapping for dependent entities
        if "issue_number_mapping" not in context:
            context["issue_number_mapping"] = {}
        context["issue_number_mapping"][created_data["original_number"]] = created_data[
            "number"
        ]

        print(
            f"Created issue #{created_data['number']}: "
            f"{entity.title} (was #{created_data['original_number']})"
        )
