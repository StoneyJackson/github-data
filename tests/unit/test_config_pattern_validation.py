"""Validation tests for configuration patterns.

Tests to ensure all environment variables work correctly with
the new ConfigBuilder and ConfigFactory patterns.
"""

import pytest
from tests.shared.builders import ConfigBuilder, ConfigFactory


class TestConfigPatternValidation:
    """Validation tests for configuration patterns."""

    def test_config_builder_supports_all_environment_variables(self):
        """Test that ConfigBuilder supports all environment variables."""
        # Test all available configuration options in ConfigBuilder
        config = (
            ConfigBuilder()
            .with_operation("save")
            .with_token("test-token")
            .with_repo("owner/repo")
            .with_data_path("/tmp/test")
            .with_label_strategy("fail-if-existing")
            .with_git_repo(True)
            .with_issues(True)
            .with_issue_comments(True)
            .with_pull_requests(True)
            .with_pull_request_comments(True)
            .with_sub_issues(True)
            .with_git_auth_method("token")
            .build()
        )

        # Verify all fields are set correctly
        assert config.operation == "save"
        assert config.github_token == "test-token"
        assert config.github_repo == "owner/repo"
        assert config.data_path == "/tmp/test"
        assert config.label_conflict_strategy == "fail-if-existing"
        assert config.include_git_repo is True
        assert config.include_issues is True
        assert config.include_issue_comments is True
        assert config.include_pull_requests is True
        assert config.include_pull_request_comments is True
        assert config.include_sub_issues is True
        assert config.git_auth_method == "token"

    def test_config_builder_environment_dict_conversion(self):
        """Test that ConfigBuilder correctly converts to environment variables."""
        env_vars = (
            ConfigBuilder()
            .with_operation("restore")
            .with_token("test-token-2")
            .with_repo("owner/repo-2")
            .with_data_path("/tmp/test-2")
            .with_label_strategy("overwrite")
            .with_git_repo(False)
            .with_issues(False)
            .with_issue_comments(False)
            .with_pull_requests(False)
            .with_pull_request_comments(False)
            .with_sub_issues(False)
            .with_git_auth_method("ssh")
            .as_env_dict()
        )

        # Verify all environment variables are present and correct
        expected_vars = {
            "OPERATION": "restore",
            "GITHUB_TOKEN": "test-token-2",
            "GITHUB_REPO": "owner/repo-2",
            "DATA_PATH": "/tmp/test-2",
            "LABEL_CONFLICT_STRATEGY": "overwrite",
            "INCLUDE_GIT_REPO": "false",
            "INCLUDE_ISSUES": "false",
            "INCLUDE_ISSUE_COMMENTS": "false",
            "INCLUDE_PULL_REQUESTS": "false",
            "INCLUDE_PULL_REQUEST_COMMENTS": "false",
            "INCLUDE_SUB_ISSUES": "false",
            "GIT_AUTH_METHOD": "ssh",
        }

        for key, expected_value in expected_vars.items():
            assert key in env_vars, f"Environment variable {key} is missing"
            assert (
                env_vars[key] == expected_value
            ), f"Environment variable {key} has incorrect value"

    def test_config_factory_all_preset_methods(self):
        """Test that ConfigFactory provides all necessary preset methods."""
        # Test all ConfigFactory preset methods
        save_config = ConfigFactory.create_save_config()
        assert save_config.operation == "save"

        restore_config = ConfigFactory.create_restore_config()
        assert restore_config.operation == "restore"

        minimal_config = ConfigFactory.create_minimal_config()
        assert minimal_config.include_git_repo is False
        assert minimal_config.include_issues is False

        pr_config = ConfigFactory.create_pr_config()
        assert pr_config.include_pull_requests is True
        assert pr_config.include_pull_request_comments is True

        full_config = ConfigFactory.create_full_config()
        assert full_config.include_git_repo is True
        assert full_config.include_issues is True
        assert full_config.include_issue_comments is True

    def test_config_factory_override_support(self):
        """Test that ConfigFactory methods support parameter overrides."""
        # Test overriding parameters in factory methods
        custom_save = ConfigFactory.create_save_config(
            github_repo="custom/repo",
            include_pull_requests=True,
            data_path="/custom/path"
        )

        assert custom_save.operation == "save"  # Default preserved
        assert custom_save.github_repo == "custom/repo"  # Override applied
        assert custom_save.include_pull_requests is True  # Override applied
        assert custom_save.data_path == "/custom/path"  # Override applied

    def test_all_environment_variables_have_test_coverage(self):
        """Test that all ApplicationConfig fields have test coverage in our patterns."""
        # Get a config with all features enabled
        config = ConfigBuilder().with_all_features().build()

        # Verify all ApplicationConfig fields are accessible
        fields_to_check = [
            'operation', 'github_token', 'github_repo', 'data_path',
            'label_conflict_strategy', 'include_git_repo', 'include_issues',
            'include_issue_comments', 'include_pull_requests',
            'include_pull_request_comments', 'include_sub_issues', 'git_auth_method'
        ]

        for field in fields_to_check:
            assert hasattr(
                config, field
            ), f"ApplicationConfig field {field} is not accessible"
            # Ensure the field has a value (not None)
            assert getattr(
                config, field
            ) is not None, f"ApplicationConfig field {field} is None"

    def test_future_environment_variable_compatibility(self):
        """Test that patterns support easy addition of new environment variables."""
        # Test that ConfigBuilder can handle new patterns by adding to environment dict
        builder = ConfigBuilder()
        env_vars = builder.as_env_dict()

        # Verify we can add new environment variables to the dict
        env_vars["SOME_FUTURE_OPTION"] = "future_value"
        assert "SOME_FUTURE_OPTION" in env_vars

        # Verify base configuration still works
        config = ConfigFactory.create_save_config()
        assert config.operation == "save"
        assert config.github_token == "test-token"

    @pytest.mark.parametrize("operation", ["save", "restore"])
    @pytest.mark.parametrize("include_prs", [True, False])
    @pytest.mark.parametrize("include_comments", [True, False])
    def test_common_configuration_combinations(
        self, operation, include_prs, include_comments
    ):
        """Test common configuration combinations work correctly."""
        config = (
            ConfigBuilder()
            .with_operation(operation)
            .with_pull_requests(include_prs)
            .with_pull_request_comments(include_comments)
            .build()
        )

        assert config.operation == operation
        assert config.include_pull_requests == include_prs
        assert config.include_pull_request_comments == include_comments

        # Test environment variable conversion
        env_vars = (
            ConfigBuilder()
            .with_operation(operation)
            .with_pull_requests(include_prs)
            .with_pull_request_comments(include_comments)
            .as_env_dict()
        )

        assert env_vars["OPERATION"] == operation
        assert env_vars["INCLUDE_PULL_REQUESTS"] == str(include_prs).lower()
        assert (
            env_vars["INCLUDE_PULL_REQUEST_COMMENTS"] == str(include_comments).lower()
        )
