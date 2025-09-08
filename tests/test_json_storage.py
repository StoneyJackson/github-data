"""Tests for JSON storage operations."""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from pydantic import BaseModel
from typing import List

from src.storage.json_storage import save_json_data, load_json_data


class TestModel(BaseModel):
    """Test model for JSON storage operations."""
    name: str
    value: int
    active: bool = True


class TestJsonStorage:
    """Test cases for JSON storage functionality."""

    def test_save_and_load_single_model(self):
        """Test saving and loading a single model."""
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            test_data = TestModel(name="test", value=42)
            
            save_json_data(test_data, file_path)
            loaded_data = load_json_data(file_path, TestModel)
            
            assert len(loaded_data) == 1
            assert loaded_data[0].name == "test"
            assert loaded_data[0].value == 42
            assert loaded_data[0].active is True

    def test_save_and_load_list_of_models(self):
        """Test saving and loading a list of models."""
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_list.json"
            test_data = [
                TestModel(name="first", value=1),
                TestModel(name="second", value=2, active=False),
            ]
            
            save_json_data(test_data, file_path)
            loaded_data = load_json_data(file_path, TestModel)
            
            assert len(loaded_data) == 2
            assert loaded_data[0].name == "first"
            assert loaded_data[0].value == 1
            assert loaded_data[1].name == "second"
            assert loaded_data[1].active is False

    def test_save_creates_parent_directories(self):
        """Test that save_json_data creates parent directories."""
        with TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "deep" / "test.json"
            test_data = TestModel(name="nested", value=99)
            
            save_json_data(test_data, nested_path)
            
            assert nested_path.exists()
            assert nested_path.parent.exists()

    def test_load_file_not_found_raises_error(self):
        """Test that loading non-existent file raises FileNotFoundError."""
        non_existent_path = Path("does_not_exist.json")
        
        with pytest.raises(FileNotFoundError):
            load_json_data(non_existent_path, TestModel)

    def test_load_invalid_json_raises_error(self):
        """Test that loading invalid JSON raises appropriate error."""
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "invalid.json"
            
            # Write invalid JSON
            with open(file_path, 'w') as f:
                f.write("{ invalid json }")
            
            with pytest.raises(json.JSONDecodeError):
                load_json_data(file_path, TestModel)

    def test_load_non_array_json_raises_error(self):
        """Test that loading non-array JSON raises ValueError."""
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "non_array.json"
            
            # Write valid JSON but not an array
            with open(file_path, 'w') as f:
                json.dump({"name": "test", "value": 1}, f)
            
            with pytest.raises(ValueError, match="Expected JSON array"):
                load_json_data(file_path, TestModel)

    def test_json_formatting_is_readable(self):
        """Test that saved JSON is properly formatted and readable."""
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "formatted.json"
            test_data = [TestModel(name="readable", value=123)]
            
            save_json_data(test_data, file_path)
            
            # Read raw content to verify formatting
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Should be indented (multiple lines)
            assert '\n' in content
            assert '  ' in content  # Should have indentation
            
            # Should contain expected data
            assert 'readable' in content
            assert '123' in content