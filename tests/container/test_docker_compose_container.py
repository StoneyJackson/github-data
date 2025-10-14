"""Docker Compose integration tests."""

import os
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.container,
    pytest.mark.integration,
    pytest.mark.slow,
]


class DockerComposeTestHelper:
    """Helper class for Docker Compose integration testing."""

    COMPOSE_FILE = "docker-compose.test.yml"
    PROJECT_NAME = "github-data-test"

    @staticmethod
    def run_compose_command(
        command: str,
        services: list = None,
        environment: dict = None,
        capture_output: bool = True,
        timeout: int = 60,
        profiles: list = None,
    ) -> subprocess.CompletedProcess:
        """Run docker-compose command with test configuration."""
        cmd = [
            "docker",
            "compose",
            "-f",
            DockerComposeTestHelper.COMPOSE_FILE,
            "-p",
            DockerComposeTestHelper.PROJECT_NAME,
        ]

        # Check if services parameter contains profile arguments
        if services and len(services) >= 2 and services[0] == "--profile":
            # Handle explicit profile in services parameter
            cmd.extend(services)  # Add the --profile arguments directly
        else:
            # Add default profile flags if no explicit profile specified
            active_profiles = profiles or ["test"]
            for profile in active_profiles:
                cmd.extend(["--profile", profile])

        cmd.append(command)

        # Add remaining services if they're not profile arguments
        if services and not (len(services) >= 2 and services[0] == "--profile"):
            cmd.extend(services)

        env = os.environ.copy()
        if environment:
            env.update(environment)

        return subprocess.run(
            cmd, capture_output=capture_output, text=True, env=env, timeout=timeout
        )

    @staticmethod
    def cleanup_compose():
        """Clean up Docker Compose resources."""
        # Stop and remove containers
        DockerComposeTestHelper.run_compose_command("down", ["-v", "--remove-orphans"])

        # Remove images
        try:
            DockerComposeTestHelper.run_compose_command("down", ["--rmi", "all"])
        except subprocess.TimeoutExpired:
            pass  # Ignore timeout on cleanup

    @staticmethod
    def get_service_logs(service_name: str) -> str:
        """Get logs from a specific service."""
        result = DockerComposeTestHelper.run_compose_command("logs", [service_name])
        return result.stdout


class TestDockerComposeSetup:
    """Tests for Docker Compose configuration and setup."""

    def teardown_method(self):
        """Clean up after each test."""
        DockerComposeTestHelper.cleanup_compose()

    def test_compose_file_syntax_is_valid(self):
        """Test that docker-compose.test.yml has valid syntax."""
        result = DockerComposeTestHelper.run_compose_command("config")
        assert result.returncode == 0, f"Compose file syntax error: {result.stderr}"

    def test_compose_services_are_defined(self):
        """Test that all expected services are defined in compose file."""
        result = DockerComposeTestHelper.run_compose_command("config", ["--services"])
        assert result.returncode == 0

        services = result.stdout.strip().split("\n")
        expected_services = [
            "github-data-save",
            "github-data-restore",
            "github-data-test",
            "github-data-health",
        ]

        for service in expected_services:
            assert service in services, f"Service {service} not found in compose file"

    def test_compose_build_context_is_correct(self):
        """Test that compose file references correct build context."""
        result = DockerComposeTestHelper.run_compose_command("config")
        assert result.returncode == 0

        config_output = result.stdout
        assert "build:" in config_output or "context:" in config_output

    def test_compose_environment_variables_are_configured(self):
        """Test that environment variables are properly configured."""
        # Set test environment variables
        test_env = {
            "GITHUB_TOKEN": "test_compose_token",
            "GITHUB_REPO": "test/compose-repo",
        }

        result = DockerComposeTestHelper.run_compose_command(
            "config", environment=test_env
        )
        assert result.returncode == 0

        config_output = result.stdout
        assert "test_compose_token" in config_output or "GITHUB_TOKEN" in config_output


class TestDockerComposeProfiles:
    """Tests for Docker Compose profile functionality."""

    def teardown_method(self):
        """Clean up after each test."""
        DockerComposeTestHelper.cleanup_compose()

    def test_save_profile_includes_correct_services(self):
        """Test that save profile includes only save-related services."""
        # This test checks the profile configuration
        result = DockerComposeTestHelper.run_compose_command(
            "config", ["--profile", "save"]
        )
        assert result.returncode == 0

        # The exact output depends on docker-compose version, so we check for
        # service presence
        config_output = result.stdout
        assert "github-data-save" in config_output

    def test_restore_profile_includes_correct_services(self):
        """Test that restore profile includes only restore-related services."""
        result = DockerComposeTestHelper.run_compose_command(
            "config", ["--profile", "restore"]
        )
        assert result.returncode == 0

        config_output = result.stdout
        assert "github-data-restore" in config_output

    def test_test_profile_includes_test_services(self):
        """Test that test profile includes test-related services."""
        result = DockerComposeTestHelper.run_compose_command(
            "config", ["--profile", "test"]
        )
        assert result.returncode == 0

        config_output = result.stdout
        assert "github-data-test" in config_output


