"""Tests for the main module."""

import pytest
from unittest.mock import patch
from src.main import main

pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.backup_workflow,
    pytest.mark.restore_workflow,
]


# Environment variable functionality moved to ApplicationConfig


class TestMain:
    """Test cases for main function."""

    @patch("src.operations.save.save_repository_data_with_config")
    @patch("src.github.create_github_service")
    @patch("src.storage.create_storage_service")
    @patch("src.config.settings.ApplicationConfig.from_environment")
    @patch("builtins.print")
    def test_main_save_operation(
        self,
        mock_print,
        mock_config_from_env,
        mock_create_storage,
        mock_create_github,
        mock_save,
    ):
        """Test main function with save operation."""
        from src.config.settings import ApplicationConfig

        mock_config = ApplicationConfig(
            operation="save",
            github_token="token123",
            github_repo="owner/repo",
            data_path="/data",
            label_conflict_strategy="fail-if-existing",
            include_git_repo=False,
            include_issues=True,
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=True,
            include_sub_issues=False,
            git_auth_method="token",
        )
        mock_config_from_env.return_value = mock_config

        main()

        # Verify expected print calls
        expected_calls = [
            "GitHub Data - Save operation",
            "Repository: owner/repo",
            "Data path: /data",
            "Saving GitHub data...",
            "Save operation completed successfully",
        ]
        for call in expected_calls:
            assert any(call in str(args) for args, _ in mock_print.call_args_list)

    @patch("src.operations.restore.restore_repository_data_with_config")
    @patch("src.github.create_github_service")
    @patch("src.storage.create_storage_service")
    @patch("src.config.settings.ApplicationConfig.from_environment")
    @patch("builtins.print")
    def test_main_restore_operation(
        self,
        mock_print,
        mock_config_from_env,
        mock_create_storage,
        mock_create_github,
        mock_restore,
    ):
        """Test main function with restore operation."""
        from src.config.settings import ApplicationConfig

        mock_config = ApplicationConfig(
            operation="restore",
            github_token="token123",
            github_repo="owner/repo",
            data_path="/data",
            label_conflict_strategy="fail-if-existing",
            include_git_repo=False,
            include_issues=True,
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=True,
            include_sub_issues=False,
            git_auth_method="token",
        )
        mock_config_from_env.return_value = mock_config

        main()

        # Verify expected print calls
        expected_calls = [
            "GitHub Data - Restore operation",
            "Repository: owner/repo",
            "Data path: /data",
            "Restoring GitHub data...",
            "Restore operation completed successfully",
        ]
        for call in expected_calls:
            assert any(call in str(args) for args, _ in mock_print.call_args_list)

    @patch("src.config.settings.ApplicationConfig.from_environment")
    def test_main_invalid_operation_exits(self, mock_config_from_env):
        """Test that invalid operation causes exit."""
        from src.config.settings import ApplicationConfig

        mock_config = ApplicationConfig(
            operation="invalid",
            github_token="token123",
            github_repo="owner/repo",
            data_path="/data",
            label_conflict_strategy="fail-if-existing",
            include_git_repo=False,
            include_issues=True,
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=True,
            include_sub_issues=False,
            git_auth_method="token",
        )
        mock_config_from_env.return_value = mock_config

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
