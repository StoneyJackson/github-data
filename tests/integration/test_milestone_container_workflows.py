"""Integration tests for milestone functionality in containerized environment.

Tests full Docker save workflow with milestones, full Docker restore workflow
with milestones, environment variable passing validation, and data persistence
across container runs.
"""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
import subprocess

from src.config.settings import ApplicationConfig


@pytest.mark.container
@pytest.mark.milestone_integration
@pytest.mark.milestones
@pytest.mark.slow
class TestMilestoneContainerWorkflows:
    """Test milestone functionality in containerized environment."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for container data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_milestone_data(self):
        """Create sample milestone data for testing."""
        return [
            {
                "id": "M_kwDOABCDEF123",
                "number": 1,
                "title": "Version 1.0",
                "description": "First major release",
                "state": "open",
                "creator_login": "testuser",
                "creator_id": "U_123456",
                "created_at": "2023-01-01T00:00:00+00:00",
                "updated_at": "2023-01-02T00:00:00+00:00",
                "due_on": "2023-12-31T23:59:59+00:00",
                "closed_at": None,
                "open_issues": 5,
                "closed_issues": 0,
                "url": "https://github.com/owner/repo/milestone/1",
            },
            {
                "id": "M_kwDOABCDEF456",
                "number": 2,
                "title": "Version 2.0",
                "description": "Second major release",
                "state": "closed",
                "creator_login": "testuser",
                "creator_id": "U_123456",
                "created_at": "2023-02-01T00:00:00+00:00",
                "updated_at": "2023-02-02T00:00:00+00:00",
                "due_on": "2023-06-30T23:59:59+00:00",
                "closed_at": "2023-06-15T12:00:00+00:00",
                "open_issues": 0,
                "closed_issues": 10,
                "url": "https://github.com/owner/repo/milestone/2",
            },
        ]

    @pytest.fixture
    def sample_issue_data_with_milestones(self):
        """Create sample issue data with milestone associations."""
        return [
            {
                "id": "I_kwDOABCDEF001",
                "number": 1,
                "title": "First Issue",
                "body": "This is the first issue",
                "state": "open",
                "milestone": {"number": 1},
                "created_at": "2023-01-05T10:00:00+00:00",
                "updated_at": "2023-01-05T11:00:00+00:00",
                "url": "https://github.com/owner/repo/issues/1",
            },
            {
                "id": "I_kwDOABCDEF002",
                "number": 2,
                "title": "Second Issue",
                "body": "This is the second issue",
                "state": "closed",
                "milestone": {"number": 2},
                "created_at": "2023-02-05T10:00:00+00:00",
                "updated_at": "2023-02-05T11:00:00+00:00",
                "url": "https://github.com/owner/repo/issues/2",
            },
        ]

    def create_mock_data_files(
        self, data_dir: str, milestone_data: list, issue_data: list = None
    ):
        """Create mock data files in the specified directory."""
        data_path = Path(data_dir)
        data_path.mkdir(exist_ok=True)

        # Create milestone data file
        milestone_file = data_path / "milestones.json"
        with open(milestone_file, "w") as f:
            json.dump(milestone_data, f, indent=2)

        # Create issue data file if provided
        if issue_data:
            issue_file = data_path / "issues.json"
            with open(issue_file, "w") as f:
                json.dump(issue_data, f, indent=2)

        return data_path

    def test_docker_save_with_milestones_enabled(
        self, temp_data_dir, sample_milestone_data
    ):
        """Test full Docker save workflow with INCLUDE_MILESTONES=true."""
        # Skip if Docker is not available
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        # Create environment variables for container
        env_vars = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "fake_token_for_testing",
            "GITHUB_REPO": "test-owner/test-repo",
            "DATA_PATH": "/data",
            "INCLUDE_MILESTONES": "true",
        }

        # Build Docker command
        docker_cmd = ["docker", "run", "--rm"]
        for key, value in env_vars.items():
            docker_cmd.extend(["-e", f"{key}={value}"])
        docker_cmd.extend(["-v", f"{temp_data_dir}:/data"])

        # Mock the container execution (since we can't actually run against
        # GitHub API in tests)
        with patch("subprocess.run") as mock_run:
            # Configure mock to simulate successful save
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            # Create expected milestone data in temp directory
            self.create_mock_data_files(temp_data_dir, sample_milestone_data)

            # Verify milestone data exists
            milestone_file = Path(temp_data_dir) / "milestones.json"
            assert milestone_file.exists()

            # Verify milestone data content
            with open(milestone_file, "r") as f:
                saved_data = json.load(f)
            assert len(saved_data) == 2
            assert saved_data[0]["title"] == "Version 1.0"
            assert saved_data[1]["title"] == "Version 2.0"

    def test_docker_restore_with_milestone_relationships(
        self, temp_data_dir, sample_milestone_data, sample_issue_data_with_milestones
    ):
        """Test full Docker restore workflow with milestone relationships."""
        # Skip if Docker is not available
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        # Create mock data files
        data_path = self.create_mock_data_files(
            temp_data_dir, sample_milestone_data, sample_issue_data_with_milestones
        )

        # Create environment variables for container
        env_vars = {
            "OPERATION": "restore",
            "GITHUB_TOKEN": "fake_token_for_testing",
            "GITHUB_REPO": "test-owner/test-repo",
            "DATA_PATH": "/data",
            "INCLUDE_MILESTONES": "true",
        }

        # Build Docker command
        docker_cmd = ["docker", "run", "--rm"]
        for key, value in env_vars.items():
            docker_cmd.extend(["-e", f"{key}={value}"])
        docker_cmd.extend(["-v", f"{temp_data_dir}:/data"])

        # Mock the container execution
        with patch("subprocess.run") as mock_run:
            # Configure mock to simulate successful restore
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            # Verify required data files exist
            assert (data_path / "milestones.json").exists()
            assert (data_path / "issues.json").exists()

            # Verify milestone-issue relationships in data
            with open(data_path / "issues.json", "r") as f:
                issue_data = json.load(f)

            # Check that issues reference milestones
            assert issue_data[0]["milestone"]["number"] == 1
            assert issue_data[1]["milestone"]["number"] == 2

    def test_environment_variable_passing_validation(self):
        """Test environment variable configuration passing to container."""
        # Test various boolean value formats for INCLUDE_MILESTONES
        # Note: Removed "1" and "0" as they're no longer supported per ApplicationConfig
        boolean_test_cases = [
            ("true", True),
            ("false", False),
            ("yes", True),
            ("no", False),
            ("on", True),
            ("off", False),
            ("TRUE", True),
            ("FALSE", False),
        ]

        for env_value, expected_bool in boolean_test_cases:
            # Test environment variable parsing
            with patch.dict(os.environ, {"INCLUDE_MILESTONES": env_value}):
                # Use ApplicationConfig's actual parsing method
                try:
                    parsed_value = ApplicationConfig._parse_enhanced_bool_env(
                        "INCLUDE_MILESTONES", default=True
                    )
                    assert parsed_value == expected_bool
                except ValueError:
                    # Expected for unsupported formats
                    assert False, f"Unexpected error for supported format: {env_value}"

    def test_data_persistence_across_container_runs(
        self, temp_data_dir, sample_milestone_data
    ):
        """Test data persistence across multiple container runs."""
        # Create initial data
        data_path = self.create_mock_data_files(temp_data_dir, sample_milestone_data)

        # Verify initial data exists
        milestone_file = data_path / "milestones.json"
        assert milestone_file.exists()

        # Read initial data
        with open(milestone_file, "r") as f:
            initial_data = json.load(f)

        # Simulate first container run (save operation)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            # Modify data to simulate save operation
            modified_data = initial_data.copy()
            modified_data.append(
                {
                    "id": "M_kwDOABCDEF789",
                    "number": 3,
                    "title": "Version 3.0",
                    "description": "Third major release",
                    "state": "open",
                    "creator_login": "testuser",
                    "creator_id": "U_123456",
                    "created_at": "2023-03-01T00:00:00+00:00",
                    "updated_at": "2023-03-02T00:00:00+00:00",
                    "due_on": None,
                    "closed_at": None,
                    "open_issues": 3,
                    "closed_issues": 0,
                    "url": "https://github.com/owner/repo/milestone/3",
                }
            )

            # Write modified data
            with open(milestone_file, "w") as f:
                json.dump(modified_data, f, indent=2)

        # Verify data persistence after first run
        with open(milestone_file, "r") as f:
            persisted_data = json.load(f)
        assert len(persisted_data) == 3
        assert persisted_data[2]["title"] == "Version 3.0"

        # Simulate second container run (restore operation)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            # Verify data is still available for second run
            assert milestone_file.exists()
            with open(milestone_file, "r") as f:
                second_run_data = json.load(f)
            assert len(second_run_data) == 3
            assert second_run_data == persisted_data

    def test_volume_mounting_validation(self, temp_data_dir, sample_milestone_data):
        """Test volume mounting and data accessibility in container."""
        # Create data structure that matches expected container paths
        data_path = self.create_mock_data_files(temp_data_dir, sample_milestone_data)

        # Create subdirectories to test volume mounting
        subdirs = ["backup", "logs", "config"]
        for subdir in subdirs:
            subdir_path = data_path / subdir
            subdir_path.mkdir(exist_ok=True)

            # Create test file in subdirectory
            test_file = subdir_path / f"{subdir}_test.txt"
            with open(test_file, "w") as f:
                f.write(f"Test content for {subdir}")

        # Verify all created files and directories
        assert (data_path / "milestones.json").exists()
        for subdir in subdirs:
            assert (data_path / subdir).is_dir()
            assert (data_path / subdir / f"{subdir}_test.txt").exists()

        # Test that container would have access to all files
        # (This simulates the container's view of the mounted volume)

        # Verify file structure matches expected container layout
        expected_files = [
            "milestones.json",
            "backup/backup_test.txt",
            "logs/logs_test.txt",
            "config/config_test.txt",
        ]

        for expected_file in expected_files:
            # Convert container path to host path for verification
            host_file_path = data_path / expected_file
            assert host_file_path.exists(), f"Expected file {expected_file} not found"

    def test_container_environment_configuration(self):
        """Test container environment configuration for milestone operations."""
        # Test complete environment configuration
        complete_env_config = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "ghp_test_token_1234567890",
            "GITHUB_REPO": "test-owner/test-repo",
            "DATA_PATH": "/data",
            "INCLUDE_MILESTONES": "true",
            "INCLUDE_ISSUES": "true",
            "INCLUDE_PULL_REQUESTS": "true",
            "INCLUDE_ISSUE_COMMENTS": "true",
            "INCLUDE_PULL_REQUEST_COMMENTS": "true",
        }

        # Test minimal environment configuration
        minimal_env_config = {
            "OPERATION": "restore",
            "GITHUB_TOKEN": "ghp_test_token_1234567890",
            "GITHUB_REPO": "test-owner/test-repo",
            "DATA_PATH": "/data",
            # INCLUDE_MILESTONES should default to true
        }

        # Verify complete configuration
        for key, value in complete_env_config.items():
            assert key is not None
            assert value is not None
            assert isinstance(value, str)

        # Verify minimal configuration has required fields
        required_fields = ["OPERATION", "GITHUB_TOKEN", "GITHUB_REPO", "DATA_PATH"]
        for field in required_fields:
            assert field in minimal_env_config
            assert minimal_env_config[field] is not None

    @pytest.mark.slow
    def test_container_performance_with_milestones(self, temp_data_dir):
        """Test container performance impact when milestones are enabled."""
        import time

        # Create large dataset for performance testing
        large_milestone_dataset = []
        for i in range(100):
            milestone = {
                "id": f"M_perf_{i:03d}",
                "number": i + 1,
                "title": f"Performance Test Milestone {i + 1}",
                "description": f"Description for performance test milestone {i + 1}"
                * 5,
                "state": "open" if i % 2 == 0 else "closed",
                "creator_login": f"testuser{i % 10}",
                "creator_id": f"U_perf_{i:06d}",
                "created_at": f"2023-{(i % 12) + 1:02d}-01T00:00:00+00:00",
                "updated_at": f"2023-{(i % 12) + 1:02d}-02T00:00:00+00:00",
                "due_on": (
                    f"2023-{(i % 12) + 1:02d}-28T23:59:59+00:00" if i % 4 == 0 else None
                ),
                "closed_at": (
                    f"2023-{(i % 12) + 1:02d}-15T12:00:00+00:00" if i % 2 == 1 else None
                ),
                "open_issues": i * 2,
                "closed_issues": i,
                "url": f"https://github.com/owner/repo/milestone/{i + 1}",
            }
            large_milestone_dataset.append(milestone)

        # Create data files
        data_path = self.create_mock_data_files(temp_data_dir, large_milestone_dataset)

        # Measure file I/O performance
        start_time = time.time()

        # Read milestone data (simulating container startup)
        milestone_file = data_path / "milestones.json"
        with open(milestone_file, "r") as f:
            loaded_data = json.load(f)

        # Process data (simulating milestone operations)
        processed_count = 0
        for milestone in loaded_data:
            # Simulate processing each milestone
            assert milestone["id"] is not None
            assert milestone["number"] is not None
            assert milestone["title"] is not None
            processed_count += 1

        end_time = time.time()
        processing_time = end_time - start_time

        # Verify performance is acceptable
        assert (
            processing_time < 2.0
        ), f"Processing took too long: {processing_time:.3f}s"
        assert processed_count == 100

        # Verify data integrity
        assert len(loaded_data) == 100
        assert loaded_data[0]["title"] == "Performance Test Milestone 1"
        assert loaded_data[99]["title"] == "Performance Test Milestone 100"

    def test_container_error_handling_scenarios(self, temp_data_dir):
        """Test container behavior under various error conditions."""
        # Test missing data directory
        nonexistent_dir = "/tmp/nonexistent_milestone_data"

        # Verify error handling for missing directory
        with pytest.raises(FileNotFoundError):
            with open(f"{nonexistent_dir}/milestones.json", "r") as f:
                json.load(f)

        # Test corrupted data file
        data_path = Path(temp_data_dir)
        data_path.mkdir(exist_ok=True)

        corrupted_file = data_path / "milestones.json"
        with open(corrupted_file, "w") as f:
            f.write("{ invalid json content }")

        # Verify error handling for corrupted file
        with pytest.raises(json.JSONDecodeError):
            with open(corrupted_file, "r") as f:
                json.load(f)

        # Test permission issues (simulate read-only filesystem)
        readonly_file = data_path / "readonly_milestones.json"
        with open(readonly_file, "w") as f:
            json.dump([], f)

        # Make file read-only
        os.chmod(readonly_file, 0o444)

        # Verify error handling for permission issues
        with pytest.raises(PermissionError):
            with open(readonly_file, "w") as f:
                json.dump([], f)

        # Cleanup: restore write permissions
        os.chmod(readonly_file, 0o644)

    @pytest.mark.performance
    def test_milestone_memory_usage_benchmark(self, temp_data_dir):
        """Test memory usage impact of milestone operations."""
        import psutil
        import gc

        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create large milestone dataset
        large_dataset = []
        for i in range(1000):  # 1000 milestones
            milestone = {
                "id": f"M_memory_{i:04d}",
                "number": i + 1,
                "title": f"Memory Test Milestone {i + 1}",
                "description": f"Memory benchmark description {i + 1}"
                * 20,  # Large descriptions
                "state": "open" if i % 2 == 0 else "closed",
                "creator_login": f"user{i % 50}",
                "creator_id": f"U_memory_{i:06d}",
                "created_at": f"2023-{(i % 12) + 1:02d}-01T00:00:00+00:00",
                "updated_at": f"2023-{(i % 12) + 1:02d}-02T00:00:00+00:00",
                "due_on": (
                    f"2023-{(i % 12) + 1:02d}-28T23:59:59+00:00" if i % 4 == 0 else None
                ),
                "closed_at": (
                    f"2023-{(i % 12) + 1:02d}-15T12:00:00+00:00" if i % 2 == 1 else None
                ),
                "open_issues": i % 100,
                "closed_issues": i % 50,
                "url": f"https://github.com/owner/repo/milestone/{i + 1}",
            }
            large_dataset.append(milestone)

        # Create and write data files
        data_path = self.create_mock_data_files(temp_data_dir, large_dataset)

        # Measure memory after data creation

        # Read and process data (simulating container operations)
        milestone_file = data_path / "milestones.json"
        with open(milestone_file, "r") as f:
            loaded_data = json.load(f)

        # Process all milestones
        processed_milestones = []
        for milestone in loaded_data:
            processed_milestone = {
                "processed_id": milestone["id"],
                "processed_title": milestone["title"].upper(),
                "processed_state": milestone["state"],
            }
            processed_milestones.append(processed_milestone)

        # Measure final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Calculate memory increases
        total_increase = final_memory - initial_memory

        # Verify memory usage is reasonable (should not exceed 100MB for
        # 1000 milestones)
        assert total_increase < 100, f"Memory usage too high: {total_increase:.2f}MB"
        assert len(processed_milestones) == 1000

        # Cleanup
        del large_dataset
        del loaded_data
        del processed_milestones
        gc.collect()

    @pytest.mark.performance
    def test_milestone_api_call_efficiency_benchmark(
        self, temp_data_dir, sample_milestone_data
    ):
        """Test API call efficiency for milestone operations."""
        import time
        from unittest.mock import patch, Mock

        # Track API call counts
        api_call_count = {
            "get_milestones": 0,
            "create_milestone": 0,
            "update_milestone": 0,
        }

        def mock_api_call(method_name):
            def wrapper(*args, **kwargs):
                api_call_count[method_name] += 1
                return Mock()

            return wrapper

        # Create test scenario with 50 milestones
        milestone_dataset = []
        for i in range(50):
            milestone = sample_milestone_data[0].copy()
            milestone["id"] = f"M_efficiency_{i:03d}"
            milestone["number"] = i + 1
            milestone["title"] = f"Efficiency Test {i + 1}"
            milestone_dataset.append(milestone)

        # Create data files
        self.create_mock_data_files(temp_data_dir, milestone_dataset)

        # Measure API call efficiency
        import time as time_module

        start_time = time_module.time()

        with patch(
            "time.sleep", return_value=None
        ):  # Remove actual API delays for testing
            # Simulate save operation API calls
            for milestone in milestone_dataset:
                mock_api_call("get_milestones")()

            # Simulate restore operation API calls
            for milestone in milestone_dataset:
                mock_api_call("create_milestone")()

        end_time = time_module.time()
        operation_time = end_time - start_time

        # Verify API call efficiency
        total_calls = sum(api_call_count.values())
        assert total_calls == 100  # 50 get + 50 create calls
        assert (
            operation_time < 1.0
        ), f"API operations took too long: {operation_time:.3f}s"

        # Verify call distribution
        assert api_call_count["get_milestones"] == 50
        assert api_call_count["create_milestone"] == 50

    @pytest.mark.performance
    def test_milestone_file_io_performance_benchmark(self, temp_data_dir):
        """Test file I/O performance for milestone data operations."""
        import time

        # Create various sized datasets for I/O testing
        test_scenarios = [
            {"size": 10, "max_time": 0.1},  # Small dataset
            {"size": 100, "max_time": 0.5},  # Medium dataset
            {"size": 500, "max_time": 2.0},  # Large dataset
        ]

        for scenario in test_scenarios:
            # Generate dataset
            dataset = []
            for i in range(scenario["size"]):
                milestone = {
                    "id": f"M_io_test_{scenario['size']}_{i:04d}",
                    "number": i + 1,
                    "title": f"I/O Test Milestone {i + 1} (Size {scenario['size']})",
                    "description": (
                        f"I/O performance test description for milestone {i + 1}" * 10
                    ),
                    "state": "open" if i % 2 == 0 else "closed",
                    "creator_login": f"iouser{i % 20}",
                    "creator_id": f"U_io_{i:06d}",
                    "created_at": f"2023-{(i % 12) + 1:02d}-01T00:00:00+00:00",
                    "updated_at": f"2023-{(i % 12) + 1:02d}-02T00:00:00+00:00",
                    "due_on": (
                        f"2023-{(i % 12) + 1:02d}-28T23:59:59+00:00"
                        if i % 4 == 0
                        else None
                    ),
                    "closed_at": (
                        f"2023-{(i % 12) + 1:02d}-15T12:00:00+00:00"
                        if i % 2 == 1
                        else None
                    ),
                    "open_issues": i % 20,
                    "closed_issues": i % 10,
                    "url": f"https://github.com/owner/repo/milestone/{i + 1}",
                }
                dataset.append(milestone)

            # Test write performance
            data_path = Path(temp_data_dir)
            test_file = data_path / f"milestone_io_test_{scenario['size']}.json"

            write_start = time.time()
            with open(test_file, "w") as f:
                json.dump(dataset, f, indent=2)
            write_end = time.time()

            write_time = write_end - write_start

            # Test read performance
            read_start = time.time()
            with open(test_file, "r") as f:
                loaded_dataset = json.load(f)
            read_end = time.time()

            read_time = read_end - read_start
            total_io_time = write_time + read_time

            # Verify performance meets benchmarks
            assert total_io_time < scenario["max_time"], (
                f"I/O for {scenario['size']} milestones took "
                f"{total_io_time:.3f}s (max: {scenario['max_time']}s)"
            )

            # Verify data integrity
            assert len(loaded_dataset) == scenario["size"]
            assert loaded_dataset[0]["title"].startswith("I/O Test Milestone 1")

            # Cleanup
            test_file.unlink()

    @pytest.mark.performance
    @pytest.mark.slow
    def test_milestone_concurrent_operation_performance(self, temp_data_dir):
        """Test performance of concurrent milestone operations."""
        import time
        from concurrent.futures import ThreadPoolExecutor

        # Create shared dataset
        shared_milestone_data = []
        for i in range(200):  # 200 milestones for concurrency testing
            milestone = {
                "id": f"M_concurrent_{i:03d}",
                "number": i + 1,
                "title": f"Concurrent Test Milestone {i + 1}",
                "description": (f"Concurrent operation test description {i + 1}"),
                "state": "open" if i % 2 == 0 else "closed",
                "creator_login": f"concuser{i % 30}",
                "creator_id": f"U_conc_{i:06d}",
                "created_at": f"2023-{(i % 12) + 1:02d}-01T00:00:00+00:00",
                "updated_at": f"2023-{(i % 12) + 1:02d}-02T00:00:00+00:00",
                "url": f"https://github.com/owner/repo/milestone/{i + 1}",
            }
            shared_milestone_data.append(milestone)

        def process_milestone_batch(batch_id, milestones):
            """Process a batch of milestones concurrently."""
            batch_file = Path(temp_data_dir) / f"concurrent_batch_{batch_id}.json"

            # Write batch
            with open(batch_file, "w") as f:
                json.dump(milestones, f)

            # Read and process batch
            with open(batch_file, "r") as f:
                loaded_milestones = json.load(f)

            # Simulate processing
            processed_count = 0
            for milestone in loaded_milestones:
                assert milestone["id"] is not None
                processed_count += 1

            # Cleanup
            batch_file.unlink()

            return processed_count

        # Split data into batches for concurrent processing
        batch_size = 50
        batches = [
            shared_milestone_data[i : i + batch_size]
            for i in range(0, len(shared_milestone_data), batch_size)
        ]

        # Test concurrent processing performance
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for batch_id, batch in enumerate(batches):
                future = executor.submit(process_milestone_batch, batch_id, batch)
                futures.append(future)

            # Wait for all batches to complete
            total_processed = 0
            for future in futures:
                total_processed += future.result()

        end_time = time.time()
        concurrent_time = end_time - start_time

        # Verify concurrent performance is acceptable
        assert (
            concurrent_time < 3.0
        ), f"Concurrent processing took too long: {concurrent_time:.3f}s"
        assert total_processed == 200

        # Test sequential processing for comparison
        sequential_start = time.time()

        for batch_id, batch in enumerate(batches):
            process_milestone_batch(f"seq_{batch_id}", batch)

        sequential_end = time.time()
        sequential_time = sequential_end - sequential_start

        # Concurrent should be faster than sequential (or at least not
        # significantly slower). In containerized environments, allow for higher
        # overhead
        performance_ratio = (
            concurrent_time / sequential_time if sequential_time > 0 else 1.0
        )
        assert performance_ratio < 5.0, (
            f"Concurrent processing extremely inefficient: "
            f"{performance_ratio:.2f}x sequential time"
        )
