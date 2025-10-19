"""
JSON storage service implementation.

Provides a concrete implementation of the StorageService protocol
using JSON file operations.
"""

from pathlib import Path
from typing import List, Type, TypeVar, Union, Sequence
from pydantic import BaseModel
from .protocols import StorageService
from .json_storage import save_json_data, load_json_data

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)


class JsonStorageService(StorageService):
    """JSON file storage implementation."""

    def write(
        self, data: Union[Sequence[BaseModel], BaseModel], file_path: Path
    ) -> None:
        """Write model data to JSON file."""
        return save_json_data(data, file_path)

    def read(self, file_path: Path, model_class: Type[T]) -> List[T]:
        """Read data from JSON file into model instances."""
        return load_json_data(file_path, model_class)
