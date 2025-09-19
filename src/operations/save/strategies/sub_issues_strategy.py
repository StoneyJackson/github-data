"""Sub-Issues save strategy implementation."""

import time
from pathlib import Path
from typing import List, Dict, Any, TYPE_CHECKING

from ..strategy import SaveEntityStrategy

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class SubIssuesSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository sub-issues."""

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "sub_issues"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return ["issues"]  # Sub-issues depend on issues being saved first

    def collect_data(
        self, github_service: "RepositoryService", repo_name: str
    ) -> List[Any]:
        """Collect sub-issues data from GitHub API."""
        from src.github import converters

        raw_sub_issues = github_service.get_repository_sub_issues(repo_name)
        sub_issues = [
            converters.convert_to_sub_issue(sub_issue_dict)
            for sub_issue_dict in raw_sub_issues
        ]
        return sub_issues

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform sub-issues data."""
        # Get issues from context (saved by issues strategy)
        issues = context.get("issues", [])
        if not issues:
            return entities  # If no issues in context, just return sub-issues as-is

        # Associate sub-issues with their parent issues
        issues_copy = [issue.model_copy() for issue in issues]

        # Create a mapping from issue number to issue index
        issue_number_to_index = {issue.number: i for i, issue in enumerate(issues_copy)}

        # Group sub-issues by parent issue number
        sub_issues_by_parent: Dict[int, List[Any]] = {}
        for sub_issue in entities:
            parent_number = sub_issue.parent_issue_number
            if parent_number not in sub_issues_by_parent:
                sub_issues_by_parent[parent_number] = []
            sub_issues_by_parent[parent_number].append(sub_issue)

        # Associate sub-issues with their parent issues
        for parent_number, child_sub_issues in sub_issues_by_parent.items():
            if parent_number in issue_number_to_index:
                parent_index = issue_number_to_index[parent_number]
                # Sort sub-issues by position
                sorted_sub_issues = sorted(child_sub_issues, key=lambda si: si.position)
                issues_copy[parent_index].sub_issues = sorted_sub_issues

        # Update the context with the updated issues
        context["issues"] = issues_copy

        return entities

    def save_data(
        self,
        entities: List[Any],
        output_path: str,
        storage_service: "StorageService",
    ) -> Dict[str, Any]:
        """Save sub-issues data to storage."""
        start_time = time.time()

        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save sub-issues
            sub_issues_file = output_dir / "sub_issues.json"
            storage_service.save_data(entities, sub_issues_file)

            execution_time = time.time() - start_time

            return {
                "success": True,
                "data_type": "sub_issues",
                "items_processed": len(entities),
                "execution_time_seconds": execution_time,
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "data_type": "sub_issues",
                "items_processed": 0,
                "error_message": str(e),
                "execution_time_seconds": execution_time,
            }
