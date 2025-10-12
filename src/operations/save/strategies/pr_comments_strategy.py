"""PR Comments save strategy implementation."""

from typing import List, Dict, Any

from ..strategy import SaveEntityStrategy


class PullRequestCommentsSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository pull request comments."""

    def __init__(self, selective_mode: bool = False):
        """Initialize PR comments save strategy.

        Args:
            selective_mode: Whether this strategy is operating in selective mode
        """
        self._selective_mode = selective_mode

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "pr_comments"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return [
            "pull_requests"
        ]  # PR comments depend on pull requests being saved first

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        return "convert_to_pr_comment"

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        return "get_all_pull_request_comments"

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform PR comments data with pull request coupling."""
        # Check if we have saved pull requests in the context to couple with
        saved_pull_requests = context.get("pull_requests", [])

        # If no pull requests context exists, preserve original behavior
        if not saved_pull_requests:
            # For backward compatibility: if no context but comments enabled, save all
            if not hasattr(self, "_selective_mode") or not self._selective_mode:
                return entities
            else:
                print("No pull requests were saved, skipping all PR comments")
                return []

        # Selective mode: filter based on saved pull requests
        return self._filter_pr_comments_by_prs(entities, saved_pull_requests)

    def _filter_pr_comments_by_prs(
        self, entities: List[Any], saved_prs: List[Any]
    ) -> List[Any]:
        """Enhanced PR comment filtering with robust URL matching."""
        # Create multiple URL patterns for matching
        saved_pr_identifiers = set()
        for pr in saved_prs:
            if hasattr(pr, "url"):
                saved_pr_identifiers.add(pr.url)
            if hasattr(pr, "number"):
                # Add alternative URL patterns
                saved_pr_identifiers.add(f"/pulls/{pr.number}")
                saved_pr_identifiers.add(str(pr.number))

        filtered_comments = []
        for comment in entities:
            if self._comment_matches_pr(comment, saved_pr_identifiers):
                filtered_comments.append(comment)

        print(
            f"Selected {len(filtered_comments)} PR comments from {len(entities)} total "
            f"(coupling to {len(saved_prs)} saved PRs)"
        )
        return filtered_comments

    def _comment_matches_pr(self, comment: Any, saved_pr_identifiers: set) -> bool:
        """Check if comment matches any of the saved PR identifiers."""
        if (
            hasattr(comment, "pull_request_url")
            and comment.pull_request_url in saved_pr_identifiers
        ):
            return True

        # Check for partial URL matches
        if hasattr(comment, "pull_request_url"):
            for identifier in saved_pr_identifiers:
                if identifier in comment.pull_request_url:
                    return True

        return False
