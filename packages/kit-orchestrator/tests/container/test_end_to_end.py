"""End-to-end container tests for kit-orchestrator.

Tests full freeze/restore workflows in containerized environment.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional

import pytest

pytestmark = [
    pytest.mark.container,
    pytest.mark.integration,
    pytest.mark.slow,
]


class KitOrchestratorTestHelper:
    """Helper class for kit-orchestrator container testing."""

    IMAGE_NAME = "kit-orchestrator-test"
    DOCKERFILE_PATH = "docker/kit-orchestrator.Dockerfile"

    @staticmethod
    def build_image(tag: Optional[str] = None) -> str:
        """Build kit-orchestrator Docker image and return the tag."""
        image_tag = tag or KitOrchestratorTestHelper.IMAGE_NAME

        # Build from repository root
        cmd = [
            "docker",
            "build",
            "-f",
            KitOrchestratorTestHelper.DOCKERFILE_PATH,
            "-t",
            image_tag,
            ".",
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd="/workspaces/github-data"
        )
        if result.returncode != 0:
            raise RuntimeError(f"Docker build failed: {result.stderr}")

        return image_tag

    @staticmethod
    def run_container(
        image_tag: str,
        environment: Dict[str, str],
        volumes: Dict[str, str],
    ) -> subprocess.CompletedProcess:
        """Run kit-orchestrator container with specified configuration."""
        cmd = ["docker", "run", "--rm"]

        # Add environment variables
        for key, value in environment.items():
            cmd.extend(["-e", f"{key}={value}"])

        # Add volume mounts
        for host_path, container_path in volumes.items():
            cmd.extend(["-v", f"{host_path}:{container_path}"])

        cmd.append(image_tag)

        return subprocess.run(cmd, capture_output=True, text=True)

    @staticmethod
    def cleanup_images() -> None:
        """Clean up test images."""
        subprocess.run(
            ["docker", "rmi", "-f", KitOrchestratorTestHelper.IMAGE_NAME],
            capture_output=True,
        )


@pytest.fixture(scope="module")
def kit_orchestrator_image():
    """Build kit-orchestrator image once for all tests in this module."""
    image_tag = KitOrchestratorTestHelper.build_image()
    yield image_tag
    KitOrchestratorTestHelper.cleanup_images()


@pytest.fixture
def test_data_dir():
    """Create temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def github_token():
    """Get GitHub token from environment."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN not set - skipping container tests")
    return token


class TestKitOrchestratorBuild:
    """Test kit-orchestrator Docker build process."""

    def test_image_builds_successfully(self, kit_orchestrator_image):
        """Verify kit-orchestrator image builds without errors."""
        assert kit_orchestrator_image == KitOrchestratorTestHelper.IMAGE_NAME

    def test_image_has_python(self, kit_orchestrator_image):
        """Verify image contains Python runtime."""
        result = subprocess.run(
            ["docker", "run", "--rm", kit_orchestrator_image, "python", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Python 3.11" in result.stdout

    def test_image_has_git(self, kit_orchestrator_image):
        """Verify image contains git for git operations."""
        result = subprocess.run(
            ["docker", "run", "--rm", kit_orchestrator_image, "git", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "git version" in result.stdout


class TestKitOrchestratorEndToEnd:
    """End-to-end tests for complete freeze/restore workflows."""

    def test_save_operation_requires_operation_env(
        self, kit_orchestrator_image, test_data_dir
    ):
        """Verify container fails without OPERATION environment variable."""
        environment = {
            "GITHUB_TOKEN": "dummy_token",
            "GITHUB_REPO": "owner/repo",
        }
        volumes = {str(test_data_dir): "/data"}

        result = KitOrchestratorTestHelper.run_container(
            kit_orchestrator_image, environment, volumes
        )

        assert result.returncode != 0
        assert "OPERATION environment variable required" in result.stderr

    def test_save_operation_requires_github_token(
        self, kit_orchestrator_image, test_data_dir
    ):
        """Verify container fails without GITHUB_TOKEN."""
        environment = {
            "OPERATION": "save",
            "GITHUB_REPO": "owner/repo",
        }
        volumes = {str(test_data_dir): "/data"}

        result = KitOrchestratorTestHelper.run_container(
            kit_orchestrator_image, environment, volumes
        )

        assert result.returncode != 0
        assert "GITHUB_TOKEN environment variable required" in result.stderr

    def test_save_operation_requires_github_repo(
        self, kit_orchestrator_image, test_data_dir, github_token
    ):
        """Verify container fails without GITHUB_REPO."""
        environment = {
            "OPERATION": "save",
            "GITHUB_TOKEN": github_token,
        }
        volumes = {str(test_data_dir): "/data"}

        result = KitOrchestratorTestHelper.run_container(
            kit_orchestrator_image, environment, volumes
        )

        assert result.returncode != 0
        assert "GITHUB_REPO environment variable required" in result.stderr

    def test_backward_compatibility_with_original_interface(
        self, kit_orchestrator_image, test_data_dir, github_token
    ):
        """Verify kit-orchestrator maintains backward compatibility.

        This test validates that the kit-orchestrator container accepts
        the same environment variables and produces the same output
        structure as the original monolithic container.
        """
        environment = {
            "OPERATION": "save",
            "GITHUB_TOKEN": github_token,
            "GITHUB_REPO": "anthropics/anthropic-cookbook",  # Small public repo
            "DATA_PATH": "/data",
            # Minimal entity set for faster testing
            "INCLUDE_LABELS": "true",
            "INCLUDE_MILESTONES": "true",
            "INCLUDE_ISSUES": "false",
            "INCLUDE_PULL_REQUESTS": "false",
            "INCLUDE_GIT_REPO": "false",
        }
        volumes = {str(test_data_dir): "/data"}

        result = KitOrchestratorTestHelper.run_container(
            kit_orchestrator_image, environment, volumes
        )

        # Should complete successfully
        assert result.returncode == 0
        assert "operation completed successfully" in result.stdout.lower()

        # Verify expected data files exist
        assert (test_data_dir / "labels.json").exists()
        assert (test_data_dir / "milestones.json").exists()

    @pytest.mark.slow
    def test_full_save_restore_cycle(
        self, kit_orchestrator_image, test_data_dir, github_token
    ):
        """Test complete save and restore workflow.

        This is the most comprehensive test - it validates:
        1. Save operation collects all data
        2. Restore operation recreates repository state
        3. All entity types are handled correctly
        4. Cross-entity dependencies work (e.g., issues -> labels)
        """
        # This test would require a test repository we can modify
        # Skipping for now - will implement when test infrastructure is ready
        pytest.skip("Full save/restore cycle requires test repository infrastructure")

    def test_selective_entity_save(
        self, kit_orchestrator_image, test_data_dir, github_token
    ):
        """Test selective entity filtering (e.g., only specific issue numbers)."""
        environment = {
            "OPERATION": "save",
            "GITHUB_TOKEN": github_token,
            "GITHUB_REPO": "anthropics/anthropic-cookbook",
            "DATA_PATH": "/data",
            # Save only specific issues
            "INCLUDE_LABELS": "false",
            "INCLUDE_MILESTONES": "false",
            "INCLUDE_ISSUES": "1,2,3",  # Selective issue numbers
            "INCLUDE_PULL_REQUESTS": "false",
            "INCLUDE_GIT_REPO": "false",
        }
        volumes = {str(test_data_dir): "/data"}

        result = KitOrchestratorTestHelper.run_container(
            kit_orchestrator_image, environment, volumes
        )

        assert result.returncode == 0
        assert "operation completed successfully" in result.stdout.lower()

        # Verify selective filtering worked
        if (test_data_dir / "issues.json").exists():
            import json

            with open(test_data_dir / "issues.json") as f:
                issues = json.load(f)
                # Should only have issues 1, 2, 3 (if they exist in the repo)
                issue_numbers = [issue["number"] for issue in issues]
                assert all(num in [1, 2, 3] for num in issue_numbers)


class TestKitOrchestratorErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_operation_fails_gracefully(
        self, kit_orchestrator_image, test_data_dir, github_token
    ):
        """Verify invalid OPERATION value is rejected."""
        environment = {
            "OPERATION": "invalid_op",
            "GITHUB_TOKEN": github_token,
            "GITHUB_REPO": "owner/repo",
        }
        volumes = {str(test_data_dir): "/data"}

        result = KitOrchestratorTestHelper.run_container(
            kit_orchestrator_image, environment, volumes
        )

        assert result.returncode != 0
        assert "Invalid OPERATION" in result.stderr

    def test_nonexistent_repository_fails_on_save(
        self, kit_orchestrator_image, test_data_dir, github_token
    ):
        """Verify save operation fails for nonexistent repository."""
        environment = {
            "OPERATION": "save",
            "GITHUB_TOKEN": github_token,
            "GITHUB_REPO": "definitely-not-a-real-repo/nonexistent-12345",
            "DATA_PATH": "/data",
        }
        volumes = {str(test_data_dir): "/data"}

        result = KitOrchestratorTestHelper.run_container(
            kit_orchestrator_image, environment, volumes
        )

        assert result.returncode != 0
        # Should see GitHub API error about repository not found
        assert "404" in result.stderr or "not found" in result.stderr.lower()

    def test_restore_with_create_repository_flag(
        self, kit_orchestrator_image, test_data_dir, github_token
    ):
        """Verify CREATE_REPOSITORY_IF_MISSING flag works correctly."""
        # This test would require ability to create test repositories
        # Skipping for now
        pytest.skip("Repository creation test requires additional infrastructure")
