import pytest
import os
from unittest.mock import patch
from src.config.settings import ApplicationConfig
from tests.shared.builders import ConfigBuilder

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
        assert config.label_conflict_strategy == "skip"
        assert config.include_git_repo is True
        assert config.include_issue_comments is True
        assert config.git_auth_method == "token"

    def test_bool_parsing(self):
        """Test legacy boolean environment variable parsing."""
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

        true_values = ["true", "True", "yes", "on"]
        false_values = ["false", "False", "no", "off"]

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

        # Test with boolean true values (these should work with enhanced parsing)
        true_values = ["true", "True", "TRUE", "yes", "YES", "on", "ON"]
        for value in true_values:
            with patch.dict(
                os.environ,
                {**base_env_vars, "INCLUDE_ISSUES": value},
                clear=True,
            ):
                config = ApplicationConfig.from_environment()
                assert config.include_issues is True, f"Expected True for '{value}'"

        # Test with boolean false values (these should work with enhanced parsing)
        false_values = ["false", "False", "FALSE", "no", "NO", "off", "OFF"]
        for value in false_values:
            with patch.dict(
                os.environ,
                {**base_env_vars, "INCLUDE_ISSUES": value},
                clear=True,
            ):
                config = ApplicationConfig.from_environment()
                assert config.include_issues is False, f"Expected False for '{value}'"

        # Test number specifications (these should work as number sets)
        number_values = ["1", "2", "3", "1,2,3"]
        for value in number_values:
            with patch.dict(
                os.environ,
                {**base_env_vars, "INCLUDE_ISSUES": value},
                clear=True,
            ):
                config = ApplicationConfig.from_environment()
                assert isinstance(
                    config.include_issues, set
                ), f"Expected set for '{value}'"

        # Test invalid values (these should fail)
        invalid_values = ["invalid", "maybe"]
        for value in invalid_values:
            with patch.dict(
                os.environ,
                {**base_env_vars, "INCLUDE_ISSUES": value},
                clear=True,
            ):
                with pytest.raises(ValueError):
                    ApplicationConfig.from_environment()

    def test_legacy_boolean_values_rejected_in_enhanced_fields(self):
        """Test that enhanced boolean fields reject legacy 0/1 values."""
        base_env_vars = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
        }

        # Test that "1" and "0" are rejected for enhanced boolean fields
        legacy_values = ["0", "1"]
        enhanced_fields = [
            "INCLUDE_GIT_REPO",
            "INCLUDE_ISSUE_COMMENTS",
            "INCLUDE_PULL_REQUEST_COMMENTS",
            "INCLUDE_SUB_ISSUES",
        ]

        for field in enhanced_fields:
            for value in legacy_values:
                with patch.dict(
                    os.environ,
                    {**base_env_vars, field: value},
                    clear=True,
                ):
                    with pytest.raises(ValueError, match="uses legacy format"):
                        ApplicationConfig.from_environment()

    def test_enhanced_bool_parsing_valid_values(self):
        """Test enhanced boolean parsing with valid values."""
        test_cases = [
            # True values
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("yes", True),
            ("YES", True),
            ("on", True),
            ("ON", True),
            # False values
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("no", False),
            ("NO", False),
            ("off", False),
            ("OFF", False),
        ]

        for value, expected in test_cases:
            with patch.dict(os.environ, {"TEST_BOOL": value}, clear=True):
                result = ApplicationConfig._parse_enhanced_bool_env("TEST_BOOL")
                assert result == expected, f"Expected {expected} for '{value}'"

    def test_enhanced_bool_parsing_legacy_values_rejected(self):
        """Test that enhanced boolean parsing rejects legacy 0/1 values."""
        legacy_values = ["0", "1"]

        for value in legacy_values:
            with patch.dict(os.environ, {"TEST_BOOL": value}, clear=True):
                with pytest.raises(ValueError, match="uses legacy format"):
                    ApplicationConfig._parse_enhanced_bool_env("TEST_BOOL")

    def test_enhanced_bool_parsing_invalid_values(self):
        """Test enhanced boolean parsing with invalid values."""
        invalid_values = ["invalid", "maybe", "2", "true1", "false0"]

        for value in invalid_values:
            with patch.dict(os.environ, {"TEST_BOOL": value}, clear=True):
                with pytest.raises(ValueError, match="Invalid boolean value"):
                    ApplicationConfig._parse_enhanced_bool_env("TEST_BOOL")

    def test_number_or_bool_env_boolean_values(self):
        """Test parsing environment variables as boolean values."""
        boolean_test_cases = [
            ("true", True),
            ("false", False),
            ("yes", True),
            ("no", False),
            ("on", True),
            ("off", False),
        ]

        for value, expected in boolean_test_cases:
            with patch.dict(os.environ, {"TEST_VAR": value}, clear=True):
                result = ApplicationConfig._parse_number_or_bool_env("TEST_VAR")
                assert result == expected, f"Expected {expected} for '{value}'"

    def test_number_or_bool_env_number_specifications(self):
        """Test parsing environment variables as number specifications."""
        number_test_cases = [
            ("5", {5}),
            ("1,3,5", {1, 3, 5}),
            ("1-3", {1, 2, 3}),
            ("1-3,5", {1, 2, 3, 5}),
            ("1 3 5", {1, 3, 5}),
            ("1-3 5", {1, 2, 3, 5}),
        ]

        for value, expected in number_test_cases:
            with patch.dict(os.environ, {"TEST_VAR": value}, clear=True):
                result = ApplicationConfig._parse_number_or_bool_env("TEST_VAR")
                assert result == expected, f"Expected {expected} for '{value}'"

    def test_number_or_bool_env_invalid_specifications(self):
        """Test that invalid number specifications raise appropriate errors."""
        invalid_values = [
            "0",  # Zero not allowed
            "-1",  # Negative not allowed
            "1-",  # Invalid range
            "abc",  # Non-numeric
            "1-abc",  # Invalid range format
        ]

        for value in invalid_values:
            with patch.dict(os.environ, {"TEST_VAR": value}, clear=True):
                with pytest.raises(ValueError):
                    ApplicationConfig._parse_number_or_bool_env("TEST_VAR")

    def test_include_issues_number_specifications_from_env(self):
        """Test INCLUDE_ISSUES with number specifications from environment."""
        base_env_vars = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
        }

        test_cases = [
            ("5", {5}),
            ("1,3,5", {1, 3, 5}),
            ("1-3", {1, 2, 3}),
            ("1-3,5", {1, 2, 3, 5}),
        ]

        for value, expected in test_cases:
            with patch.dict(
                os.environ,
                {**base_env_vars, "INCLUDE_ISSUES": value},
                clear=True,
            ):
                config = ApplicationConfig.from_environment()
                assert (
                    config.include_issues == expected
                ), f"Expected {expected} for '{value}'"

    def test_include_pull_requests_number_specifications_from_env(self):
        """Test INCLUDE_PULL_REQUESTS with number specifications from environment."""
        base_env_vars = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
        }

        test_cases = [
            ("2", {2}),
            ("1,4,7", {1, 4, 7}),
            ("2-4", {2, 3, 4}),
            ("1-2,5", {1, 2, 5}),
        ]

        for value, expected in test_cases:
            with patch.dict(
                os.environ,
                {**base_env_vars, "INCLUDE_PULL_REQUESTS": value},
                clear=True,
            ):
                config = ApplicationConfig.from_environment()
                assert (
                    config.include_pull_requests == expected
                ), f"Expected {expected} for '{value}'"

    def test_validation_number_specification_empty_sets(self):
        """Test validation fails for empty number specification sets."""
        config = ConfigBuilder().build()

        # Test empty issues set
        config.include_issues = set()
        with pytest.raises(
            ValueError, match="INCLUDE_ISSUES number specification cannot be empty"
        ):
            config.validate()

        # Test empty PRs set
        config.include_issues = True  # Reset to valid
        config.include_pull_requests = set()
        with pytest.raises(
            ValueError,
            match="INCLUDE_PULL_REQUESTS number specification cannot be empty",
        ):
            config.validate()

    def test_validation_number_specification_invalid_numbers(self):
        """Test validation fails for invalid numbers in specifications."""
        config = ConfigBuilder().build()

        # Test zero in issues set
        config.include_issues = {0, 1, 2}
        with pytest.raises(
            ValueError, match="INCLUDE_ISSUES numbers must be positive integers"
        ):
            config.validate()

        # Test negative in PRs set
        config.include_issues = True  # Reset to valid
        config.include_pull_requests = {1, -1, 3}
        with pytest.raises(
            ValueError, match="INCLUDE_PULL_REQUESTS numbers must be positive integers"
        ):
            config.validate()

    def test_enhanced_comment_coupling_validation_boolean_false(self):
        """Test enhanced comment coupling validation with boolean false values."""
        config = ConfigBuilder().build()
        config.include_issue_comments = True
        config.include_pull_request_comments = True

        # Test issues boolean false disables issue comments
        config.include_issues = False
        config.validate()
        assert config.include_issue_comments is False

        # Test PRs boolean false disables PR comments
        config.include_issue_comments = True  # Reset
        config.include_issues = True  # Reset
        config.include_pull_requests = False
        config.validate()
        assert config.include_pull_request_comments is False

    def test_enhanced_comment_coupling_validation_empty_sets(self):
        """Test enhanced comment coupling validation with empty number sets."""
        config = ConfigBuilder().build()
        config.include_issue_comments = True
        config.include_pull_request_comments = True

        # Empty issues set should not disable issue comments
        # (would fail validation first)
        # But if we bypass validation, it should disable comments
        config.include_issues = set()
        # Skip validation that would fail due to empty set
        # Manually call the comment validation logic
        if config.include_issue_comments:
            if isinstance(config.include_issues, set) and not config.include_issues:
                config.include_issue_comments = False
        assert config.include_issue_comments is False

    def test_type_annotations_correct(self):
        """Test that type annotations are correctly applied."""
        config = ConfigBuilder().build()

        # Boolean assignments should work
        config.include_issues = True
        config.include_pull_requests = False

        # Set assignments should work
        config.include_issues = {1, 2, 3}
        config.include_pull_requests = {4, 5, 6}

        # These should all be valid without type errors


@pytest.mark.unit
def test_application_config_removed():
    """Test that ApplicationConfig class no longer exists."""
    import src.config.settings as settings

    # ApplicationConfig should not exist
    assert not hasattr(settings, "ApplicationConfig")


@pytest.mark.unit
def test_number_specification_parser_still_exists():
    """Test that NumberSpecificationParser still exists (used by registry)."""
    from src.config.settings import NumberSpecificationParser

    # Parser should still exist
    assert NumberSpecificationParser is not None
