"""Milestone restore strategy implementation."""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from pathlib import Path
from src.operations.restore.strategy import RestoreEntityStrategy
from src.entities.milestones.models import Milestone

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService

logger = logging.getLogger(__name__)


class MilestonesRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring repository milestones."""

    def get_entity_name(self) -> str:
        """Return the entity name for file location and logging."""
        return "milestones"

    def get_dependencies(self) -> List[str]:
        """Milestones have no dependencies."""
        return []

    def load_data(
        self, input_path: str, storage_service: "StorageService"
    ) -> List[Milestone]:
        """Load milestone data from JSON storage."""
        milestone_file = Path(input_path) / f"{self.get_entity_name()}.json"

        if not milestone_file.exists():
            logger.info(f"No {self.get_entity_name()} file found at {milestone_file}")
            return []

        return storage_service.load_data(milestone_file, Milestone)

    def transform_for_creation(
        self, milestone: Milestone, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Transform milestone for creation via API."""
        creation_data = {
            "title": milestone.title,
            "state": milestone.state,
        }

        if milestone.description:
            creation_data["description"] = milestone.description

        if milestone.due_on:
            creation_data["due_on"] = milestone.due_on.isoformat()

        return creation_data

    def create_entity(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create milestone via GitHub API."""
        try:
            return github_service.create_milestone(
                repo_name=repo_name,
                title=entity_data["title"],
                description=entity_data.get("description"),
                due_on=entity_data.get("due_on"),
                state=entity_data["state"],
            )
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.warning(
                    f"Milestone '{entity_data['title']}' already exists, skipping"
                )
                # Return a mock response for consistency
                return {"title": entity_data["title"], "number": -1}
            raise

    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: Milestone,
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """Store milestone mapping for use by dependent entities."""
        if created_data and created_data.get("number", -1) != -1:
            milestone_mapping = context.setdefault("milestone_mapping", {})
            milestone_mapping[entity.number] = created_data["number"]

    def should_skip(self, config: Any) -> bool:
        """Skip milestone operations if disabled in config."""
        return not getattr(config, "include_milestones", True)
