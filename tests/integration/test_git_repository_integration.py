"""Integration tests for Git repository operations."""

import pytest
from pathlib import Path
from unittest.mock import patch
from src.git.service import GitRepositoryServiceImpl
from src.entities.git_repositories.models import GitBackupFormat, GitOperationResult
from src.operations.save.strategies.git_repository_strategy import GitRepositoryStrategy
from src.operations.restore.strategies.git_repository_strategy import (
    GitRepositoryRestoreStrategy,
)

# Test markers following project standards
pytestmark = [pytest.mark.integration, pytest.mark.medium, pytest.mark.git_repositories]


class TestGitRepositoryIntegration:
    """Integration test suite for Git repository operations."""

    @pytest.fixture
    def git_service(self):
        """Create Git repository service."""
        return GitRepositoryServiceImpl()

    @pytest.fixture
    def git_strategy(self, git_service):
        """Create Git repository strategy."""
        return GitRepositoryStrategy(git_service, GitBackupFormat.MIRROR)

    @pytest.fixture
    def git_restore_strategy(self, git_service):
        """Create Git repository restore strategy."""
        return GitRepositoryRestoreStrategy(git_service)

    @pytest.mark.skipif(
        True,  # Skip by default as it requires real Git operations
        reason="Git integration tests require --run-git-integration flag",
    )
    @pytest.mark.slow
    @pytest.mark.github_api
    def test_public_repository_clone_real(self, git_service, temp_data_dir):
        """Test cloning public repository from GitHub."""
        destination = Path(temp_data_dir) / "test_repo"

        result = git_service.clone_repository(
            "https://github.com/octocat/Hello-World.git",
            destination,
            GitBackupFormat.MIRROR,
        )

        assert result.success is True
        assert destination.exists()
        assert (destination / "HEAD").exists()

    def test_git_strategy_collect_data_structure(self, git_strategy):
        """Test Git strategy data collection creates proper structure."""
        entities = git_strategy.collect_data(None, "test/repo")

        assert len(entities) == 1
        entity = entities[0]
        assert entity["repo_name"] == "test/repo"
        assert entity["repo_url"] == "https://github.com/test/repo.git"
        assert entity["backup_format"] == GitBackupFormat.MIRROR.value

    def test_git_strategy_save_data_integration(
        self, git_strategy, storage_service_mock, temp_data_dir
    ):
        """Test Git strategy save data with mocked Git operations."""
        entities = [
            {
                "repo_name": "test/repo",
                "repo_url": "https://github.com/test/repo.git",
                "backup_format": GitBackupFormat.MIRROR.value,
            }
        ]

        # Mock the git service to avoid actual cloning
        with patch.object(git_strategy._git_service, "clone_repository") as mock_clone:
            mock_result = GitOperationResult(
                success=True,
                backup_format="mirror",
                destination=str(Path(temp_data_dir) / "git-repo"),
                size_bytes=1024,
            )
            mock_clone.return_value = mock_result

            result = git_strategy.save_data(
                entities, temp_data_dir, storage_service_mock
            )

        assert result["total_repositories"] == 1
        assert result["saved_repositories"] == 1
        assert (Path(temp_data_dir) / "git-repo").exists()
        mock_clone.assert_called_once()

    def test_git_strategy_save_data_error_handling(
        self, git_strategy, storage_service_mock, temp_data_dir
    ):
        """Test Git strategy error handling during save."""
        entities = [
            {
                "repo_name": "test/repo",
                "repo_url": "https://github.com/test/repo.git",
                "backup_format": GitBackupFormat.MIRROR.value,
            }
        ]

        # Mock the git service to return failure
        with patch.object(git_strategy._git_service, "clone_repository") as mock_clone:
            mock_result = GitOperationResult(
                success=False, backup_format="mirror", error="Authentication failed"
            )
            mock_clone.return_value = mock_result

            result = git_strategy.save_data(
                entities, temp_data_dir, storage_service_mock
            )

        assert result["total_repositories"] == 1
        assert result["saved_repositories"] == 0
        assert len(result["results"]) == 1
        assert result["results"][0]["success"] is False
        assert "Authentication failed" in result["results"][0]["error"]


    def test_git_service_and_strategy_integration(
        self, git_service, storage_service_mock, temp_data_dir
    ):
        """Test integration between GitRepositoryService and GitRepositoryStrategy."""
        strategy = GitRepositoryStrategy(git_service, GitBackupFormat.MIRROR)

        # Mock the command executor to avoid actual Git operations
        with patch.object(
            git_service._command_executor, "execute_clone_mirror"
        ) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "method": "mirror",
                "destination": str(Path(temp_data_dir) / "git-repo"),
                "size_bytes": 2048,
            }

            entities = strategy.collect_data(None, "test/repo")
            result = strategy.save_data(entities, temp_data_dir, storage_service_mock)

            assert result["saved_repositories"] == 1
            mock_execute.assert_called_once()

    def test_git_restore_strategy_load_data(
        self, git_restore_strategy, storage_service_mock, temp_data_dir
    ):
        """Test Git restore strategy load data functionality."""
        # Create mock git-repo directory structure with flattened layout
        git_data_dir = Path(temp_data_dir) / "git-repo"
        git_data_dir.mkdir(parents=True)

        # Create mock Git repository directly in git-repo (simulating clone)
        git_dir = git_data_dir / ".git"
        git_dir.mkdir()

        # Act
        repositories = git_restore_strategy.load_data(
            temp_data_dir, storage_service_mock
        )

        # Assert - only one repository should be found (the flattened one)
        assert len(repositories) == 1

        # Check mirror repository (flattened structure)
        mirror_data = repositories[0]
        assert mirror_data["backup_format"] == GitBackupFormat.MIRROR.value
        assert (
            mirror_data["repo_name"] == "repository"
        )  # Generic name for flattened structure
        assert mirror_data["backup_path"] == str(git_data_dir)

    def test_git_restore_strategy_restore_data(
        self, git_restore_strategy, temp_data_dir
    ):
        """Test Git restore strategy restore data functionality."""
        entities = [
            {
                "backup_path": str(Path(temp_data_dir) / "backup_repo.git"),
                "backup_format": GitBackupFormat.MIRROR.value,
                "repo_name": "test/repo",
            }
        ]

        # Create mock backup directory
        backup_path = Path(entities[0]["backup_path"])
        backup_path.mkdir(parents=True)

        with patch.object(
            git_restore_strategy._git_service, "restore_repository"
        ) as mock_restore:
            mock_result = GitOperationResult(
                success=True,
                backup_format="mirror",
                destination=str(
                    Path(temp_data_dir) / "restored-repositories" / "test_repo"
                ),
                size_bytes=1024,
            )
            mock_restore.return_value = mock_result

            result = git_restore_strategy.restore_data(entities, temp_data_dir)

        assert result["total_repositories"] == 1
        assert result["restored_repositories"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["success"] is True
        mock_restore.assert_called_once()

    def test_git_restore_strategy_error_handling(
        self, git_restore_strategy, temp_data_dir
    ):
        """Test Git restore strategy error handling."""
        entities = [
            {
                "backup_path": str(Path(temp_data_dir) / "backup_repo.git"),
                "backup_format": GitBackupFormat.MIRROR.value,
                "repo_name": "test/repo",
            }
        ]

        # Create mock backup directory
        backup_path = Path(entities[0]["backup_path"])
        backup_path.mkdir(parents=True)

        with patch.object(
            git_restore_strategy._git_service, "restore_repository"
        ) as mock_restore:
            mock_result = GitOperationResult(
                success=False,
                backup_format="mirror",
                error="Restore failed: corrupted backup",
            )
            mock_restore.return_value = mock_result

            result = git_restore_strategy.restore_data(entities, temp_data_dir)

        assert result["total_repositories"] == 1
        assert result["restored_repositories"] == 0
        assert len(result["results"]) == 1
        assert result["results"][0]["success"] is False
        assert "corrupted backup" in result["results"][0]["error"]


@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.storage
class TestGitRepositoryStorageIntegration:
    """Integration tests for Git repository storage operations."""

    def test_git_data_directory_creation(self, temp_data_dir, storage_service_mock):
        """Test that git-repo directory is created properly."""
        git_service = GitRepositoryServiceImpl()
        strategy = GitRepositoryStrategy(git_service, GitBackupFormat.MIRROR)

        entities = [
            {
                "repo_name": "test/repo",
                "repo_url": "https://github.com/test/repo.git",
                "backup_format": GitBackupFormat.MIRROR.value,
            }
        ]

        with patch.object(
            git_service._command_executor, "execute_clone_mirror"
        ) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "method": "mirror",
                "destination": str(Path(temp_data_dir) / "git-repo"),
                "size_bytes": 512,
            }

            strategy.save_data(entities, temp_data_dir, storage_service_mock)

            git_data_dir = Path(temp_data_dir) / "git-repo"
            assert git_data_dir.exists()
            assert git_data_dir.is_dir()

    def test_git_backup_path_sanitization(self, temp_data_dir, storage_service_mock):
        """Test that repository names with slashes are properly sanitized for paths."""
        git_service = GitRepositoryServiceImpl()
        strategy = GitRepositoryStrategy(git_service, GitBackupFormat.MIRROR)

        entities = [
            {
                "repo_name": "organization/repository-name",
                "repo_url": "https://github.com/organization/repository-name.git",
                "backup_format": GitBackupFormat.MIRROR.value,
            }
        ]

        with patch.object(
            git_service._command_executor, "execute_clone_mirror"
        ) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "method": "mirror",
                "destination": str(Path(temp_data_dir) / "git-repo"),
                "size_bytes": 1024,
            }

            strategy.save_data(entities, temp_data_dir, storage_service_mock)

            # Verify the path goes directly to git-repo (flattened structure)
            expected_path = Path(temp_data_dir) / "git-repo"
            mock_execute.assert_called_once()
            args, kwargs = mock_execute.call_args
            assert args[1] == expected_path  # destination parameter

    def test_git_mirror_path_handling(
        self, temp_data_dir, storage_service_mock
    ):
        """Test mirror format path handling."""
        git_service = GitRepositoryServiceImpl()

        # Test mirror format
        mirror_strategy = GitRepositoryStrategy(git_service, GitBackupFormat.MIRROR)
        mirror_entities = [
            {
                "repo_name": "test/repo",
                "repo_url": "https://github.com/test/repo.git",
                "backup_format": GitBackupFormat.MIRROR.value,
            }
        ]

        with patch.object(
            git_service._command_executor, "execute_clone_mirror"
        ) as mock_mirror:
            mock_mirror.return_value = {
                "success": True,
                "method": "mirror",
                "destination": str(Path(temp_data_dir) / "git-repo"),
                "size_bytes": 1024,
            }

            mirror_strategy.save_data(
                mirror_entities, temp_data_dir, storage_service_mock
            )

            # Verify mirror path (directory)
            args, kwargs = mock_mirror.call_args
            assert not str(args[1]).endswith(".bundle")


