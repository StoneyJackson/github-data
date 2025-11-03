"""Release restore strategy implementation."""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from pathlib import Path
from github_data.operations.restore.strategy import RestoreEntityStrategy
from github_data.entities.releases.models import Release

if TYPE_CHECKING:
    from github_data.storage.protocols import StorageService
    from github_data.github.protocols import RepositoryService

logger = logging.getLogger(__name__)


class ReleasesRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring repository releases."""

    def get_entity_name(self) -> str:
        """Return the entity name for file location and logging."""
        return "releases"

    def get_dependencies(self) -> List[str]:
        """Releases have no dependencies."""
        return []

    def read(self, input_path: str, storage_service: "StorageService") -> List[Release]:
        """Load release data from JSON storage."""
        release_file = Path(input_path) / f"{self.get_entity_name()}.json"

        if not release_file.exists():
            logger.info(f"No {self.get_entity_name()} file found at {release_file}")
            return []

        return storage_service.read(release_file, Release)

    def transform(
        self, release: Release, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Transform release for creation via API."""
        creation_data = {
            "tag_name": release.tag_name,
            "target_commitish": release.target_commitish,
            "draft": release.draft,
            "prerelease": release.prerelease,
        }

        # Add optional fields
        if release.name:
            creation_data["name"] = release.name

        # Handle body with immutable note
        body = release.body or ""
        if release.immutable:
            immutable_note = (
                "\n\n---\n**Note:** Original release was marked as "
                "immutable. This flag cannot be set via API and must be "
                "configured at the organization or repository level."
            )
            body = body + immutable_note

        if body:
            creation_data["body"] = body

        return creation_data

    def write(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create release via GitHub API."""
        try:
            return github_service.create_release(
                repo_name=repo_name,
                tag_name=entity_data["tag_name"],
                target_commitish=entity_data["target_commitish"],
                name=entity_data.get("name"),
                body=entity_data.get("body"),
                draft=entity_data.get("draft", False),
                prerelease=entity_data.get("prerelease", False),
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg or "tag" in error_msg:
                logger.warning(
                    f"Release '{entity_data['tag_name']}' already exists, skipping"
                )
                # Return a mock response for consistency
                return {"tag_name": entity_data["tag_name"], "id": -1}
            raise

    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: Release,
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """Perform post-creation actions.

        Releases have no dependent entities, so no action needed.
        """
        pass

    def should_skip(self, config: Any) -> bool:
        """Skip release operations if disabled in config."""
        return not getattr(config, "include_releases", True)
