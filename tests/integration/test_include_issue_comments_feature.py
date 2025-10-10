import pytest
import os
from unittest.mock import patch
from src.main import main
from src.config.settings import ApplicationConfig
from tests.shared.builders import ConfigBuilder

# Test markers for organization and selective execution
pytestmark = [
    pytest.mark.integration,
    pytest.mark.medium,
    pytest.mark.include_issue_comments,
]


class TestIncludeIssueCommentsFeature:
    """Integration tests for INCLUDE_ISSUE_COMMENTS environment variable."""

    def test_save_with_comments_enabled_by_default(
        self, temp_data_dir, github_service_mock
    ):
        """Test that comments are included by default in save operations."""
        env_vars = ConfigBuilder().with_data_path(str(temp_data_dir)).as_env_dict()
        # INCLUDE_ISSUE_COMMENTS defaults to True in ConfigBuilder

        with patch.dict(os.environ, env_vars, clear=True):
            with patch(
                "src.github.create_github_service", return_value=github_service_mock
            ):
                with patch("src.storage.create_storage_service"):
                    with patch(
                        "src.operations.save.save_repository_data_with_config"
                    ) as mock_save:
                        main()

                        # Verify save was called with config that includes comments
                        mock_save.assert_called_once()
                        config = mock_save.call_args[0][0]  # First argument is config
                        assert config.include_issue_comments is True

    def test_save_with_comments_explicitly_enabled(
        self, temp_data_dir, github_service_mock
    ):
        """Test save operation with INCLUDE_ISSUE_COMMENTS=true."""
        env_vars = (
            ConfigBuilder()
            .with_data_path(str(temp_data_dir))
            .with_issue_comments(True)
            .as_env_dict()
        )

        with patch.dict(os.environ, env_vars, clear=True):
            with patch(
                "src.github.create_github_service", return_value=github_service_mock
            ):
                with patch("src.storage.create_storage_service"):
                    with patch(
                        "src.operations.save.save_repository_data_with_config"
                    ) as mock_save:
                        main()

                        config = mock_save.call_args[0][0]
                        assert config.include_issue_comments is True

    def test_save_with_comments_disabled(self, temp_data_dir, github_service_mock):
        """Test save operation with INCLUDE_ISSUE_COMMENTS=false."""
        env_vars = (
            ConfigBuilder()
            .with_data_path(str(temp_data_dir))
            .with_issue_comments(False)
            .as_env_dict()
        )

        with patch.dict(os.environ, env_vars, clear=True):
            with patch(
                "src.github.create_github_service", return_value=github_service_mock
            ):
                with patch("src.storage.create_storage_service"):
                    with patch(
                        "src.operations.save.save_repository_data_with_config"
                    ) as mock_save:
                        main()

                        config = mock_save.call_args[0][0]
                        assert config.include_issue_comments is False

    def test_restore_with_comments_disabled(self, temp_data_dir, github_service_mock):
        """Test restore operation with INCLUDE_ISSUE_COMMENTS=false."""
        env_vars = {
            "OPERATION": "restore",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
            "DATA_PATH": str(temp_data_dir),
            "INCLUDE_ISSUE_COMMENTS": "false",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch(
                "src.github.create_github_service", return_value=github_service_mock
            ):
                with patch("src.storage.create_storage_service"):
                    with patch(
                        "src.operations.restore."
                        "restore.restore_repository_data_with_config"
                    ) as mock_restore:
                        main()

                        config = mock_restore.call_args[0][0]
                        assert config.include_issue_comments is False

    def test_boolean_parsing_edge_cases(self):
        """Test various boolean value formats for INCLUDE_ISSUE_COMMENTS."""
        # Valid enhanced boolean values
        valid_test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("yes", True),
            ("YES", True),
            ("on", True),
            ("ON", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("no", False),
            ("NO", False),
            ("off", False),
            ("OFF", False),
        ]

        base_env = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
            "DATA_PATH": "/tmp/test",
        }

        # Test valid values
        for value, expected in valid_test_cases:
            env_vars = {**base_env, "INCLUDE_ISSUE_COMMENTS": value}

            with patch.dict(os.environ, env_vars, clear=True):
                config = ApplicationConfig.from_environment()
                assert (
                    config.include_issue_comments == expected
                ), f"Failed for value: '{value}'"

        # Test that legacy values are rejected
        legacy_values = ["0", "1"]
        for value in legacy_values:
            env_vars = {**base_env, "INCLUDE_ISSUE_COMMENTS": value}
            with patch.dict(os.environ, env_vars, clear=True):
                with pytest.raises(ValueError, match="uses legacy format"):
                    ApplicationConfig.from_environment()

        # Test that invalid values are rejected
        invalid_values = ["invalid", "maybe"]
        for value in invalid_values:
            env_vars = {**base_env, "INCLUDE_ISSUE_COMMENTS": value}
            with patch.dict(os.environ, env_vars, clear=True):
                with pytest.raises(ValueError, match="Invalid boolean value"):
                    ApplicationConfig.from_environment()


# Use shared fixtures from tests.shared instead of local fixtures
# This follows project convention for fixture reuse
