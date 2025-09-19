"""Base strategy interfaces for entity save operations."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class SaveEntityStrategy(ABC):
    """Base strategy for entity save operations."""

    @abstractmethod
    def get_entity_name(self) -> str:
        """Return the entity type name (e.g., 'labels', 'issues')."""
        pass

    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        pass

    @abstractmethod
    def collect_data(
        self, github_service: "RepositoryService", repo_name: str
    ) -> List[Any]:
        """Collect entity data from GitHub API."""
        pass

    @abstractmethod
    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform entity data."""
        pass

    @abstractmethod
    def save_data(
        self,
        entities: List[Any],
        output_path: str,
        storage_service: "StorageService",
    ) -> Dict[str, Any]:
        """Save entity data to storage."""
        pass
