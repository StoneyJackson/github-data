"""Comments save strategy implementation."""

from typing import List, Dict, Any

from ..strategy import SaveEntityStrategy


class CommentsSaveStrategy(SaveEntityStrategy):
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

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform comments data with issue coupling."""
        # Check if we have saved issues in the context to couple with
        saved_issues = context.get("issues", [])

        # If no issues context exists, preserve original behavior
        if not saved_issues:
            # For backward compatibility: if no context but comments enabled, save all
            if not hasattr(self, "_selective_mode") or not self._selective_mode:
                return entities
            else:
                print("No issues were saved, skipping all issue comments")
                return []

        # Selective mode: filter based on saved issues
        return self._filter_comments_by_issues(entities, saved_issues)

    def _filter_comments_by_issues(
        self, entities: List[Any], saved_issues: List[Any]
    ) -> List[Any]:
        """Filter comments to only include those from saved issues."""
        # Create a set of issue identifiers from saved issues for efficient lookup
        saved_issue_identifiers = set()
        for issue in saved_issues:
            # Add issue number as identifier
            if hasattr(issue, "number"):
                saved_issue_identifiers.add(str(issue.number))
            # Add various URL patterns
            if hasattr(issue, "html_url"):
                saved_issue_identifiers.add(issue.html_url)
                # Extract issue number from html_url and create API URL
                try:
                    issue_number = issue.html_url.split("/")[-1]
                    # Create API URL pattern:
                    api_url_pattern = f"/issues/{issue_number}"
                    saved_issue_identifiers.add(api_url_pattern)
                except (IndexError, ValueError):
                    pass

        if not saved_issue_identifiers:
            print(
                "No valid issue identifiers found in saved issues, "
                "skipping all comments"
            )
            return []

        # Filter comments to only include those from saved issues
        filtered_comments = []
        for comment in entities:
            if self._comment_matches_issue(comment, saved_issue_identifiers):
                filtered_comments.append(comment)

        print(
            f"Selected {len(filtered_comments)} comments from {len(entities)} total "
            f"(coupling to {len(saved_issues)} saved issues)"
        )
        return filtered_comments

    def _comment_matches_issue(
        self, comment: Any, saved_issue_identifiers: set
    ) -> bool:
        """Check if comment matches any of the saved issue identifiers."""
        if hasattr(comment, "issue_url"):
            # Direct match
            if comment.issue_url in saved_issue_identifiers:
                return True
            # Check for partial URL matches
            for identifier in saved_issue_identifiers:
                if identifier in comment.issue_url:
                    return True
            # Check issue number extracted from URL
            try:
                issue_number = comment.issue_url.split("/")[-1]
                if issue_number in saved_issue_identifiers:
                    return True
            except (IndexError, ValueError):
                pass

        return False
