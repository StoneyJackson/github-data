"""Container integration tests for Docker workflow."""

import errno

import os
import shutil
import stat
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

import pytest

pytestmark = [
    pytest.mark.container,
    pytest.mark.integration,
    pytest.mark.docker,
    pytest.mark.slow,
]


class DockerTestHelper:
    """Helper class for Docker integration testing."""

    IMAGE_NAME = "github-data-test"
    CONTAINER_PREFIX = "github-data-test-"

    @staticmethod
    def build_image(dockerfile_path: str = ".", tag: Optional[str] = None) -> str:
        """Build Docker image and return the tag."""
        image_tag = tag or DockerTestHelper.IMAGE_NAME
        cmd = ["docker", "build", "-t", image_tag, dockerfile_path]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Docker build failed: {result.stderr}")

        return image_tag

    @staticmethod
    def run_container(
        image_tag: str,
        environment: Dict[str, str],
        volumes: Dict[str, str],
        command: Optional[List[str]] = None,
        detach: bool = False,
        name: Optional[str] = None,
    ) -> subprocess.CompletedProcess:
        """Run Docker container with specified configuration."""
        cmd = ["docker", "run", "--rm"]

        if name:
            cmd.extend(["--name", name])

        if detach:
            cmd.append("-d")

        # Add environment variables
        for key, value in environment.items():
            cmd.extend(["-e", f"{key}={value}"])

        # Add volume mounts
        for host_path, container_path in volumes.items():
            cmd.extend(["-v", f"{host_path}:{container_path}"])

        cmd.append(image_tag)

        if command:
            cmd.extend(command)

        return subprocess.run(cmd, capture_output=True, text=True)

    @staticmethod
    def cleanup_containers() -> None:
        """Clean up test containers."""
        # List containers with our prefix
        cmd = [
            "docker",
            "ps",
            "-a",
            "--filter",
            f"name={DockerTestHelper.CONTAINER_PREFIX}",
            "-q",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        container_ids = result.stdout.strip().split("\n")
        if container_ids and container_ids[0]:  # Check if any containers exist
            subprocess.run(["docker", "rm", "-f"] + container_ids, capture_output=True)

    @staticmethod
    def cleanup_images() -> None:
        """Clean up test images."""
        subprocess.run(
            ["docker", "rmi", "-f", DockerTestHelper.IMAGE_NAME], capture_output=True
        )


class TestDockerBuild:
    """Tests for Docker image building."""

    def teardown_method(self):
        """Clean up after each test."""
        DockerTestHelper.cleanup_containers()
        DockerTestHelper.cleanup_images()

    def test_dockerfile_builds_successfully(self):
        """Test that Dockerfile builds without errors."""
        image_tag = DockerTestHelper.build_image()
        assert image_tag == DockerTestHelper.IMAGE_NAME

        # Verify image exists
        cmd = ["docker", "images", "-q", DockerTestHelper.IMAGE_NAME]
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.stdout.strip(), "Docker image should exist after build"

    def test_built_image_has_correct_structure(self):
        """Test that built image has the expected file structure."""
        image_tag = DockerTestHelper.build_image()

        # Run container to inspect structure
        cmd = ["ls", "-la", "/app"]
        result = DockerTestHelper.run_container(
            image_tag, environment={}, volumes={}, command=cmd
        )

        assert result.returncode == 0, f"Container inspection failed: {result.stderr}"
        output = result.stdout

        # Check for expected files/directories
        assert "src" in output, "Source directory should be present"
        assert "pyproject.toml" in output, "pyproject.toml should be present"

    def test_built_image_has_python_dependencies(self):
        """Test that built image has required Python dependencies installed."""
        image_tag = DockerTestHelper.build_image()

        # Check if PyGithub is installed
        cmd = [
            "pdm",
            "run",
            "python",
            "-c",
            "import github; print('PyGithub installed')",
        ]
        result = DockerTestHelper.run_container(
            image_tag, environment={}, volumes={}, command=cmd
        )

        assert result.returncode == 0, f"Dependency check failed: {result.stderr}"
        assert "PyGithub installed" in result.stdout

    def test_docker_build_uses_pdm_correctly(self):
        """Test that Docker build properly uses PDM for dependency management."""
        image_tag = DockerTestHelper.build_image()

        # Verify PDM is available and project is set up
        cmd = ["pdm", "info"]
        result = DockerTestHelper.run_container(
            image_tag, environment={}, volumes={}, command=cmd
        )

        assert result.returncode == 0, f"PDM info failed: {result.stderr}"
        # Verify PDM is working by checking for project root
        assert "project root" in result.stdout.lower()
        assert "/app" in result.stdout.lower()


class TestDockerRun:
    """Tests for Docker container runtime functionality."""

    @pytest.fixture
    def docker_image(self):
        """Build Docker image for tests."""
        yield DockerTestHelper.build_image()
        DockerTestHelper.cleanup_containers()
        DockerTestHelper.cleanup_images()

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for container data."""
        temp_dir = tempfile.mkdtemp()
        try:
            yield temp_dir
        finally:
            # Fix permissions before cleanup (Docker containers create files as root)
            def handle_remove_readonly(func, path, exc):
                """Handle removal of readonly files created by Docker containers."""
                if exc[1].errno == errno.EACCES:
                    os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                    func(path)
                else:
                    raise

            try:
                shutil.rmtree(temp_dir, onerror=handle_remove_readonly)
            except Exception:
                # Fallback: use sudo to clean up if needed
                try:
                    subprocess.run(
                        ["sudo", "rm", "-rf", temp_dir], capture_output=True, check=True
                    )
                except Exception:
                    # If all else fails, just warn and continue
                    import warnings

                    warnings.warn(f"Could not clean up temp directory: {temp_dir}")

    def test_container_runs_with_environment_variables(
        self, docker_image, temp_data_dir
    ):
        """Test that container accepts and uses environment variables."""
        environment = {
            "GITHUB_TOKEN": "fake_token_12345",
            "GITHUB_REPO": "owner/test-repo",
            "OPERATION": "save",
            "DATA_PATH": "/data",
        }
        volumes = {temp_data_dir: "/data"}

        result = DockerTestHelper.run_container(
            docker_image, environment=environment, volumes=volumes
        )

        # Container should run (even if it fails due to fake token)
        assert result.returncode in [0, 1], f"Container failed to run: {result.stderr}"

    def test_container_creates_data_directory_structure(
        self, docker_image, temp_data_dir
    ):
        """Test that container can write to mounted data directory."""
        environment = {
            "GITHUB_TOKEN": "fake_token",
            "GITHUB_REPO": "owner/repo",
            "DATA_PATH": "/data",
        }
        volumes = {temp_data_dir: "/data"}

        # Run container that creates a test file
        cmd = [
            "sh",
            "-c",
            "mkdir -p /data/test && echo 'test data' > /data/test/file.txt",
        ]
        result = DockerTestHelper.run_container(
            docker_image, environment=environment, volumes=volumes, command=cmd
        )

        assert (
            result.returncode == 0
        ), f"Data directory creation failed: {result.stderr}"

        # Verify file was created on host
        test_file = Path(temp_data_dir) / "test" / "file.txt"
        assert test_file.exists(), "Test file should be created in mounted volume"
        assert test_file.read_text().strip() == "test data"

    def test_container_handles_missing_environment_variables(
        self, docker_image, temp_data_dir
    ):
        """Test container behavior with missing required environment variables."""
        # Run without required environment variables
        volumes = {temp_data_dir: "/data"}

        result = DockerTestHelper.run_container(
            docker_image, environment={}, volumes=volumes
        )

        # Should fail gracefully, not crash
        assert (
            result.returncode != 0
        ), "Container should fail with missing environment variables"
        # Should have meaningful error message
        error_output = result.stderr.lower()
        assert any(
            word in error_output for word in ["token", "repo", "environment", "missing"]
        )

    def test_container_python_path_configuration(self, docker_image, temp_data_dir):
        """Test that container has correct Python path configuration."""
        cmd = ["pdm", "run", "python", "-c", "import sys; print('\\n'.join(sys.path))"]
        result = DockerTestHelper.run_container(
            docker_image, environment={}, volumes={}, command=cmd
        )

        assert result.returncode == 0, f"Python path check failed: {result.stderr}"
        assert "/app" in result.stdout, "App directory should be in Python path"

    def test_container_working_directory(self, docker_image):
        """Test that container sets correct working directory."""
        cmd = ["pwd"]
        result = DockerTestHelper.run_container(
            docker_image, environment={}, volumes={}, command=cmd
        )

        assert result.returncode == 0
        assert result.stdout.strip() == "/app", "Working directory should be /app"


class TestDockerWorkflow:
    """Tests for end-to-end Docker workflow scenarios."""

    @pytest.fixture
    def docker_image(self):
        """Build Docker image for tests."""
        yield DockerTestHelper.build_image()
        DockerTestHelper.cleanup_containers()
        DockerTestHelper.cleanup_images()

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for container data."""
        temp_dir = tempfile.mkdtemp()
        try:
            yield temp_dir
        finally:
            # Fix permissions before cleanup (Docker containers create files as root)
            def handle_remove_readonly(func, path, exc):
                """Handle removal of readonly files created by Docker containers."""
                if exc[1].errno == errno.EACCES:
                    os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                    func(path)
                else:
                    raise

            try:
                shutil.rmtree(temp_dir, onerror=handle_remove_readonly)
            except Exception:
                # Fallback: use sudo to clean up if needed
                try:
                    subprocess.run(
                        ["sudo", "rm", "-rf", temp_dir], capture_output=True, check=True
                    )
                except Exception:
                    # If all else fails, just warn and continue
                    import warnings

                    warnings.warn(f"Could not clean up temp directory: {temp_dir}")

    def test_makefile_docker_build_command_works(self):
        """Test that Makefile docker-build target works correctly."""
        # Run make docker-build
        result = subprocess.run(
            ["make", "docker-build"], cwd=".", capture_output=True, text=True
        )

        assert result.returncode == 0, f"Make docker-build failed: {result.stderr}"

        # Verify image was created
        cmd = ["docker", "images", "-q", "github-data"]
        verify_result = subprocess.run(cmd, capture_output=True, text=True)
        assert (
            verify_result.stdout.strip()
        ), "Docker image should exist after make build"

        # Cleanup
        subprocess.run(["docker", "rmi", "-f", "github-data"], capture_output=True)

    def test_container_handles_volume_permissions(self, docker_image, temp_data_dir):
        """Test that container handles volume mount permissions correctly."""
        # Create a directory structure that the container should be able to write to
        test_subdir = Path(temp_data_dir) / "backup"
        test_subdir.mkdir(parents=True, exist_ok=True)

        environment = {"DATA_PATH": "/data"}
        volumes = {temp_data_dir: "/data"}

        # Test writing to subdirectory
        cmd = [
            "sh",
            "-c",
            "echo 'permission test' > /data/backup/test.txt && "
            "cat /data/backup/test.txt",
        ]
        result = DockerTestHelper.run_container(
            docker_image, environment=environment, volumes=volumes, command=cmd
        )

        assert result.returncode == 0, f"Permission test failed: {result.stderr}"
        assert "permission test" in result.stdout

        # Verify file exists on host
        test_file = test_subdir / "test.txt"
        assert test_file.exists()

    def test_container_env_var_substitution_in_makefile_commands(self, temp_data_dir):
        """Test that Makefile commands work with environment variable substitution."""
        # Set up environment for makefile
        env = os.environ.copy()
        env.update(
            {"GITHUB_TOKEN": "fake_token_for_test", "GITHUB_REPO": "owner/test-repo"}
        )

        # Build image first
        build_result = subprocess.run(
            ["make", "docker-build"], capture_output=True, text=True
        )
        assert build_result.returncode == 0, "Failed to build Docker image"

        try:
            # Test make command (this will fail due to fake token, but should run)
            result = subprocess.run(
                ["make", "docker-run-save"],
                cwd=".",
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Command should execute (may fail due to fake token, but should not crash)
            assert result.returncode in [
                0,
                1,
                2,
            ], f"Make command failed unexpectedly: {result.stderr}"

        finally:
            # Cleanup
            subprocess.run(["docker", "rmi", "-f", "github-data"], capture_output=True)

    def test_container_resource_limits_and_cleanup(self, docker_image, temp_data_dir):
        """Test container resource usage and cleanup behavior."""
        # Resource limits test - variables not used in this specific test
        # environment = {"DATA_PATH": "/data"}
        # volumes = {temp_data_dir: "/data"}

        # Run container with resource limits
        cmd = [
            "docker",
            "run",
            "--rm",
            "--memory=256m",  # Limit memory
            "--cpus=0.5",  # Limit CPU
            "-e",
            "DATA_PATH=/data",
            "-v",
            f"{temp_data_dir}:/data",
            docker_image,
            "sh",
            "-c",
            "echo 'Resource test completed'",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        assert (
            result.returncode == 0
        ), f"Resource limited container failed: {result.stderr}"
        assert "Resource test completed" in result.stdout

    def test_container_exit_codes_and_error_handling(self, docker_image, temp_data_dir):
        """Test container returns appropriate exit codes for different
        scenarios."""
        volumes = {temp_data_dir: "/data"}

        # Test successful operation (with fake token, will fail auth but
        # code should handle it)
        environment = {
            "GITHUB_TOKEN": "fake_token",
            "GITHUB_REPO": "owner/repo",
            "DATA_PATH": "/data",
        }

        result = DockerTestHelper.run_container(
            docker_image, environment=environment, volumes=volumes
        )

        # Should exit with non-zero code due to fake token, but not crash
        assert result.returncode != 0, "Should fail with fake credentials"

        # Test with completely missing required args
        result2 = DockerTestHelper.run_container(
            docker_image, environment={}, volumes=volumes
        )

        assert result2.returncode != 0, "Should fail with missing environment variables"


class TestDockerPerformance:
    """Performance and efficiency tests for Docker workflow."""

    @pytest.fixture
    def docker_image(self):
        """Build Docker image for tests."""
        yield DockerTestHelper.build_image()
        DockerTestHelper.cleanup_containers()
        DockerTestHelper.cleanup_images()

    def test_docker_build_speed_is_reasonable(self):
        """Test that Docker build completes within reasonable time."""
        start_time = time.time()

        try:
            DockerTestHelper.build_image()
            build_time = time.time() - start_time

            # Build should complete within 5 minutes for this simple image
            assert (
                build_time < 300
            ), f"Docker build took too long: {build_time:.2f} seconds"

        finally:
            DockerTestHelper.cleanup_images()

    def test_container_startup_time(self, docker_image):
        """Test that container starts up quickly."""
        start_time = time.time()

        result = DockerTestHelper.run_container(
            docker_image, environment={}, volumes={}, command=["echo", "startup test"]
        )

        startup_time = time.time() - start_time

        assert result.returncode == 0
        assert (
            startup_time < 10
        ), f"Container startup too slow: {startup_time:.2f} seconds"

    def test_docker_image_size_is_reasonable(self, docker_image):
        """Test that Docker image size is not excessive."""
        # Get image size
        cmd = ["docker", "images", "--format", "{{.Size}}", docker_image]
        result = subprocess.run(cmd, capture_output=True, text=True)

        assert result.returncode == 0
        size_str = result.stdout.strip()

        # Extract numeric value (assumes format like "123MB" or "1.2GB")
        import re

        size_match = re.match(r"(\d+(?:\.\d+)?)([KMGT]B)", size_str)
        assert size_match, f"Could not parse image size: {size_str}"

        size_value = float(size_match.group(1))
        size_unit = size_match.group(2)

        # Convert to MB for comparison
        if size_unit == "GB":
            size_mb = size_value * 1024
        elif size_unit == "TB":
            size_mb = size_value * 1024 * 1024
        else:  # MB, KB
            size_mb = size_value if size_unit == "MB" else size_value / 1024

        # Image should be reasonably sized (less than 1GB for this simple Python app)
        assert size_mb < 1024, f"Docker image too large: {size_str}"