@pytest.mark.integration
@pytest.mark.medium
class TestGitRepositoryWorkflow:
    """Integration tests for complete Git repository workflows."""

    def test_complete_save_restore_workflow(self, temp_data_dir, storage_service_mock):
        """Test complete save and restore workflow integration."""
        git_service = GitRepositoryServiceImpl()

        # Step 1: Save operation
        save_strategy = GitRepositoryStrategy(git_service, GitBackupFormat.MIRROR)
        entities = [
            {
                "repo_name": "test/repo",
                "repo_url": "https://github.com/test/repo.git",
                "backup_format": GitBackupFormat.MIRROR.value,
            }
        ]

        # Mock save operation
        with patch.object(
            git_service._command_executor, "execute_clone_mirror"
        ) as mock_clone:
            mock_clone.return_value = {
                "success": True,
                "method": "mirror",
                "destination": str(Path(temp_data_dir) / "git-repo"),
                "size_bytes": 1024,
            }

            save_result = save_strategy.save_data(
                entities, temp_data_dir, storage_service_mock
            )

        assert save_result["saved_repositories"] == 1

        # Simulate the saved directory structure (flattened)
        git_data_dir = Path(temp_data_dir) / "git-repo"
        git_data_dir.mkdir(parents=True, exist_ok=True)
        # Create .git directory to simulate a Git repository
        git_dir = git_data_dir / ".git"
        git_dir.mkdir()

        # Step 2: Restore operation
        restore_strategy = GitRepositoryRestoreStrategy(git_service)

        # Mock restore operation
        with patch.object(git_service, "restore_repository") as mock_restore:
            mock_restore.return_value = GitOperationResult(
                success=True,
                backup_format="mirror",
                destination=str(
                    Path(temp_data_dir) / "restored-repositories" / "test_repo"
                ),
                size_bytes=1024,
            )

            restore_result = restore_strategy.restore_data(
                restore_strategy.load_data(temp_data_dir, storage_service_mock),
                temp_data_dir,
            )

        assert restore_result["restored_repositories"] == 1
        assert restore_result["total_repositories"] == 1

    def test_empty_git_data_directory_handling(
        self, temp_data_dir, storage_service_mock
    ):
        """Test handling of empty git-repo directory."""
        git_service = GitRepositoryServiceImpl()
        restore_strategy = GitRepositoryRestoreStrategy(git_service)

        # No git-repo directory exists
        repositories = restore_strategy.load_data(temp_data_dir, storage_service_mock)
        assert repositories == []

        # Empty git-repo directory
        git_data_dir = Path(temp_data_dir) / "git-repo"
        git_data_dir.mkdir()

        repositories = restore_strategy.load_data(temp_data_dir, storage_service_mock)
        assert repositories == []

