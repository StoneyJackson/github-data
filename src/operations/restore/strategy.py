"""Base strategy interfaces for entity restoration operations."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...storage.protocols import StorageService
    from ...github.protocols import RepositoryService


class RestoreEntityStrategy(ABC):
    """Base strategy for entity restoration operations."""

    @abstractmethod
    def get_entity_name(self) -> str:
        """Return the entity type name (e.g., 'labels', 'issues')."""
        pass

    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        pass

    @abstractmethod
    def read(self, input_path: str, storage_service: "StorageService") -> List[Any]:
        """Read entity data from storage."""
        pass

    @abstractmethod
    def transform(
        self, entity: Any, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Transform entity for GitHub API creation."""
        pass

    @abstractmethod
    def write(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Write entity via GitHub API."""
        pass

    @abstractmethod
    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: Any,
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """Perform any post-creation actions (e.g., close issues)."""
        pass


class RestoreConflictStrategy(ABC):
    """Strategy for handling conflicts during restoration."""

    @abstractmethod
    def resolve_conflicts(
        self, existing_entities: List[Any], entities_to_restore: List[Any]
    ) -> List[Any]:
        """Resolve conflicts and return entities to create."""
        pass
