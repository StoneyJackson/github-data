"""Labels save strategy implementation."""

import time
from pathlib import Path
from typing import List, Dict, Any, TYPE_CHECKING

from ..strategy import SaveEntityStrategy

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class LabelsSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository labels."""

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "labels"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return []  # Labels have no dependencies

    def collect_data(
        self, github_service: "RepositoryService", repo_name: str
    ) -> List[Any]:
        """Collect labels data from GitHub API."""
        from src.github import converters

        raw_labels = github_service.get_repository_labels(repo_name)
        labels = [converters.convert_to_label(label_dict) for label_dict in raw_labels]
        return labels

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform labels data."""
        # Labels don't require any processing
        return entities

    def save_data(
        self,
        entities: List[Any],
        output_path: str,
        storage_service: "StorageService",
    ) -> Dict[str, Any]:
        """Save labels data to storage."""
        start_time = time.time()

        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            labels_file = output_dir / "labels.json"
            storage_service.save_data(entities, labels_file)

            execution_time = time.time() - start_time

            return {
                "success": True,
                "data_type": "labels",
                "items_processed": len(entities),
                "execution_time_seconds": execution_time,
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "data_type": "labels",
                "items_processed": 0,
                "error_message": str(e),
                "execution_time_seconds": execution_time,
            }
