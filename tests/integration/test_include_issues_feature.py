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
    pytest.mark.issues,
]


class TestIncludeIssuesFeature:
    """Integration tests for INCLUDE_ISSUES environment variable."""

    def test_save_with_issues_enabled_by_default(
        self, temp_data_dir, github_service_mock
    ):
        """Test that issues are included by default in save operations."""
        env_vars = ConfigBuilder().with_data_path(str(temp_data_dir)).as_env_dict()
        # INCLUDE_ISSUES defaults to True in ConfigBuilder

        with patch.dict(os.environ, env_vars, clear=True):
            with patch(
                "src.github.create_github_service", return_value=github_service_mock
            ):
                with patch("src.storage.create_storage_service"):
                    with patch(
                        "src.operations.save.save_repository_data_with_config"
                    ) as mock_save:
                        main()

                        # Verify save was called with config that includes issues
                        mock_save.assert_called_once()
                        config = mock_save.call_args[0][0]  # First argument is config
                        assert config.include_issues is True

    def test_save_with_issues_explicitly_enabled(
        self, temp_data_dir, github_service_mock
    ):
        """Test save operation with INCLUDE_ISSUES=true."""
        env_vars = (
            ConfigBuilder()
            .with_data_path(str(temp_data_dir))
            .with_issues(True)
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
                        assert config.include_issues is True

    def test_save_with_issues_disabled(self, temp_data_dir, github_service_mock):
        """Test save operation with INCLUDE_ISSUES=false."""
        env_vars = (
            ConfigBuilder()
            .with_data_path(str(temp_data_dir))
            .with_issues(False)
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
                        assert config.include_issues is False

    def test_restore_with_issues_disabled(self, temp_data_dir, github_service_mock):
        """Test restore operation with INCLUDE_ISSUES=false."""
        env_vars = (
            ConfigBuilder()
            .with_operation("restore")
            .with_data_path(str(temp_data_dir))
            .with_issues(False)
            .as_env_dict()
        )

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
                        assert config.include_issues is False

    def test_issue_comments_dependency_violation(
        self, temp_data_dir, github_service_mock
    ):
        """Test that issue comments are ignored when issues are disabled."""
        env_vars = (
            ConfigBuilder()
            .with_data_path(str(temp_data_dir))
            .with_issues(False)
            .with_issue_comments(True)
            .as_env_dict()
        )

        with patch.dict(os.environ, env_vars, clear=True):
            with patch(
                "src.github.create_github_service", return_value=github_service_mock
            ):
                with patch("src.storage.create_storage_service"):
                    with patch("src.operations.save.save_repository_data_with_config"):
                        config = ApplicationConfig.from_environment()
                        config.validate()

                        # After validation, issue comments should be disabled
                        assert config.include_issues is False
                        assert config.include_issue_comments is False

    def test_boolean_parsing_edge_cases(self):
        """Test various value formats for INCLUDE_ISSUES."""
        base_env = ConfigBuilder().with_data_path("/tmp/test").as_env_dict()
        base_env.pop("INCLUDE_ISSUES", None)  # Remove so we can test individual values

        # Test boolean values
        boolean_test_cases = [
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

        for value, expected in boolean_test_cases:
            env_vars = {**base_env, "INCLUDE_ISSUES": value}
            with patch.dict(os.environ, env_vars, clear=True):
                config = ApplicationConfig.from_environment()
                assert (
                    config.include_issues == expected
                ), f"Failed for boolean value: '{value}'"

        # Test number specifications (new feature)
        number_test_cases = [
            ("1", {1}),
            ("5", {5}),
            ("1,3,5", {1, 3, 5}),
            ("1-3", {1, 2, 3}),
        ]

        for value, expected in number_test_cases:
            env_vars = {**base_env, "INCLUDE_ISSUES": value}
            with patch.dict(os.environ, env_vars, clear=True):
                config = ApplicationConfig.from_environment()
                assert (
                    config.include_issues == expected
                ), f"Failed for number spec: '{value}'"

        # Test invalid values (should raise errors)
        invalid_values = ["invalid", "0", "-1", "abc"]
        for value in invalid_values:
            env_vars = {**base_env, "INCLUDE_ISSUES": value}
            with patch.dict(os.environ, env_vars, clear=True):
                with pytest.raises(ValueError):
                    ApplicationConfig.from_environment()


# Use shared fixtures from tests.shared instead of local fixtures
# This follows project convention for fixture reuse
