"""Issues save strategy implementation."""

from typing import List, Dict, Any, Union, Set

from ..strategy import SaveEntityStrategy


class IssuesSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository issues with selective filtering support."""

    def __init__(self, include_issues: Union[bool, Set[int]] = True):
        """Initialize issues save strategy.

        Args:
            include_issues: Boolean for all/none or set of issue numbers for
                selective filtering
        """
        self._include_issues = include_issues

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "issues"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return ["labels"]  # Issues depend on labels being saved first

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        return "convert_to_issue"

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        return "get_repository_issues"

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform issues data with selective filtering."""
        if isinstance(self._include_issues, bool):
            if self._include_issues:
                # Include all issues
                return entities
            else:
                # Skip all issues
                return []
        else:
            # Selective filtering: include only specified issue numbers
            filtered_issues = []
            for issue in entities:
                if self._should_include_issue(issue, self._include_issues):
                    filtered_issues.append(issue)

            # Log selection results for visibility
            found_numbers = {issue.number for issue in filtered_issues}
            missing_numbers = self._include_issues - found_numbers
            if missing_numbers:
                print(
                    f"Warning: Issues not found in repository: "
                    f"{sorted(missing_numbers)}"
                )

            print(f"Selected {len(filtered_issues)} issues from {len(entities)} total")
            return filtered_issues

    def _should_include_issue(self, issue_data: Any, include_spec: Set[int]) -> bool:
        """Determine if issue should be included based on specification.

        Args:
            issue_data: Issue data object with 'number' attribute
            include_spec: Set of specific issue numbers to include

        Returns:
            True if issue should be included, False otherwise
        """
        return hasattr(issue_data, "number") and issue_data.number in include_spec
