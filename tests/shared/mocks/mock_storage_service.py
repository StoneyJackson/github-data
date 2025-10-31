"""
Mock storage service for testing.

Provides a fake implementation of the StorageService protocol
for unit testing without file I/O dependencies.
"""

from pathlib import Path
from typing import List, Type, TypeVar, Union, Sequence, Dict, Any
from pydantic import BaseModel
from github_data.storage.protocols import StorageService

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)


class MockStorageService(StorageService):
    """In-memory storage service for testing."""

    def __init__(self):
        """Initialize with empty storage."""
        self.stored_data: Dict[str, Any] = {}
        self.save_calls: List[Dict[str, Any]] = []
        self.load_calls: List[Dict[str, Any]] = []

    def write(
        self, data: Union[Sequence[BaseModel], BaseModel], file_path: Path
    ) -> None:
        """Write model data to in-memory storage."""
        # Record the call for test verification
        call_info = {
            "file_path": str(file_path),
            "data_type": (
                type(data).__name__ if isinstance(data, BaseModel) else "Sequence"
            ),
            "data_count": 1 if isinstance(data, BaseModel) else len(data),
        }
        self.save_calls.append(call_info)

        # Store the actual data
        if isinstance(data, BaseModel):
            self.stored_data[str(file_path)] = [data.model_dump()]
        else:
            self.stored_data[str(file_path)] = [item.model_dump() for item in data]

    def read(self, file_path: Path, model_class: Type[T]) -> List[T]:
        """Read data from in-memory storage into model instances."""
        # Record the call for test verification
        call_info = {
            "file_path": str(file_path),
            "model_class": model_class.__name__,
        }
        self.load_calls.append(call_info)

        # Return stored data as model instances
        file_path_str = str(file_path)
        if file_path_str not in self.stored_data:
            raise FileNotFoundError(f"Mock file not found: {file_path}")

        raw_data = self.stored_data[file_path_str]
        return [model_class(**item) for item in raw_data]

    def add_mock_data(self, file_path: Path, data: List[Dict[str, Any]]) -> None:
        """Add mock data for testing load operations."""
        self.stored_data[str(file_path)] = data

    def was_data_saved(self, file_path: Path) -> bool:
        """Check if data was saved to a specific path."""
        return str(file_path) in self.stored_data

    def get_saved_data_count(self, file_path: Path) -> int:
        """Get the number of items saved to a specific path."""
        file_path_str = str(file_path)
        if file_path_str not in self.stored_data:
            return 0
        return len(self.stored_data[file_path_str])

    def clear_storage(self) -> None:
        """Clear all stored data and call history."""
        self.stored_data.clear()
        self.save_calls.clear()
        self.load_calls.clear()
