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

    def load_data(
        self, input_path: str, storage_service: "StorageService"
    ) -> List[Any]:
        """Load entity data from storage.

        Deprecated: Use read() instead. This method is kept for backward compatibility.
        """
        return self.read(input_path, storage_service)

    @abstractmethod
    def transform(
        self, entity: Any, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Transform entity for GitHub API creation."""
        pass

    def transform_for_creation(
        self, entity: Any, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Transform entity for GitHub API creation.

        Deprecated: Use transform() instead. This method is kept for backward
        compatibility.
        """
        return self.transform(entity, context)

    @abstractmethod
    def write(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Write entity via GitHub API."""
        pass

    def create_entity(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create entity via GitHub API.

        Deprecated: Use write() instead. This method is kept for backward compatibility.
        """
        return self.write(github_service, repo_name, entity_data)

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