class TestDockerComposeExecution:
    """Tests for Docker Compose service execution."""

    @pytest.fixture
    def compose_temp_dir(self):
        """Create temporary directory for Docker Compose container data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test-data subdirectory as expected by compose
            test_data_dir = Path(temp_dir) / "test-data"
            test_data_dir.mkdir(exist_ok=True)
            yield temp_dir

    def teardown_method(self):
        """Clean up after each test."""
        DockerComposeTestHelper.cleanup_compose()

    def test_build_services_with_compose(self):
        """Test building all services using docker-compose."""
        result = DockerComposeTestHelper.run_compose_command("build", timeout=300)
        assert result.returncode == 0, f"Compose build failed: {result.stderr}"

    def test_test_service_runs_successfully(self, compose_temp_dir, monkeypatch):
        """Test that the test service runs and completes successfully."""
        import subprocess

        # Change to temp directory to avoid affecting real data directory
        monkeypatch.chdir(compose_temp_dir)

        # Copy compose file to temp directory and fix build context
        # Find project root dynamically
        project_root = Path(__file__).parent.parent.parent
        compose_source = project_root / "docker-compose.test.yml"
        compose_dest = Path(compose_temp_dir) / "docker-compose.test.yml"
        compose_content = compose_source.read_text()
        # Fix build context to point to project root
        compose_content = compose_content.replace("build: .", f"build: {project_root}")
        compose_dest.write_text(compose_content)

        # Build first
        result = DockerComposeTestHelper.run_compose_command("build", timeout=300)
        assert result.returncode == 0, f"Build failed: {result.stderr}"

        # Run test service using 'run' to capture output directly
        run_cmd = [
            "docker",
            "compose",
            "-f",
            "docker-compose.test.yml",
            "-p",
            DockerComposeTestHelper.PROJECT_NAME,
            "run",
            "--rm",
            "github-data-test",
        ]
        result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=60)

        # Check if service completed successfully
        assert "Docker Compose test completed successfully" in result.stdout

    def test_health_check_service_works(self, compose_temp_dir, monkeypatch):
        """Test that health check service works correctly."""
        # Change to temp directory
        monkeypatch.chdir(compose_temp_dir)

        # Copy compose file to temp directory and fix build context
        # Find project root dynamically
        project_root = Path(__file__).parent.parent.parent
        compose_source = project_root / "docker-compose.test.yml"
        compose_dest = Path(compose_temp_dir) / "docker-compose.test.yml"
        compose_content = compose_source.read_text()
        # Fix build context to point to project root
        compose_content = compose_content.replace("build: .", f"build: {project_root}")
        compose_dest.write_text(compose_content)

        # Build first
        result = DockerComposeTestHelper.run_compose_command("build", timeout=300)
        assert result.returncode == 0, f"Build failed: {result.stderr}"

        # Run health check service (build and start in detached mode)
        # First create a subprocess call directly to handle the -d flag correctly
        import subprocess

        cmd = [
            "docker",
            "compose",
            "-f",
            DockerComposeTestHelper.COMPOSE_FILE,
            "-p",
            DockerComposeTestHelper.PROJECT_NAME,
            "--profile",
            "health",
            "up",
            "-d",
            "github-data-health",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, f"Health service start failed: {result.stderr}"

        # Wait a bit for health check to run
        time.sleep(15)

        # Check service logs
        logs = DockerComposeTestHelper.get_service_logs("github-data-health")
        assert "Health check passed" in logs

    def test_service_dependencies_work_correctly(self):
        """Test that service dependencies are respected."""
        result = DockerComposeTestHelper.run_compose_command("config")
        assert result.returncode == 0

        config_output = result.stdout
        # Check that restore service depends on save service
        assert "depends_on" in config_output
        assert "github-data-save" in config_output

    def test_volume_mounts_work_in_compose(self, compose_temp_dir, monkeypatch):
        """Test that volume mounts work correctly in compose services."""
        # Change to temp directory
        monkeypatch.chdir(compose_temp_dir)

        # Create data directories
        data_dir = Path(compose_temp_dir) / "data"
        test_data_dir = Path(compose_temp_dir) / "test-data"
        data_dir.mkdir(exist_ok=True)
        test_data_dir.mkdir(exist_ok=True)

        # Copy compose file to temp directory and fix build context
        # Find project root dynamically
        project_root = Path(__file__).parent.parent.parent
        compose_source = project_root / "docker-compose.test.yml"
        compose_dest = Path(compose_temp_dir) / "docker-compose.test.yml"
        compose_content = compose_source.read_text()
        # Fix build context to point to project root
        compose_content = compose_content.replace("build: .", f"build: {project_root}")
        compose_dest.write_text(compose_content)

        # Build first
        result = DockerComposeTestHelper.run_compose_command("build", timeout=300)
        assert result.returncode == 0, f"Build failed: {result.stderr}"

        # Run a service that should create files in mounted volume
        # Modify the test service command to create a test file
        modified_compose = compose_dest.read_text().replace(
            'command: ["python", "-c", '
            "\"print('Docker Compose test completed successfully')\"]",
            'command: ["sh", "-c", '
            "\"echo 'volume test' > /data/volume_test.txt && "
            'cat /data/volume_test.txt"]',
        )
        compose_dest.write_text(modified_compose)

        # Run the modified test service using 'run' to wait for completion
        result = DockerComposeTestHelper.run_compose_command(
            "run", ["--rm", "github-data-test"], timeout=60
        )

        # Check that file was created in host directory
        test_file = test_data_dir / "volume_test.txt"
        assert test_file.exists(), "Volume mount should allow file creation"
        assert test_file.read_text().strip() == "volume test"


class TestDockerComposeNetworking:
    """Tests for Docker Compose networking functionality."""

    def teardown_method(self):
        """Clean up after each test."""
        DockerComposeTestHelper.cleanup_compose()

    def test_custom_network_is_created(self):
        """Test that custom network is properly configured."""
        result = DockerComposeTestHelper.run_compose_command("config")
        assert result.returncode == 0

        config_output = result.stdout
        assert "networks:" in config_output
        assert "github-data-network" in config_output

    def test_services_can_communicate_on_network(self, monkeypatch):
        """Test that services can communicate with each other on the custom network."""
        # This is a more complex test that would require running multiple services
        # For now, we'll test that the network configuration is valid
        result = DockerComposeTestHelper.run_compose_command("config")
        assert result.returncode == 0

        # Verify network configuration doesn't have syntax errors
        config_lines = result.stdout.split("\n")
        network_section = False
        for line in config_lines:
            if "networks:" in line:
                network_section = True
            elif network_section and "name:" in line:
                assert "github-data-network" in line


class TestDockerComposeErrorHandling:
    """Tests for Docker Compose error handling and edge cases."""

    def teardown_method(self):
        """Clean up after each test."""
        DockerComposeTestHelper.cleanup_compose()

    def test_compose_handles_missing_environment_variables(self):
        """Test compose behavior with missing environment variables."""
        # Remove environment variables that have defaults
        clean_env = {k: v for k, v in os.environ.items() if not k.startswith("GITHUB_")}

        result = DockerComposeTestHelper.run_compose_command(
            "config", environment=clean_env
        )

        # Should still work with default values
        assert result.returncode == 0

        config_output = result.stdout
        assert "fake_token" in config_output  # Default value should be used

    def test_compose_validates_service_configuration(self):
        """Test that compose validates service configurations."""
        # Test with valid configuration
        result = DockerComposeTestHelper.run_compose_command("config", ["--quiet"])
        assert result.returncode == 0, "Valid compose file should pass validation"

    def test_compose_fails_gracefully_on_build_errors(self, tmp_path):
        """Test compose behavior when build fails."""
        # Create a compose file with invalid Dockerfile reference
        invalid_compose = tmp_path / "docker-compose.invalid.yml"
        invalid_compose.write_text(
            """
