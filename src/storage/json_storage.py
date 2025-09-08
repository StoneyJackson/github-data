"""
JSON file storage operations.

Handles reading and writing of JSON data files with type safety
using Pydantic models for serialization and deserialization.
"""

import json
from pathlib import Path
from typing import List, Type, TypeVar, Union
from pydantic import BaseModel

# Type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)


def save_json_data(data: Union[List[BaseModel], BaseModel], file_path: Path) -> None:
    """Save Pydantic model data to JSON file."""
    _ensure_parent_directory_exists(file_path)
    json_content = _serialize_data_to_json(data)
    _write_json_to_file(json_content, file_path)


def load_json_data(file_path: Path, model_class: Type[T]) -> List[T]:
    """Load JSON file data into Pydantic model instances."""
    _validate_file_exists(file_path)
    json_content = _read_json_from_file(file_path)
    return _deserialize_json_to_models(json_content, model_class)


def _serialize_data_to_json(data: Union[List[BaseModel], BaseModel]) -> str:
    """Convert Pydantic models to JSON string."""
    if isinstance(data, list):
        return json.dumps([item.dict() for item in data], indent=2, default=str)
    else:
        return json.dumps(data.dict(), indent=2, default=str)


def _deserialize_json_to_models(json_content: str, model_class: Type[T]) -> List[T]:
    """Convert JSON string to list of Pydantic model instances."""
    data = json.loads(json_content)
    
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")
    
    return [model_class(**item) for item in data]


def _ensure_parent_directory_exists(file_path: Path) -> None:
    """Create parent directories if they don't exist."""
    file_path.parent.mkdir(parents=True, exist_ok=True)


def _validate_file_exists(file_path: Path) -> None:
    """Validate that the specified file exists."""
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")


def _write_json_to_file(json_content: str, file_path: Path) -> None:
    """Write JSON string to file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(json_content)
    except IOError as e:
        raise IOError(f"Failed to write JSON file {file_path}: {e}") from e


def _read_json_from_file(file_path: Path) -> str:
    """Read JSON string from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except IOError as e:
        raise IOError(f"Failed to read JSON file {file_path}: {e}") from e