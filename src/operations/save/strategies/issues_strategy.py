"""Issues save strategy implementation."""

import time
from pathlib import Path
from typing import List, Dict, Any, TYPE_CHECKING, Union, Set

from ..strategy import SaveEntityStrategy

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class IssuesSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository issues with selective filtering support."""

    def __init__(self, include_issues: Union[bool, Set[int]] = True):
        """Initialize issues save strategy.
        
        Args:
            include_issues: Boolean for all/none or set of issue numbers for selective filtering
        """
        self._include_issues = include_issues

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "issues"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return ["labels"]  # Issues depend on labels being saved first

    def collect_data(
        self, github_service: "RepositoryService", repo_name: str
    ) -> List[Any]:
        """Collect issues data from GitHub API."""
        from src.github import converters

        raw_issues = github_service.get_repository_issues(repo_name)
        issues = [converters.convert_to_issue(issue_dict) for issue_dict in raw_issues]
        return issues

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
                print(f"Warning: Issues not found in repository: {sorted(missing_numbers)}")
            
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
        return hasattr(issue_data, 'number') and issue_data.number in include_spec

    def save_data(
        self,
        entities: List[Any],
        output_path: str,
        storage_service: "StorageService",
    ) -> Dict[str, Any]:
        """Save issues data to storage."""
        start_time = time.time()

        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            issues_file = output_dir / "issues.json"
            storage_service.save_data(entities, issues_file)

            execution_time = time.time() - start_time

            return {
                "success": True,
                "data_type": "issues",
                "items_processed": len(entities),
                "execution_time_seconds": execution_time,
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "data_type": "issues",
                "items_processed": 0,
                "error_message": str(e),
                "execution_time_seconds": execution_time,
            }
