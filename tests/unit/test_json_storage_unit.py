"""Tests for JSON storage operations."""

import json
import pytest
import time
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from pydantic import BaseModel
from unittest.mock import patch

from github_data.storage.json_storage import save_json_data, load_json_data

# Fixtures are auto-injected by pytest via conftest.py

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.storage]


class SampleModel(BaseModel):
    """Sample model for JSON storage operations."""

    name: str
    value: int
    active: bool = True


class TestJsonStorage:
    """Test cases for JSON storage functionality."""

    def test_save_and_load_single_model(self):
        """Test saving and loading a single model."""
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            test_data = SampleModel(name="test", value=42)

            save_json_data(test_data, file_path)
            loaded_data = load_json_data(file_path, SampleModel)

            assert len(loaded_data) == 1
            assert loaded_data[0].name == "test"
            assert loaded_data[0].value == 42
            assert loaded_data[0].active is True

    def test_save_and_load_list_of_models(self):
        """Test saving and loading a list of models."""
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_list.json"
            test_data = [
                SampleModel(name="first", value=1),
                SampleModel(name="second", value=2, active=False),
            ]

            save_json_data(test_data, file_path)
            loaded_data = load_json_data(file_path, SampleModel)

            assert len(loaded_data) == 2
            assert loaded_data[0].name == "first"
            assert loaded_data[0].value == 1
            assert loaded_data[1].name == "second"
            assert loaded_data[1].active is False

    def test_save_creates_parent_directories(self):
        """Test that save_json_data creates parent directories."""
        with TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "deep" / "test.json"
            test_data = SampleModel(name="nested", value=99)

            save_json_data(test_data, nested_path)

            assert nested_path.exists()
            assert nested_path.parent.exists()

    def test_load_file_not_found_raises_error(self):
        """Test that loading non-existent file raises FileNotFoundError."""
        non_existent_path = Path("does_not_exist.json")

        with pytest.raises(FileNotFoundError):
            load_json_data(non_existent_path, SampleModel)

    def test_load_invalid_json_raises_error(self):
        """Test that loading invalid JSON raises appropriate error."""
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "invalid.json"

            # Write invalid JSON
            with open(file_path, "w") as f:
                f.write("{ invalid json }")

            with pytest.raises(json.JSONDecodeError):
                load_json_data(file_path, SampleModel)

    def test_load_non_object_or_array_json_raises_error(self):
        """Test that loading JSON that is neither object nor array raises ValueError."""
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "invalid_type.json"

            # Write valid JSON but neither object nor array
            # (e.g., string, number, boolean)
            with open(file_path, "w") as f:
                json.dump("invalid_data_type", f)

            with pytest.raises(ValueError, match="Expected JSON array or object"):
                load_json_data(file_path, SampleModel)

    def test_json_formatting_is_readable(self):
        """Test that saved JSON is properly formatted and readable."""
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "formatted.json"
            test_data = [SampleModel(name="readable", value=123)]

            save_json_data(test_data, file_path)

            # Read raw content to verify formatting
            with open(file_path, "r") as f:
                content = f.read()

            # Should be indented (multiple lines)
            assert "\n" in content
            assert "  " in content  # Should have indentation

            # Should contain expected data
            assert "readable" in content
            assert "123" in content


