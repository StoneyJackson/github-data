"""Pull Requests save strategy implementation."""

from typing import List, Dict, Any, Union, Set

from ..strategy import SaveEntityStrategy


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

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        return "convert_to_pull_request"

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        return "get_repository_pull_requests"

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
