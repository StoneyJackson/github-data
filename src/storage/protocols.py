"""
Abstract protocols for storage service dependencies.

Defines explicit contracts for data persistence operations, enabling better
testability and architectural flexibility through dependency inversion.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Type, TypeVar, Union, Sequence
from pydantic import BaseModel

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)


class StorageService(ABC):
    """Abstract interface for data persistence operations."""

    @abstractmethod
    def write(
        self, data: Union[Sequence[BaseModel], BaseModel], file_path: Path
    ) -> None:
        """Write model data to storage."""
        pass

    @abstractmethod
    def read(self, file_path: Path, model_class: Type[T]) -> List[T]:
        """Read data from storage into model instances."""
        pass

    def save_data(
        self, data: Union[Sequence[BaseModel], BaseModel], file_path: Path
    ) -> None:
        """Save model data to storage.

        Deprecated: Use write() instead. This method is kept for backward compatibility.
        """
        return self.write(data, file_path)

    def load_data(self, file_path: Path, model_class: Type[T]) -> List[T]:
        """Load data from storage into model instances.

        Deprecated: Use read() instead. This method is kept for backward compatibility.
        """
        return self.read(file_path, model_class)
