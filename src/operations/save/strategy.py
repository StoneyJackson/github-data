"""Base strategy interfaces for entity save operations."""

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, TYPE_CHECKING, Callable

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

    def read(self, github_service: "RepositoryService", repo_name: str) -> List[Any]:
        """Template method for reading data from external source."""
        converter_name = self.get_converter_name()
        service_method = self.get_service_method()

        raw_data = getattr(github_service, service_method)(repo_name)

        # Import converters dynamically to avoid circular imports
        from src.github import converters

        converter = getattr(converters, converter_name)
        return [converter(item) for item in raw_data]

    def collect_data(
        self, github_service: "RepositoryService", repo_name: str
    ) -> List[Any]:
        """Template method for standard data collection pattern.

        Deprecated: Use read() instead. This method is kept for backward compatibility.
        """
        return self.read(github_service, repo_name)

    @abstractmethod
    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        pass

    @abstractmethod
    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        pass

    @abstractmethod
    def transform(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Transform entity data for processing."""
        pass

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform entity data.

        Deprecated: Use transform() instead. This method is kept for backward
        compatibility.
        """
        return self.transform(entities, context)

    def write(
        self,
        entities: List[Any],
        output_path: str,
        storage_service: "StorageService",
    ) -> Dict[str, Any]:
        """Template method for writing entity data with standardized timing and
        error handling."""
        return self._execute_with_timing(
            lambda: self._perform_save(entities, output_path, storage_service),
            self.get_entity_name(),
            len(entities),
        )

    def save_data(
        self,
        entities: List[Any],
        output_path: str,
        storage_service: "StorageService",
    ) -> Dict[str, Any]:
        """Template method for saving entity data with standardized timing and
        error handling.

        Deprecated: Use write() instead. This method is kept for backward compatibility.
        """
        return self.write(entities, output_path, storage_service)

    def _execute_with_timing(
        self, operation: Callable[[], None], entity_type: str, item_count: int
    ) -> Dict[str, Any]:
        """Execute operation with timing and standardized result formatting."""
        start_time = time.time()
        try:
            operation()
            execution_time = time.time() - start_time
            return self._success_result(entity_type, item_count, execution_time)
        except Exception as e:
            execution_time = time.time() - start_time
            return self._error_result(entity_type, str(e), execution_time)

    def _perform_save(
        self, entities: List[Any], output_path: str, storage_service: "StorageService"
    ) -> None:
        """Standard save implementation using entity name."""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        entity_file = output_dir / f"{self.get_entity_name()}.json"
        storage_service.save_data(entities, entity_file)

    def _success_result(
        self, entity_type: str, item_count: int, execution_time: float
    ) -> Dict[str, Any]:
        """Standard success result format."""
        return {
            "success": True,
            "data_type": entity_type,
            "items_processed": item_count,
            "execution_time_seconds": execution_time,
        }

    def _error_result(
        self, entity_type: str, error_message: str, execution_time: float
    ) -> Dict[str, Any]:
        """Standard error result format."""
        return {
            "success": False,
            "data_type": entity_type,
            "items_processed": 0,
            "error_message": error_message,
            "execution_time_seconds": execution_time,
        }
