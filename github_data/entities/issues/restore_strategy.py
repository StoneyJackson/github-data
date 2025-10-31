"""Issues restore strategy implementation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING, Union, Set
from pathlib import Path

from github_data.operations.restore.strategy import RestoreEntityStrategy
from github_data.entities.issues.models import Issue

if TYPE_CHECKING:
    from github_data.storage.protocols import StorageService
    from github_data.github.protocols import RepositoryService


class IssuesRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring GitHub issues with selective filtering support."""

    def __init__(
        self,
        include_original_metadata: bool = True,
        include_issues: Union[bool, Set[int]] = True,
    ):
        """Initialize issues restore strategy.

        Args:
            include_original_metadata: Whether to include original metadata in
                restored issues
            include_issues: Boolean for all/none or set of issue numbers for
                selective filtering
        """
        self._include_original_metadata = include_original_metadata
        self._include_issues = include_issues

    def get_entity_name(self) -> str:
        return "issues"

    def get_dependencies(self) -> List[str]:
        return ["labels", "milestones"]  # Issues depend on labels and milestones

    def read(self, input_path: str, storage_service: "StorageService") -> List[Issue]:
        """Load and filter issues data based on selection criteria."""
        issues_file = Path(input_path) / "issues.json"
        all_issues = storage_service.read(issues_file, Issue)

        if isinstance(self._include_issues, bool):
            if self._include_issues:
                # Include all issues
                return all_issues
            else:
                # Skip all issues
                return []
        else:
            # Selective filtering: include only specified issue numbers
            filtered_issues = []
            for issue in all_issues:
                if issue.number in self._include_issues:
                    filtered_issues.append(issue)

            # Log selection results for visibility
            found_numbers = {issue.number for issue in filtered_issues}
            missing_numbers = self._include_issues - found_numbers
            if missing_numbers:
                print(
                    f"Warning: Issues not found in saved data: "
                    f"{sorted(missing_numbers)}"
                )

            print(
                f"Selected {len(filtered_issues)} issues from "
                f"{len(all_issues)} total for restoration"
            )
            return filtered_issues

    def transform(
        self, issue: Issue, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Prepare issue body with metadata if needed
        if self._include_original_metadata:
            from github_data.github.metadata import add_issue_metadata_footer

            issue_body = add_issue_metadata_footer(issue)
        else:
            issue_body = issue.body or ""

        # Convert label objects to names
        label_names = [label.name for label in issue.labels]

        # Prepare basic issue data
        issue_data = {
            "title": issue.title,
            "body": issue_body,
            "labels": label_names,
            "original_number": issue.number,
            "original_state": issue.state,
            "state_reason": issue.state_reason,
        }

        # Map milestone relationship if present
        if issue.milestone:
            milestone_mapping = context.get("milestone_mapping", {})
            original_milestone_number = issue.milestone.number
            if original_milestone_number in milestone_mapping:
                new_milestone_number = milestone_mapping[original_milestone_number]
                issue_data["milestone"] = new_milestone_number
            else:
                print(
                    f"Warning: Milestone #{original_milestone_number} not found "
                    f"in mapping for issue #{issue.number}"
                )

        return issue_data

    def write(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Prepare create issue parameters
        title = entity_data["title"]
        body = entity_data["body"]
        labels = entity_data["labels"]
        milestone = entity_data.get("milestone")

        created_issue = github_service.create_issue(
            repo_name, title, body, labels, milestone=milestone
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
