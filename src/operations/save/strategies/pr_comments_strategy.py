"""PR Comments save strategy implementation."""

import time
from pathlib import Path
from typing import List, Dict, Any, TYPE_CHECKING

from ..strategy import SaveEntityStrategy

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class PullRequestCommentsSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository pull request comments."""

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "pr_comments"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return [
            "pull_requests"
        ]  # PR comments depend on pull requests being saved first

    def collect_data(
        self, github_service: "RepositoryService", repo_name: str
    ) -> List[Any]:
        """Collect PR comments data from GitHub API."""
        from src.github import converters

        raw_comments = github_service.get_all_pull_request_comments(repo_name)
        pr_comments = [
            converters.convert_to_pr_comment(comment_dict)
            for comment_dict in raw_comments
        ]
        return pr_comments

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform PR comments data with pull request coupling."""
        # Check if we have saved pull requests in the context to couple with
        saved_pull_requests = context.get("pull_requests", [])
        
        if not saved_pull_requests:
            # No pull requests were saved, so no PR comments should be saved
            print("No pull requests were saved, skipping all PR comments")
            return []
        
        # Create a set of PR URLs from saved pull requests for efficient lookup
        saved_pr_urls = set()
        for pr in saved_pull_requests:
            if hasattr(pr, 'url'):
                saved_pr_urls.add(pr.url)
        
        if not saved_pr_urls:
            print("No valid PR URLs found in saved pull requests, skipping all PR comments")
            return []
        
        # Filter PR comments to only include those from saved pull requests
        filtered_pr_comments = []
        for comment in entities:
            if hasattr(comment, 'pull_request_url') and comment.pull_request_url in saved_pr_urls:
                filtered_pr_comments.append(comment)
        
        print(f"Selected {len(filtered_pr_comments)} PR comments from {len(entities)} total (coupling to {len(saved_pull_requests)} saved PRs)")
        return filtered_pr_comments

    def save_data(
        self,
        entities: List[Any],
        output_path: str,
        storage_service: "StorageService",
    ) -> Dict[str, Any]:
        """Save PR comments data to storage."""
        start_time = time.time()

        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            pr_comments_file = output_dir / "pr_comments.json"
            storage_service.save_data(entities, pr_comments_file)

            execution_time = time.time() - start_time

            return {
                "success": True,
                "data_type": "pr_comments",
                "items_processed": len(entities),
                "execution_time_seconds": execution_time,
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "data_type": "pr_comments",
                "items_processed": 0,
                "error_message": str(e),
                "execution_time_seconds": execution_time,
            }