@pytest.mark.storage
@pytest.mark.error_simulation
class TestJsonStorageErrorConditions:
    """Test JSON storage error handling and edge cases."""

    def test_save_to_readonly_directory(self, temp_data_dir):
        """Test saving to a read-only directory raises appropriate error."""
        readonly_dir = Path(temp_data_dir) / "readonly"
        readonly_dir.mkdir()
        os.chmod(readonly_dir, 0o444)  # Read-only

        file_path = readonly_dir / "test.json"
        test_data = SampleModel(name="test", value=42)

        try:
            with pytest.raises((PermissionError, OSError)):
                save_json_data(test_data, file_path)
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)

    def test_save_to_invalid_path(self):
        """Test saving to invalid path raises appropriate error."""
        # Try to save to a path with null bytes (invalid on most filesystems)
        invalid_path = Path("invalid\x00path.json")
        test_data = SampleModel(name="test", value=42)

        with pytest.raises((ValueError, OSError)):
            save_json_data(test_data, invalid_path)

    @patch("builtins.open", side_effect=OSError("Disk full"))
    def test_save_disk_full_error(self, _mock_file):
        """Test handling of disk full errors during save."""
        test_data = SampleModel(name="test", value=42)
        file_path = Path("test.json")

        with pytest.raises(OSError, match="Disk full"):
            save_json_data(test_data, file_path)

    def test_load_corrupted_json_with_encoding_issues(self, temp_data_dir):
        """Test loading JSON with encoding issues."""
        file_path = Path(temp_data_dir) / "corrupted.json"

        # Write file with invalid UTF-8 bytes
        with open(file_path, "wb") as f:
            f.write(b'{"name": "test\xff", "value": 42}')

        with pytest.raises((UnicodeDecodeError, json.JSONDecodeError)):
            load_json_data(file_path, SampleModel)

    def test_load_json_with_missing_required_fields(self, temp_data_dir):
        """Test loading JSON missing required model fields."""
        file_path = Path(temp_data_dir) / "incomplete.json"

        # Write JSON missing required 'value' field
        incomplete_data = [{"name": "test", "active": True}]
        with open(file_path, "w") as f:
            json.dump(incomplete_data, f)

        with pytest.raises(Exception):  # Pydantic validation error
            load_json_data(file_path, SampleModel)

    def test_load_json_with_wrong_data_types(self, temp_data_dir):
        """Test loading JSON with incorrect data types."""
        file_path = Path(temp_data_dir) / "wrong_types.json"

        # Write JSON with wrong types (string for int field)
        wrong_data = [{"name": "test", "value": "not_a_number", "active": True}]
        with open(file_path, "w") as f:
            json.dump(wrong_data, f)

        with pytest.raises(Exception):  # Pydantic validation error
            load_json_data(file_path, SampleModel)

    def test_load_memory_error(self, temp_data_dir):
        """Test handling of memory errors during load by simulating large file."""
        file_path = Path(temp_data_dir) / "large_file.json"

        # Create a very large JSON file that could cause memory issues
        large_data = [SampleModel(name=f"large_{i}", value=i) for i in range(10000)]
        save_json_data(large_data, file_path)

        # For this test, we just verify it can handle reasonably large files
        # In a real scenario with insufficient memory, this would fail
        loaded_data = load_json_data(file_path, SampleModel)
        assert len(loaded_data) == 10000

    def test_save_very_large_dataset(self, temp_data_dir):
        """Test saving large datasets to verify memory handling."""
        file_path = Path(temp_data_dir) / "large.json"

        # Create large dataset (but not too large for CI)
        large_data = [
            SampleModel(name=f"item_{i}", value=i, active=i % 2 == 0)
            for i in range(1000)
        ]

        # Should not raise memory errors for reasonable large datasets
        save_json_data(large_data, file_path)
        loaded_data = load_json_data(file_path, SampleModel)

        assert len(loaded_data) == 1000
        assert loaded_data[0].name == "item_0"
        assert loaded_data[999].name == "item_999"


