"""Unit tests for Git repository service."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from github_data.git.service import GitRepositoryServiceImpl
from github_data.git.command_executor import GitCommandExecutorImpl
from github_data.entities.git_repositories.models import GitBackupFormat

# Test markers following project standards
pytestmark = [pytest.mark.unit, pytest.mark.fast]


class TestGitRepositoryService:
    """Test suite for Git repository service."""

    @pytest.fixture
    def mock_command_executor(self):
        """Create mock command executor."""
        return Mock(spec=GitCommandExecutorImpl)

    @pytest.fixture
    def git_service(self, mock_command_executor):
        """Create Git repository service instance with mocked executor."""
        return GitRepositoryServiceImpl(command_executor=mock_command_executor)

    def test_clone_repository_success_mirror(
        self, git_service, mock_command_executor, temp_data_dir
    ):
        """Test successful mirror repository clone."""
        # Arrange
        repo_url = "https://github.com/test/repo.git"
        destination = Path(temp_data_dir) / "test_repo"
        expected_result = {
            "success": True,
            "method": "mirror",
            "destination": str(destination),
            "size_bytes": 1024,
        }
        mock_command_executor.execute_clone_mirror.return_value = expected_result

        # Act
        result = git_service.clone_repository(
            repo_url, destination, GitBackupFormat.MIRROR
        )

        # Assert
        assert result.success is True
        assert result.backup_format == "mirror"
        assert result.destination == str(destination)
        mock_command_executor.execute_clone_mirror.assert_called_once_with(
            repo_url, destination
        )

    def test_clone_repository_failure_returns_error_result(
        self, git_service, mock_command_executor, temp_data_dir
    ):
        """Test clone repository failure handling."""
        # Arrange
        repo_url = "https://github.com/test/repo.git"
        destination = Path(temp_data_dir) / "test_repo"
        mock_command_executor.execute_clone_mirror.side_effect = RuntimeError(
            "Clone failed"
        )

        # Act
        result = git_service.clone_repository(
            repo_url, destination, GitBackupFormat.MIRROR
        )

        # Assert
        assert result.success is False
        assert "Clone failed" in result.error
        assert result.backup_format == "mirror"

    def test_validate_repository_delegates_to_executor(
        self, git_service, mock_command_executor, temp_data_dir
    ):
        """Test repository validation delegates to command executor."""
        # Arrange
        repo_path = Path(temp_data_dir) / "test_repo.git"
        repo_path.mkdir()
        expected_validation = {"valid": True, "fsck_output": "ok"}
        mock_command_executor.execute_fsck.return_value = expected_validation

        # Act
        result = git_service.validate_repository(repo_path)

        # Assert
        assert result == expected_validation
        mock_command_executor.execute_fsck.assert_called_once_with(repo_path)

    def test_validate_repository_nonexistent_path(
        self, git_service, mock_command_executor, temp_data_dir
    ):
        """Test validation of nonexistent repository path."""
        # Arrange
        nonexistent_path = Path(temp_data_dir) / "nonexistent"

        # Act
        result = git_service.validate_repository(nonexistent_path)

        # Assert
        assert result["valid"] is False
        assert "does not exist" in result["error"]

    def test_update_repository_mirror_format(
        self, git_service, mock_command_executor, temp_data_dir
    ):
        """Test updating mirror repository."""
        # Arrange
        repo_path = Path(temp_data_dir) / "test_repo.git"
        repo_path.mkdir()

        update_result = {
            "success": True,
            "method": "remote_update",
            "path": str(repo_path),
        }
        stats_result = {"commit_count": 150, "branch_count": 5}

        mock_command_executor.execute_remote_update.return_value = update_result
        mock_command_executor.get_repository_stats.return_value = stats_result

        # Act
        result = git_service.update_repository(repo_path, GitBackupFormat.MIRROR)

        # Assert
        assert result.success is True
        assert result.backup_format == "mirror"
        assert result.metadata["commit_count"] == 150
        mock_command_executor.execute_remote_update.assert_called_once_with(repo_path)

    def test_get_repository_info_mirror(
        self, git_service, mock_command_executor, temp_data_dir
    ):
        """Test getting repository info for mirror."""
        # Arrange
        repo_path = Path(temp_data_dir) / "test_repo.git"
        repo_path.mkdir()
        stats_result = {"commit_count": 100, "branch_count": 3, "tag_count": 5}
        mock_command_executor.get_repository_stats.return_value = stats_result
        mock_command_executor.get_directory_size.return_value = 4096

        # Act
        result = git_service.get_repository_info(repo_path)

        # Assert
        assert result.repo_name == "test_repo.git"
        assert result.backup_format == GitBackupFormat.MIRROR
        assert result.commit_count == 100
        assert result.branch_count == 3
        assert result.tag_count == 5

    def test_restore_repository_from_mirror(
        self, git_service, mock_command_executor, temp_data_dir
    ):
        """Test restoring repository from mirror."""
        # Arrange
        backup_path = Path(temp_data_dir) / "backup_repo.git"
        backup_path.mkdir()
        destination = Path(temp_data_dir) / "restored_repo"

        # Act
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            mock_command_executor.get_directory_size.return_value = 2048

            result = git_service.restore_repository(
                backup_path, destination, GitBackupFormat.MIRROR
            )

        # Assert
        assert result.success is True
        assert result.backup_format == "mirror"
        mock_run.assert_called_once()


class TestGitCommandExecutor:
    """Test suite for Git command executor."""

    @pytest.fixture
    def git_executor(self):
        """Create Git command executor instance."""
        return GitCommandExecutorImpl(auth_token="test_token")

    @patch("src.git.command_executor.subprocess.run")
    def test_execute_clone_mirror_success(
        self, mock_subprocess, git_executor, temp_data_dir
    ):
        """Test successful git clone --mirror execution."""
        # Arrange
        destination = Path(temp_data_dir) / "test_repo.git"
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Act
        with patch.object(git_executor, "get_directory_size", return_value=2048):
            with patch.object(
                git_executor, "_get_mirror_info", return_value={"commit_count": 10}
            ):
                result = git_executor.execute_clone_mirror(
                    "https://github.com/test/repo.git", destination
                )

        # Assert
        assert result["success"] is True
        assert result["method"] == "mirror"
        assert result["destination"] == str(destination)
        assert result["size_bytes"] == 2048
        mock_subprocess.assert_called_once()

    @patch("src.git.command_executor.subprocess.run")
    def test_execute_clone_mirror_failure(
        self, mock_subprocess, git_executor, temp_data_dir
    ):
        """Test git clone --mirror execution failure."""
        # Arrange
        destination = Path(temp_data_dir) / "test_repo.git"
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Authentication failed"
        mock_subprocess.return_value = mock_result

        # Act & Assert
        with pytest.raises(RuntimeError, match="Git clone failed"):
            git_executor.execute_clone_mirror(
                "https://github.com/test/repo.git", destination
            )

    def test_prepare_authenticated_url_https(self, git_executor):
        """Test HTTPS URL authentication preparation."""
        original_url = "https://github.com/test/repo.git"
        auth_url = git_executor._prepare_authenticated_url(original_url)

        assert auth_url == "https://test_token@github.com/test/repo.git"

    def test_prepare_authenticated_url_ssh_conversion(self, git_executor):
        """Test SSH URL conversion to authenticated HTTPS."""
        ssh_url = "git@github.com:test/repo.git"
        auth_url = git_executor._prepare_authenticated_url(ssh_url)

        assert auth_url == "https://test_token@github.com/test/repo.git"

    def test_prepare_authenticated_url_no_token(self):
        """Test URL preparation without authentication token."""
        executor = GitCommandExecutorImpl(auth_token=None)
        original_url = "https://github.com/test/repo.git"
        auth_url = executor._prepare_authenticated_url(original_url)

        assert auth_url == original_url

    @patch("src.git.command_executor.subprocess.run")
    def test_execute_fsck_success(self, mock_subprocess, git_executor, temp_data_dir):
        """Test successful git fsck execution."""
        # Arrange
        repo_path = Path(temp_data_dir) / "test_repo.git"

        # Mock rev-parse command (validates git repo)
        rev_parse_result = Mock()
        rev_parse_result.returncode = 0

        # Mock fsck command
        fsck_result = Mock()
        fsck_result.returncode = 0
        fsck_result.stdout = "Everything looks good"

        mock_subprocess.side_effect = [rev_parse_result, fsck_result]

        # Act
        result = git_executor.execute_fsck(repo_path)

        # Assert
        assert result["valid"] is True
        assert "Everything looks good" in result["fsck_output"]
        assert mock_subprocess.call_count == 2

    @patch("src.git.command_executor.subprocess.run")
    def test_execute_fsck_invalid_repo(
        self, mock_subprocess, git_executor, temp_data_dir
    ):
        """Test git fsck on invalid repository."""
        # Arrange
        repo_path = Path(temp_data_dir) / "not_a_repo"

        # Mock rev-parse command failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result

        # Act
        result = git_executor.execute_fsck(repo_path)

        # Assert
        assert result["valid"] is False
        assert "Not a valid git repository" in result["error"]

    @patch("src.git.command_executor.subprocess.run")
    def test_get_repository_stats(self, mock_subprocess, git_executor, temp_data_dir):
        """Test getting repository statistics."""
        # Arrange
        repo_path = Path(temp_data_dir) / "test_repo.git"

        # Mock commit count command
        commit_result = Mock()
        commit_result.returncode = 0
        commit_result.stdout = "42"

        # Mock branch count command
        branch_result = Mock()
        branch_result.returncode = 0
        branch_result.stdout = "origin/main\norigin/dev\n"

        # Mock tag count command
        tag_result = Mock()
        tag_result.returncode = 0
        tag_result.stdout = "v1.0\nv2.0\nv3.0"

        mock_subprocess.side_effect = [commit_result, branch_result, tag_result]

        # Act
        result = git_executor.get_repository_stats(repo_path)

        # Assert
        assert result["commit_count"] == 42
        assert result["branch_count"] == 2
        assert result["tag_count"] == 3
        assert mock_subprocess.call_count == 3

    @patch("os.walk")
    def testget_directory_size(self, mock_walk, git_executor, temp_data_dir):
        """Test directory size calculation."""
        # Arrange - mock os.walk to return file structure
        mock_walk.return_value = [("/test", ["dir1"], ["file1", "file2"])]

        # Mock Path.stat() calls for the files
        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.side_effect = [
                Mock(st_size=1024),  # file1
                Mock(st_size=2048),  # file2
            ]

            # Act
            result = git_executor.get_directory_size(Path(temp_data_dir))

        # Assert
        assert result == 3072  # 1024 + 2048
        assert mock_walk.called
        assert mock_stat.call_count == 2
