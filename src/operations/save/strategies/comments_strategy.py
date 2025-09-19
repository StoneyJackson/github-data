"""Comments save strategy implementation."""

import time
from pathlib import Path
from typing import List, Dict, Any, TYPE_CHECKING

from ..strategy import SaveEntityStrategy

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class CommentsSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository comments."""

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
        """Process and transform comments data."""
        # Comments don't require any processing
        return entities

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