version: '3.8'
services:
  test-service:
    build: ./nonexistent-directory
"""
        )

        cmd = ["docker", "compose", "-f", str(invalid_compose), "build"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode != 0, "Should fail with invalid build context"
        assert (
            "nonexistent-directory" in result.stderr
            or "cannot" in result.stderr.lower()
        )


class TestDockerComposePerformance:
    """Performance tests for Docker Compose operations."""

    def teardown_method(self):
        """Clean up after each test."""
        DockerComposeTestHelper.cleanup_compose()

    def test_compose_build_time_is_reasonable(self):
        """Test that compose build completes in reasonable time."""
        start_time = time.time()

        result = DockerComposeTestHelper.run_compose_command("build", timeout=600)
        build_time = time.time() - start_time

        assert result.returncode == 0, f"Build failed: {result.stderr}"
        assert build_time < 600, f"Build took too long: {build_time:.2f} seconds"

    def test_compose_up_time_is_reasonable(self, monkeypatch):
        """Test that compose services start up quickly."""
        # Use a temporary directory to avoid conflicts
        with tempfile.TemporaryDirectory() as temp_dir:
            monkeypatch.chdir(temp_dir)

            # Copy compose file and fix build context
            # Find project root dynamically
            project_root = Path(__file__).parent.parent.parent
            compose_source = project_root / "docker-compose.test.yml"
            compose_dest = Path(temp_dir) / "docker-compose.test.yml"
            compose_content = compose_source.read_text()
            # Fix build context to point to project root
            compose_content = compose_content.replace(
                "build: .", f"build: {project_root}"
            )
            compose_dest.write_text(compose_content)

            # Create required directories
            (Path(temp_dir) / "test-data").mkdir()

            # Build first
            build_result = DockerComposeTestHelper.run_compose_command(
                "build", timeout=600
            )
            assert build_result.returncode == 0, "Build should succeed"

            start_time = time.time()

            DockerComposeTestHelper.run_compose_command(
                "up", ["--profile", "test", "github-data-test"], timeout=120
            )

            startup_time = time.time() - start_time

            # Service should start and complete within 2 minutes
            assert (
                startup_time < 120
            ), f"Service startup too slow: {startup_time:.2f} seconds"