@pytest.mark.storage
@pytest.mark.performance
class TestJsonStoragePerformance:
    """Test JSON storage performance and timing."""

    def test_save_performance_timing(self, temp_data_dir):
        """Test save operation performance with timing validation."""
        file_path = Path(temp_data_dir) / "performance.json"

        # Create moderately sized dataset
        test_data = [
            SampleModel(name=f"perf_test_{i}", value=i, active=i % 3 == 0)
            for i in range(100)
        ]

        start_time = time.time()
        save_json_data(test_data, file_path)
        save_time = time.time() - start_time

        # Performance assertion: should complete within reasonable time
        assert save_time < 1.0, f"Save took {save_time:.3f}s, expected < 1.0s"

        # Verify file was created and has expected size
        assert file_path.exists()
        assert file_path.stat().st_size > 1000  # Should be substantial

    def test_load_performance_timing(self, temp_data_dir):
        """Test load operation performance with timing validation."""
        file_path = Path(temp_data_dir) / "load_perf.json"

        # Prepare test data
        test_data = [
            SampleModel(name=f"load_test_{i}", value=i * 2, active=i % 2 == 1)
            for i in range(100)
        ]
        save_json_data(test_data, file_path)

        # Time the load operation
        start_time = time.time()
        loaded_data = load_json_data(file_path, SampleModel)
        load_time = time.time() - start_time

        # Performance assertion
        assert load_time < 1.0, f"Load took {load_time:.3f}s, expected < 1.0s"
        assert len(loaded_data) == 100

    def test_repeated_operations_consistency(self, temp_data_dir):
        """Test performance consistency across repeated operations."""
        file_path = Path(temp_data_dir) / "repeated.json"
        test_data = [SampleModel(name="repeat", value=i) for i in range(50)]

        # Warmup iteration to eliminate cold-start effects
        save_json_data(test_data, file_path)
        load_json_data(file_path, SampleModel)

        save_times = []
        load_times = []

        # Perform multiple save/load cycles with larger sample size
        for _ in range(10):
            # Save timing
            start_time = time.time()
            save_json_data(test_data, file_path)
            save_times.append(time.time() - start_time)

            # Load timing
            start_time = time.time()
            loaded_data = load_json_data(file_path, SampleModel)
            load_times.append(time.time() - start_time)

            assert len(loaded_data) == 50

        # Performance consistency checks
        avg_save_time = sum(save_times) / len(save_times)
        avg_load_time = sum(load_times) / len(load_times)

        assert avg_save_time < 0.5, f"Average save time {avg_save_time:.3f}s too slow"
        assert avg_load_time < 0.5, f"Average load time {avg_load_time:.3f}s too slow"

        # Consistency check: no operation should be more than 10x average
        # Using 10x threshold to accommodate system variability and I/O patterns
        # With 10 samples, this provides reasonable statistical confidence
        # while allowing for occasional system load spikes
        max_save_time = max(save_times)
        max_load_time = max(load_times)

        assert max_save_time < avg_save_time * 10, (
            f"Save time inconsistent: max={max_save_time:.3f}s, "
            f"avg={avg_save_time:.3f}s, "
            f"ratio={max_save_time/avg_save_time:.1f}x"
        )
        assert max_load_time < avg_load_time * 10, (
            f"Load time inconsistent: max={max_load_time:.3f}s, "
            f"avg={avg_load_time:.3f}s, "
            f"ratio={max_load_time/avg_load_time:.1f}x"
        )


@pytest.mark.storage
@pytest.mark.integration
@pytest.mark.medium
class TestJsonStorageIntegration:
    """Test JSON storage integration with enhanced fixtures."""

    def test_storage_with_temp_service(self, storage_service_for_temp_dir):
        """Test JSON storage using shared temp directory service."""
        service = storage_service_for_temp_dir
        test_data = [SampleModel(name="service_test", value=99)]

        # Use storage service to save data
        labels_file = Path(service._base_path) / "labels.json"
        service.write(test_data, labels_file)

        # Verify file was created in temp directory
        temp_dir = Path(service._base_path)
        labels_file = temp_dir / "labels.json"
        assert labels_file.exists()

        # Load using storage service to verify integration
        loaded_data = service.read(labels_file, SampleModel)
        assert len(loaded_data) == 1
        assert loaded_data[0].name == "service_test"
        assert loaded_data[0].value == 99

    def test_storage_error_handling_integration(self, temp_data_dir):
        """Test storage error handling in integration scenarios."""
        from github_data.storage import create_storage_service

        service = create_storage_service("json")
        service._base_path = temp_data_dir

        # Test with invalid data type that should be caught
        invalid_data = "not_a_list_or_model"

        with pytest.raises(Exception):
            invalid_file = Path(temp_data_dir) / "invalid.json"
            service.write(invalid_data, invalid_file)

    def test_performance_monitoring_integration(self, performance_monitoring_services):
        """Test storage performance with monitoring services."""
        services = performance_monitoring_services
        storage_service = services["storage"]

        # Create test data for performance monitoring
        test_data = [SampleModel(name=f"monitor_{i}", value=i) for i in range(50)]

        # Use monitored storage service
        labels_file = Path(services["temp_dir"]) / "labels.json"
        start_time = time.time()
        storage_service.write(test_data, labels_file)
        operation_time = time.time() - start_time

        # Verify storage worked
        assert labels_file.exists()

        # Performance validation
        assert operation_time < 1.0, f"Storage operation took {operation_time:.3f}s"

        # Load and verify data integrity
        loaded_data = storage_service.read(labels_file, SampleModel)
        assert len(loaded_data) == 50
        assert loaded_data[0].name == "monitor_0"


