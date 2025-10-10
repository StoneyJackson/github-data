"""Comments save strategy implementation."""

import time
from pathlib import Path
from typing import List, Dict, Any, TYPE_CHECKING

from ..strategy import SaveEntityStrategy

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class CommentsSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository comments with selective filtering based on included issues."""

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "comments"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return ["issues"]  # Comments depend on issues being saved first

    def collect_data(
        self, github_service: "RepositoryService", repo_name: str
    ) -> List[Any]:
        """Collect comments data from GitHub API."""
        from src.github import converters

        raw_comments = github_service.get_all_issue_comments(repo_name)
        comments = [
            converters.convert_to_comment(comment_dict) for comment_dict in raw_comments
        ]
        return comments

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform comments data with issue coupling."""
        # Check if we have saved issues in the context to couple with
        saved_issues = context.get("issues", [])
        
        if not saved_issues:
            # No issues were saved, so no comments should be saved
            print("No issues were saved, skipping all issue comments")
            return []
        
        # Create a set of issue URLs from saved issues for efficient lookup
        saved_issue_urls = set()
        for issue in saved_issues:
            if hasattr(issue, 'url'):
                saved_issue_urls.add(issue.url)
        
        if not saved_issue_urls:
            print("No valid issue URLs found in saved issues, skipping all comments")
            return []
        
        # Filter comments to only include those from saved issues
        filtered_comments = []
        for comment in entities:
            if hasattr(comment, 'issue_url') and comment.issue_url in saved_issue_urls:
                filtered_comments.append(comment)
        
        print(f"Selected {len(filtered_comments)} comments from {len(entities)} total (coupling to {len(saved_issues)} saved issues)")
        return filtered_comments

    def save_data(
        self,
        entities: List[Any],
        output_path: str,
        storage_service: "StorageService",
    ) -> Dict[str, Any]:
        """Save comments data to storage."""
        start_time = time.time()

        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            comments_file = output_dir / "comments.json"
            storage_service.save_data(entities, comments_file)

            execution_time = time.time() - start_time

            return {
                "success": True,
                "data_type": "comments",
                "items_processed": len(entities),
                "execution_time_seconds": execution_time,
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "data_type": "comments",
                "items_processed": 0,
                "error_message": str(e),
                "execution_time_seconds": execution_time,
            }
