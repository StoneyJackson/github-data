"""Sub-issues restore strategy implementation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path

from ..strategy import RestoreEntityStrategy
from src.entities.sub_issues.models import SubIssue

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class SubIssuesRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring GitHub sub-issue relationships."""

    def __init__(self, include_original_metadata: bool = True):
        self._include_original_metadata = include_original_metadata

    def get_entity_name(self) -> str:
        return "sub_issues"

    def get_dependencies(self) -> List[str]:
        return ["issues"]  # Sub-issues depend on issues

    def read(
        self, input_path: str, storage_service: "StorageService"
    ) -> List[SubIssue]:
        sub_issues_file = Path(input_path) / "sub_issues.json"
        return storage_service.read(sub_issues_file, SubIssue)

    def transform(
        self, sub_issue: SubIssue, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Get issue number mapping from context
        issue_mapping = context.get("issue_number_mapping", {})

        # Check if both parent and child issues exist in mapping
        if sub_issue.parent_issue_number not in issue_mapping:
            print(
                f"Warning: Sub-issue references unmapped parent "
                f"#{sub_issue.parent_issue_number}, skipping"
            )
            return None

        if sub_issue.sub_issue_number not in issue_mapping:
            print(
                f"Warning: Sub-issue references unmapped child "
                f"#{sub_issue.sub_issue_number}, skipping"
            )
            return None

        parent_number = issue_mapping[sub_issue.parent_issue_number]
        child_number = issue_mapping[sub_issue.sub_issue_number]

        return {
            "parent_number": parent_number,
            "child_number": child_number,
            "original_parent_number": sub_issue.parent_issue_number,
            "original_child_number": sub_issue.sub_issue_number,
        }

    def write(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Create sub-issue relationship
        github_service.add_sub_issue(
            repo_name, entity_data["parent_number"], entity_data["child_number"]
        )
        return {
            "parent_number": entity_data["parent_number"],
            "child_number": entity_data["child_number"],
            "original_parent_number": entity_data["original_parent_number"],
            "original_child_number": entity_data["original_child_number"],
        }

    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: SubIssue,
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        # Print confirmation of sub-issue relationship creation
        print(
            f"Created sub-issue relationship: #{created_data['parent_number']} -> "
            f"#{created_data['child_number']} "
            f"(was #{created_data['original_parent_number']} -> "
            f"#{created_data['original_child_number']})"
        )
