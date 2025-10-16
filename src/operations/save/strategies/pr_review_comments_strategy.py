"""PR review comments save strategy implementation."""

from typing import List, Dict, Any

from ..strategy import SaveEntityStrategy
from ..mixins.entity_coupling import EntityCouplingMixin


class PullRequestReviewCommentsSaveStrategy(EntityCouplingMixin, SaveEntityStrategy):
    """Strategy for saving repository PR review comments with selective filtering."""

    def __init__(self, selective_mode: bool = False):
        """Initialize PR review comments save strategy.

        Args:
            selective_mode: Whether this strategy is operating in selective mode
        """
        self._selective_mode = selective_mode

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "pr_review_comments"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return [
            "pr_reviews",
            "pull_requests",
        ]  # PR review comments depend on both reviews and PRs

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        return "convert_to_pr_review_comment"

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        return "get_all_pull_request_review_comments"

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform PR review comments data with review coupling."""
        saved_reviews = context.get("pr_reviews", [])
        # Filter by reviews first, then by PRs
        filtered_by_reviews = self.filter_children_by_reviews(entities, saved_reviews)

        saved_prs = context.get("pull_requests", [])
        return self.filter_children_by_parents(
            filtered_by_reviews, saved_prs, "pull_requests"
        )

    def get_parent_entity_name(self) -> str:
        """Return parent entity name."""
        return "pr_reviews"

    def get_parent_api_path(self) -> str:
        """Return parent API path."""
        return "pulls"

    def _get_child_parent_url(self, child: Any) -> str:
        """Extract pull request URL from review comment."""
        return getattr(child, "pull_request_url", "")

    def filter_children_by_reviews(
        self, children: List[Any], saved_reviews: List[Any]
    ) -> List[Any]:
        """Filter review comments by saved reviews."""
        if not saved_reviews:
            return []

        saved_review_ids = {str(getattr(review, "id", "")) for review in saved_reviews}

        filtered_children = []
        for child in children:
            review_id = str(getattr(child, "review_id", ""))
            if review_id in saved_review_ids:
                filtered_children.append(child)

        return filtered_children
