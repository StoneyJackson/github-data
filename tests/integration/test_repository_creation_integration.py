"""Integration tests for repository creation during restore."""

import pytest
import os
from unittest.mock import patch, MagicMock
from github_data.main import Main


@pytest.mark.integration
class TestRepositoryCreationIntegration:
    """Integration tests for repository creation control."""

    def test_restore_creates_repository_when_missing(self):
        """Test full restore flow creates repository when missing."""
        with patch.dict(
            os.environ,
            {
                "OPERATION": "restore",
                "GITHUB_TOKEN": "test-token",
                "GITHUB_REPO": "owner/test-repo",
                "DATA_PATH": "/tmp/test-data",
                "CREATE_REPOSITORY_IF_MISSING": "true",
                "REPOSITORY_VISIBILITY": "public",
            },
        ):
            main = Main()
            # Load environment settings
            main._operation = "restore"
            main._repo_name = "owner/test-repo"
            main._load_create_repository_if_missing_from_environment()
            main._load_repository_visibility_from_environment()

            # Mock GitHub service
            main._github_service = MagicMock()
            main._github_service.get_repository_metadata.return_value = None

            # Should create repository
            with (
                patch("builtins.print"),
                patch.object(main, "_wait_for_repository_availability"),
            ):
                main._ensure_repository_exists()

            main._github_service.create_repository.assert_called_once_with(
                "owner/test-repo", private=False, description=""
            )

    def test_restore_fails_when_repository_missing_and_flag_false(self):
        """Test restore fails when repository missing and flag is false."""
        with patch.dict(
            os.environ,
            {
                "OPERATION": "restore",
                "GITHUB_TOKEN": "test-token",
                "GITHUB_REPO": "owner/test-repo",
                "DATA_PATH": "/tmp/test-data",
                "CREATE_REPOSITORY_IF_MISSING": "false",
            },
        ):
            main = Main()
            # Load environment settings
            main._operation = "restore"
            main._repo_name = "owner/test-repo"
            main._load_create_repository_if_missing_from_environment()

            # Mock GitHub service
            main._github_service = MagicMock()
            main._github_service.get_repository_metadata.return_value = None

            # Should exit with error
            with pytest.raises(SystemExit):
                main._ensure_repository_exists()

    def test_restore_proceeds_when_repository_exists(self):
        """Test restore proceeds normally when repository exists."""
        with patch.dict(
            os.environ,
            {
                "OPERATION": "restore",
                "GITHUB_TOKEN": "test-token",
                "GITHUB_REPO": "owner/test-repo",
                "DATA_PATH": "/tmp/test-data",
            },
        ):
            main = Main()

            # Mock GitHub service - repository exists
            main._github_service = MagicMock()
            main._github_service.get_repository_metadata.return_value = {"id": 123}

            # Should not create repository
            main._ensure_repository_exists()

            main._github_service.create_repository.assert_not_called()
