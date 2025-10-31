"""Pull Requests save strategy implementation."""

from typing import List, Dict, Any, Union, Set

from github_data.operations.save.strategy import SaveEntityStrategy
from github_data.operations.save.mixins.selective_filtering import (
    SelectiveFilteringMixin,
)


class PullRequestsSaveStrategy(SelectiveFilteringMixin, SaveEntityStrategy):
    """Strategy for saving repository pull requests with selective filtering support."""

    def __init__(self, include_pull_requests: Union[bool, Set[int]] = True):
        """Initialize pull requests save strategy.

        Args:
            include_pull_requests: Boolean for all/none or set of PR numbers for
                selective filtering
        """
        super().__init__(include_spec=include_pull_requests)

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "pull_requests"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return [
            "labels",
            "milestones",
        ]  # Pull requests depend on labels and milestones being saved first

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        return "convert_to_pull_request"

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        return "get_repository_pull_requests"

    def transform(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform pull requests data with selective filtering."""
        return self.apply_selective_filtering(entities, context)
