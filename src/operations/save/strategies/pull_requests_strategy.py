"""Pull Requests save strategy implementation."""

import time
from pathlib import Path
from typing import List, Dict, Any, TYPE_CHECKING, Union, Set

from ..strategy import SaveEntityStrategy

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class PullRequestsSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository pull requests with selective filtering support."""

    def __init__(self, include_pull_requests: Union[bool, Set[int]] = True):
        """Initialize pull requests save strategy.

        Args:
            include_pull_requests: Boolean for all/none or set of PR numbers for
                selective filtering
        """
        self._include_pull_requests = include_pull_requests

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "pull_requests"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return ["labels"]  # Pull requests depend on labels being saved first

    def collect_data(
        self, github_service: "RepositoryService", repo_name: str
    ) -> List[Any]:
        """Collect pull requests data from GitHub API."""
        from src.github import converters

        raw_prs = github_service.get_repository_pull_requests(repo_name)
        pull_requests = [
            converters.convert_to_pull_request(pr_dict) for pr_dict in raw_prs
        ]
        return pull_requests

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform pull requests data with selective filtering."""
        if isinstance(self._include_pull_requests, bool):
            if self._include_pull_requests:
                # Include all pull requests
                return entities
            else:
                # Skip all pull requests
                return []
        else:
            # Selective filtering: include only specified PR numbers
            filtered_prs = []
            for pr in entities:
                if self._should_include_pull_request(pr, self._include_pull_requests):
                    filtered_prs.append(pr)

            # Log selection results for visibility
            found_numbers = {pr.number for pr in filtered_prs}
            missing_numbers = self._include_pull_requests - found_numbers
            if missing_numbers:
                print(
                    f"Warning: Pull requests not found in repository: "
                    f"{sorted(missing_numbers)}"
                )

            print(
                f"Selected {len(filtered_prs)} pull requests from {len(entities)} total"
            )
            return filtered_prs

    def _should_include_pull_request(
        self, pr_data: Any, include_spec: Set[int]
    ) -> bool:
        """Determine if pull request should be included based on specification.

        Args:
            pr_data: PR data object with 'number' attribute
            include_spec: Set of specific PR numbers to include

        Returns:
            True if PR should be included, False otherwise
        """
        return hasattr(pr_data, "number") and pr_data.number in include_spec

    def save_data(
        self,
        entities: List[Any],
        output_path: str,
        storage_service: "StorageService",
    ) -> Dict[str, Any]:
        """Save pull requests data to storage."""
        start_time = time.time()

        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            prs_file = output_dir / "pull_requests.json"
            storage_service.save_data(entities, prs_file)

            execution_time = time.time() - start_time

            return {
                "success": True,
                "data_type": "pull_requests",
                "items_processed": len(entities),
                "execution_time_seconds": execution_time,
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "data_type": "pull_requests",
                "items_processed": 0,
                "error_message": str(e),
                "execution_time_seconds": execution_time,
            }
