"""Sub-Issues save strategy implementation."""

from typing import List, Dict, Any

from github_data.operations.save.strategy import SaveEntityStrategy


class SubIssuesSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository sub-issues."""

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "sub_issues"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return ["issues"]  # Sub-issues depend on issues being saved first

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        return "convert_to_sub_issue"

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        return "get_repository_sub_issues"

    def transform(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
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
