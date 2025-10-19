"""PR reviews save strategy implementation."""

from typing import List, Dict, Any

from ..strategy import SaveEntityStrategy
from ..mixins.entity_coupling import EntityCouplingMixin


class PullRequestReviewsSaveStrategy(EntityCouplingMixin, SaveEntityStrategy):
    """Strategy for saving repository PR reviews with selective filtering based on
    included pull requests."""

    def __init__(self, selective_mode: bool = False):
        """Initialize PR reviews save strategy.

        Args:
            selective_mode: Whether this strategy is operating in selective mode
        """
        self._selective_mode = selective_mode

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "pr_reviews"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return ["pull_requests"]  # PR reviews depend on pull requests being saved first

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        return "convert_to_pr_review"

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        return "get_all_pull_request_reviews"

    def transform(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform PR reviews data with pull request coupling."""
        saved_prs = context.get("pull_requests", [])
        return self.filter_children_by_parents(entities, saved_prs, "pull_requests")

    def get_parent_entity_name(self) -> str:
        """Return parent entity name."""
        return "pull_requests"

    def get_parent_api_path(self) -> str:
        """Return parent API path."""
        return "pull_requests"

    def _get_child_parent_url(self, child: Any) -> str:
        """Extract pull request URL from review."""
        return getattr(child, "pull_request_url", "")