@pytest.mark.storage
@pytest.mark.integration
@pytest.mark.medium
class TestJsonStorageValidation:
    """Test JSON storage data validation and integrity."""

    def test_data_integrity_validation(
        self, temp_data_dir, storage_service_for_temp_dir
    ):
        """Test data integrity validation with storage service."""
        storage_service = storage_service_for_temp_dir

        # Create test data with known values
        sample_labels = [
            SampleModel(name="test-label-1", value=1001),
            SampleModel(name="test-label-2", value=1002, active=False),
            SampleModel(name="test-label-3", value=1003),
        ]

        # Save using storage service
        labels_file = Path(temp_data_dir) / "test_labels.json"
        storage_service.write(sample_labels, labels_file)

        # Verify file was created
        assert labels_file.exists()

        # Load and validate data integrity
        loaded_data = storage_service.read(labels_file, SampleModel)
        assert len(loaded_data) == len(sample_labels)

        # Verify all data matches
        for original, loaded in zip(sample_labels, loaded_data):
            assert original.name == loaded.name
            assert original.value == loaded.value
            assert original.active == loaded.active

    def test_large_dataset_integrity(self, temp_data_dir):
        """Test data integrity with large datasets."""
        file_path = Path(temp_data_dir) / "large_integrity.json"

        # Create large dataset with known patterns
        large_data = [
            SampleModel(
                name=f"integrity_test_{i}",
                value=i * 7,  # Use multiplication for pattern verification
                active=(i % 3 == 0),  # Alternating pattern
            )
            for i in range(500)
        ]

        save_json_data(large_data, file_path)
        loaded_data = load_json_data(file_path, SampleModel)

        # Verify integrity
        assert len(loaded_data) == 500

        # Check specific patterns
        for i, item in enumerate(loaded_data):
            assert item.name == f"integrity_test_{i}"
            assert item.value == i * 7
            assert item.active == (i % 3 == 0)

    def test_unicode_data_integrity(self, temp_data_dir):
        """Test data integrity with Unicode characters."""
        file_path = Path(temp_data_dir) / "unicode.json"

        # Test data with various Unicode characters
        unicode_data = [
            SampleModel(name="English", value=1),
            SampleModel(name="Español", value=2),
            SampleModel(name="中文", value=3),
            SampleModel(name="العربية", value=4),
            SampleModel(name="🚀🌟", value=5),  # Emoji
            SampleModel(name="Ñoño niño", value=6),  # Accented characters
        ]

        save_json_data(unicode_data, file_path)
        loaded_data = load_json_data(file_path, SampleModel)

        # Verify Unicode integrity
        assert len(loaded_data) == 6

        expected_names = ["English", "Español", "中文", "العربية", "🚀🌟", "Ñoño niño"]
        for i, (expected_name, item) in enumerate(zip(expected_names, loaded_data)):
            assert item.name == expected_name
            assert item.value == i + 1

    def test_validation_with_malformed_json_recovery(self, temp_data_dir):
        """Test validation and recovery from malformed JSON scenarios."""
        file_path = Path(temp_data_dir) / "malformed.json"

        # Create valid data first
        valid_data = [SampleModel(name="valid", value=123)]
        save_json_data(valid_data, file_path)

        # Verify it loads correctly
        loaded = load_json_data(file_path, SampleModel)
        assert len(loaded) == 1
        assert loaded[0].name == "valid"

        # Now corrupt the file
        with open(file_path, "w") as f:
            f.write('{"name": "corrupted", "value": incomplete')

        # Should raise error for corrupted file
        with pytest.raises(json.JSONDecodeError):
            load_json_data(file_path, SampleModel)

        # Recovery: overwrite with new valid data
        recovery_data = [SampleModel(name="recovered", value=456)]
        save_json_data(recovery_data, file_path)

        # Verify recovery worked
        recovered = load_json_data(file_path, SampleModel)
        assert len(recovered) == 1
        assert recovered[0].name == "recovered"
        assert recovered[0].value == 456
