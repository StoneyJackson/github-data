import pytest
import os
from unittest.mock import patch
from src.config.settings import ApplicationConfig
from tests.shared.builders import ConfigBuilder, ConfigFactory

# Import fixtures from shared fixtures
pytest_plugins = ["tests.shared.fixtures.config_fixtures"]


class TestApplicationConfig:
    """Test cases for ApplicationConfig."""

    def test_from_environment_with_all_required_vars(self):
        """Test configuration creation with all required environment variables."""
        env_vars = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
            "DATA_PATH": "/tmp/data",
            "INCLUDE_ISSUE_COMMENTS": "true",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        assert config.operation == "save"
        assert config.github_token == "test-token"
        assert config.github_repo == "owner/repo"
        assert config.data_path == "/tmp/data"
        assert config.include_issue_comments is True

    def test_from_environment_missing_required_var(self):
        """Test configuration creation fails with missing required variable."""
        env_vars = {
            "OPERATION": "save",
            # Missing GITHUB_TOKEN
            "GITHUB_REPO": "owner/repo",
            "DATA_PATH": "/tmp/data",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(
                ValueError, match="Required environment variable GITHUB_TOKEN"
            ):
                ApplicationConfig.from_environment()

    def test_from_environment_with_defaults(self):
        """Test configuration creation with default values."""
        env_vars = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
            # DATA_PATH will use default
            # LABEL_CONFLICT_STRATEGY will use default
            # INCLUDE_GIT_REPO will use default
            # INCLUDE_ISSUE_COMMENTS will use default
            # GIT_AUTH_METHOD will use default
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        assert config.data_path == "/data"
        assert config.label_conflict_strategy == "fail-if-existing"
        assert config.include_git_repo is True
        assert config.include_issue_comments is True
        assert config.git_auth_method == "token"

    def test_bool_parsing(self):
        """Test boolean environment variable parsing."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("", False),
        ]

        for value, expected in test_cases:
            with patch.dict(os.environ, {"TEST_BOOL": value}, clear=True):
                result = ApplicationConfig._parse_bool_env("TEST_BOOL")
                assert result == expected, f"Expected {expected} for '{value}'"

    def test_bool_parsing_with_default(self):
        """Test boolean parsing with default values."""
        # Test with missing environment variable
        with patch.dict(os.environ, {}, clear=True):
            result = ApplicationConfig._parse_bool_env("MISSING_VAR", default=True)
            assert result is True

            result = ApplicationConfig._parse_bool_env("MISSING_VAR", default=False)
            assert result is False

    def test_validation_valid_operation(self, base_config):
        """Test validation passes for valid operation."""
        base_config.operation = "save"
        base_config.validate()  # Should not raise

        base_config.operation = "restore"
        base_config.validate()  # Should not raise

    def test_validation_invalid_operation(self, base_config):
        """Test validation fails for invalid operation."""
        base_config.operation = "invalid"
        with pytest.raises(ValueError, match="Operation must be one of"):
            base_config.validate()

    def test_validation_valid_conflict_strategy(self, base_config):
        """Test validation passes for valid conflict strategies."""
        valid_strategies = ["fail-if-existing", "skip", "overwrite"]
        for strategy in valid_strategies:
            base_config.label_conflict_strategy = strategy
            base_config.validate()  # Should not raise

    def test_validation_invalid_conflict_strategy(self, base_config):
        """Test validation fails for invalid conflict strategy."""
        base_config.label_conflict_strategy = "invalid"
        with pytest.raises(ValueError, match="Label conflict strategy must be one of"):
            base_config.validate()

    def test_validation_valid_auth_method(self, base_config):
        """Test validation passes for valid auth methods."""
        valid_methods = ["token", "ssh"]
        for method in valid_methods:
            base_config.git_auth_method = method
            base_config.validate()  # Should not raise

    def test_validation_invalid_auth_method(self, base_config):
        """Test validation fails for invalid auth method."""
        base_config.git_auth_method = "invalid"
        with pytest.raises(ValueError, match="Git auth method must be one of"):
            base_config.validate()

    def test_get_required_env_success(self):
        """Test getting required environment variable successfully."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}, clear=True):
            result = ApplicationConfig._get_required_env("TEST_VAR")
            assert result == "test_value"

    def test_get_required_env_missing(self):
        """Test getting required environment variable fails when missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="Required environment variable TEST_VAR"
            ):
                ApplicationConfig._get_required_env("TEST_VAR")

    def test_get_env_with_default(self):
        """Test getting environment variable with default."""
        # Test with existing variable
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}, clear=True):
            result = ApplicationConfig._get_env_with_default("TEST_VAR", "default")
            assert result == "test_value"

        # Test with missing variable
        with patch.dict(os.environ, {}, clear=True):
            result = ApplicationConfig._get_env_with_default("TEST_VAR", "default")
            assert result == "default"

    def test_include_pull_request_comments_parsing_from_env(self):
        """Test INCLUDE_PULL_REQUEST_COMMENTS environment variable parsing."""
        base_env_vars = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
        }

        # Test with explicit true
        with patch.dict(
            os.environ,
            {**base_env_vars, "INCLUDE_PULL_REQUEST_COMMENTS": "true"},
            clear=True,
        ):
            config = ApplicationConfig.from_environment()
            assert config.include_pull_request_comments is True

        # Test with explicit false
        with patch.dict(
            os.environ,
            {**base_env_vars, "INCLUDE_PULL_REQUEST_COMMENTS": "false"},
            clear=True,
        ):
            config = ApplicationConfig.from_environment()
            assert config.include_pull_request_comments is False

        # Test with default (should be True)
        with patch.dict(os.environ, base_env_vars, clear=True):
            config = ApplicationConfig.from_environment()
            assert config.include_pull_request_comments is True

    def test_include_pull_request_comments_various_bool_values(self):
        """Test INCLUDE_PULL_REQUEST_COMMENTS with various boolean representations."""
        base_env_vars = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
        }

        true_values = ["true", "True", "1", "yes", "on"]
        false_values = ["false", "False", "0", "no", "off"]

        for value in true_values:
            with patch.dict(
                os.environ,
                {**base_env_vars, "INCLUDE_PULL_REQUEST_COMMENTS": value},
                clear=True,
            ):
                config = ApplicationConfig.from_environment()
                assert (
                    config.include_pull_request_comments is True
                ), f"Expected True for '{value}'"

        for value in false_values:
            with patch.dict(
                os.environ,
                {**base_env_vars, "INCLUDE_PULL_REQUEST_COMMENTS": value},
                clear=True,
            ):
                config = ApplicationConfig.from_environment()
                assert (
                    config.include_pull_request_comments is False
                ), f"Expected False for '{value}'"

    def test_include_issues_parsing_from_env(self):
        """Test INCLUDE_ISSUES environment variable parsing."""
        base_env_vars = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
            "DATA_PATH": "/tmp/test",
        }

        # Test with True value
        with patch.dict(
            os.environ,
            {**base_env_vars, "INCLUDE_ISSUES": "true"},
            clear=True,
        ):
            config = ApplicationConfig.from_environment()
            assert config.include_issues is True

        # Test with False value
        with patch.dict(
            os.environ,
            {**base_env_vars, "INCLUDE_ISSUES": "false"},
            clear=True,
        ):
            config = ApplicationConfig.from_environment()
            assert config.include_issues is False

    def test_include_issues_boolean_parsing_edge_cases(self):
        """Test INCLUDE_ISSUES with various boolean representations."""
        base_env_vars = ConfigBuilder().with_data_path("/tmp/test").as_env_dict()

        # True values
        true_values = ["true", "True", "TRUE", "1", "yes", "YES", "on", "ON"]
        for value in true_values:
            with patch.dict(
                os.environ,
                {**base_env_vars, "INCLUDE_ISSUES": value},
                clear=True,
            ):
                config = ApplicationConfig.from_environment()
                assert config.include_issues is True, f"Expected True for '{value}'"

        # False values
        false_values = [
            "false",
            "False",
            "FALSE",
            "0",
            "no",
            "NO",
            "off",
            "OFF",
            "invalid",
        ]
        for value in false_values:
            with patch.dict(
                os.environ,
                {**base_env_vars, "INCLUDE_ISSUES": value},
                clear=True,
            ):
                config = ApplicationConfig.from_environment()
                assert config.include_issues is False, f"Expected False for '{value}'"
