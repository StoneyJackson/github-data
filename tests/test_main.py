"""Tests for the main module."""

import os
import pytest
from unittest.mock import patch
from src.main import _get_env_var, main

pytestmark = [pytest.mark.unit]


class TestGetEnvVar:
    """Test cases for _get_env_var function."""

    @patch.dict(os.environ, {"TEST_VAR": "test_value"})
    def test_get_existing_env_var(self):
        """Test getting an existing environment variable."""
        result = _get_env_var("TEST_VAR")
        assert result == "test_value"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_missing_optional_env_var(self):
        """Test getting a missing optional environment variable."""
        result = _get_env_var("MISSING_VAR", required=False)
        assert result is None

    @patch.dict(os.environ, {}, clear=True)
    def test_get_missing_required_env_var_exits(self):
        """Test that missing required environment variable causes exit."""
        with pytest.raises(SystemExit) as exc_info:
            _get_env_var("MISSING_VAR", required=True)
        assert exc_info.value.code == 1


class TestMain:
    """Test cases for main function."""

    @patch("src.operations.save.save_repository_data_with_services")
    @patch("src.github.create_github_service")
    @patch("src.storage.create_storage_service")
    @patch("src.main._get_required_env_var")
    @patch("src.main._get_env_var")
    @patch("builtins.print")
    def test_main_save_operation(
        self,
        mock_print,
        mock_get_env_var,
        mock_get_required_env_var,
        mock_create_storage,
        mock_create_github,
        mock_save,
    ):
        """Test main function with save operation."""
        mock_get_required_env_var.side_effect = lambda name: {
            "OPERATION": "save",
            "GITHUB_TOKEN": "token123",
            "GITHUB_REPO": "owner/repo",
        }.get(name)
        mock_get_env_var.return_value = "/data"

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

    @patch("src.operations.restore.restore_repository_data_with_services")
    @patch("src.github.create_github_service")
    @patch("src.storage.create_storage_service")
    @patch("src.main._get_required_env_var")
    @patch("src.main._get_env_var")
    @patch("builtins.print")
    def test_main_restore_operation(
        self,
        mock_print,
        mock_get_env_var,
        mock_get_required_env_var,
        mock_create_storage,
        mock_create_github,
        mock_restore,
    ):
        """Test main function with restore operation."""
        mock_get_required_env_var.side_effect = lambda name: {
            "OPERATION": "restore",
            "GITHUB_TOKEN": "token123",
            "GITHUB_REPO": "owner/repo",
        }.get(name)
        mock_get_env_var.return_value = "/data"

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

    @patch("src.main._get_required_env_var")
    @patch("src.main._get_env_var")
    def test_main_invalid_operation_exits(
        self, mock_get_env_var, mock_get_required_env_var
    ):
        """Test that invalid operation causes exit."""
        mock_get_required_env_var.side_effect = lambda name: {
            "OPERATION": "invalid",
            "GITHUB_TOKEN": "token123",
            "GITHUB_REPO": "owner/repo",
        }.get(name)
        mock_get_env_var.return_value = "/data"

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
