"""Issues save strategy implementation."""

from typing import List, Dict, Any, Union, Set

from ..strategy import SaveEntityStrategy
from ..mixins.selective_filtering import SelectiveFilteringMixin


class IssuesSaveStrategy(SelectiveFilteringMixin, SaveEntityStrategy):
    """Strategy for saving repository issues with selective filtering support."""

    def __init__(self, include_issues: Union[bool, Set[int]] = True):
        """Initialize issues save strategy.

        Args:
            include_issues: Boolean for all/none or set of issue numbers for
                selective filtering
        """
        super().__init__(include_spec=include_issues)

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "issues"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return [
            "labels",
            "milestones",
        ]  # Issues depend on labels and milestones being saved first

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        return "convert_to_issue"

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        return "get_repository_issues"

    def transform(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Transform issues data with selective filtering."""
        return self.apply_selective_filtering(entities, context)
