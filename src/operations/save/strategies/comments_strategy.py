"""Comments save strategy implementation."""

from typing import List, Dict, Any

from ..strategy import SaveEntityStrategy
from ..mixins.entity_coupling import EntityCouplingMixin


class CommentsSaveStrategy(EntityCouplingMixin, SaveEntityStrategy):
    """Strategy for saving repository comments with selective filtering based on
    included issues."""

    def __init__(self, selective_mode: bool = False):
        """Initialize comments save strategy.

        Args:
            selective_mode: Whether this strategy is operating in selective mode
        """
        self._selective_mode = selective_mode

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "comments"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return ["issues"]  # Comments depend on issues being saved first

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        return "convert_to_comment"

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        return "get_all_issue_comments"

    def transform(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Transform comments data with issue coupling."""
        saved_issues = context.get("issues", [])
        return self.filter_children_by_parents(entities, saved_issues, "issues")

    def get_parent_entity_name(self) -> str:
        """Return parent entity name."""
        return "issues"

    def get_parent_api_path(self) -> str:
        """Return parent API path."""
        return "issues"

    def _get_child_parent_url(self, child: Any) -> str:
        """Extract issue URL from comment."""
        return getattr(child, "issue_url", "")
