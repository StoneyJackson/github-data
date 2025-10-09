"""Test the new configuration patterns from Phase 1.

This test file validates the new ConfigBuilder, ConfigFactory,
and enhanced fixture patterns work correctly.
"""

import os
from unittest.mock import patch

from tests.shared.builders import ConfigBuilder, ConfigFactory
from tests.shared.fixtures.env_fixtures import (
    env_config,
    make_env_vars,
)
from src.config.settings import ApplicationConfig


class TestConfigBuilder:
    """Test the ConfigBuilder pattern."""

    def test_default_configuration(self):
        """Test builder creates valid default configuration."""
        config = ConfigBuilder().build()

        assert config.operation == "save"
        assert config.github_token == "test-token"
        assert config.github_repo == "test-owner/test-repo"
        assert config.data_path == "/tmp/test-data"
        assert config.include_issues is True
        assert config.include_pull_requests is False

    def test_fluent_api_chaining(self):
        """Test fluent API allows method chaining."""
        config = (
            ConfigBuilder()
            .with_operation("restore")
            .with_repo("owner/repo")
            .with_pr_features()
            .build()
        )

        assert config.operation == "restore"
        assert config.github_repo == "owner/repo"
        assert config.include_pull_requests is True
        assert config.include_pull_request_comments is True

    def test_feature_shortcuts(self):
        """Test feature shortcut methods."""
        # Test minimal features
        config = ConfigBuilder().with_minimal_features().build()
        assert config.include_git_repo is False
        assert config.include_issues is False
        assert config.include_pull_requests is False

        # Test all features
        config = ConfigBuilder().with_all_features().build()
        assert config.include_git_repo is True
        assert config.include_issues is True
        assert config.include_pull_requests is True
        assert config.include_sub_issues is True

    def test_as_env_dict(self):
        """Test conversion to environment variables."""
        env_vars = (
            ConfigBuilder().with_operation("restore").with_pr_features().as_env_dict()
        )

        assert env_vars["OPERATION"] == "restore"
        assert env_vars["INCLUDE_PULL_REQUESTS"] == "true"
        assert env_vars["INCLUDE_PULL_REQUEST_COMMENTS"] == "true"
        assert env_vars["INCLUDE_ISSUES"] == "true"  # default


class TestConfigFactory:
    """Test the ConfigFactory pattern."""

    def test_save_config_creation(self):
        """Test save config factory method."""
        config = ConfigFactory.create_save_config()

        assert config.operation == "save"
        assert config.github_token == "test-token"
        assert config.include_issues is True

    def test_restore_config_creation(self):
        """Test restore config factory method."""
        config = ConfigFactory.create_restore_config()

        assert config.operation == "restore"
        assert config.github_token == "test-token"
        assert config.include_issues is True

    def test_minimal_config_creation(self):
        """Test minimal config factory method."""
        config = ConfigFactory.create_minimal_config()

        assert config.operation == "save"
        assert config.include_git_repo is False
        assert config.include_issues is False
        assert config.include_pull_requests is False

    def test_pr_config_creation(self):
        """Test PR config factory method."""
        config = ConfigFactory.create_pr_config()

        assert config.include_pull_requests is True
        assert config.include_pull_request_comments is True
        assert config.include_issues is True  # default preserved

    def test_factory_with_overrides(self):
        """Test factory methods with custom overrides."""
        config = ConfigFactory.create_save_config(
            github_repo="custom/repo", include_sub_issues=True
        )

        assert config.github_repo == "custom/repo"
        assert config.include_sub_issues is True
        assert config.operation == "save"  # default preserved


class TestEnvFixtures:
    """Test the enhanced environment fixtures."""

    def test_minimal_env_vars_fixture(self, minimal_env_vars):
        """Test minimal environment variables fixture."""
        assert minimal_env_vars["OPERATION"] == "save"
        assert minimal_env_vars["GITHUB_TOKEN"] == "test-token"
        assert minimal_env_vars["GITHUB_REPO"] == "test-owner/test-repo"
        assert len(minimal_env_vars) == 3  # Only required vars

    def test_standard_env_vars_fixture(self, standard_env_vars):
        """Test standard environment variables fixture."""
        assert standard_env_vars["OPERATION"] == "save"
        assert standard_env_vars["INCLUDE_ISSUES"] == "true"
        assert standard_env_vars["INCLUDE_PULL_REQUESTS"] == "false"
        assert len(standard_env_vars) > 3  # Includes defaults

    def test_pr_enabled_env_vars_fixture(self, pr_enabled_env_vars):
        """Test PR-enabled environment variables fixture."""
        assert pr_enabled_env_vars["INCLUDE_PULL_REQUESTS"] == "true"
        assert pr_enabled_env_vars["INCLUDE_PULL_REQUEST_COMMENTS"] == "true"

    def test_config_builder_fixture(self, config_builder):
        """Test config builder fixture provides fresh instance."""
        config1 = config_builder.with_operation("save").build()
        config2 = config_builder.with_operation("restore").build()

        # Both should work since it's a fresh instance
        assert config1.operation == "save"
        assert config2.operation == "restore"

    def test_config_factory_fixture(self, config_factory):
        """Test config factory fixture provides access to factory."""
        config = config_factory.create_minimal_config()
        assert config.include_issues is False

    def test_env_config_context_manager(self):
        """Test the env_config context manager."""
        with env_config(INCLUDE_PULL_REQUESTS="true") as config:
            assert config.include_pull_requests is True
            assert config.github_token == "test-token"  # default preserved

    def test_make_env_vars_helper(self):
        """Test the make_env_vars helper function."""
        env_vars = make_env_vars(OPERATION="restore", INCLUDE_PULL_REQUESTS="true")

        assert env_vars["OPERATION"] == "restore"
        assert env_vars["INCLUDE_PULL_REQUESTS"] == "true"
        assert env_vars["GITHUB_TOKEN"] == "test-token"  # default


class TestIntegrationPatterns:
    """Test integration between different patterns."""

    def test_builder_to_env_vars_to_config(self):
        """Test round-trip: builder -> env vars -> config."""
        # Create env vars using builder
        env_vars = (
            ConfigBuilder().with_operation("restore").with_pr_features().as_env_dict()
        )

        # Use env vars to create config
        with patch.dict(os.environ, env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        assert config.operation == "restore"
        assert config.include_pull_requests is True
        assert config.include_pull_request_comments is True

    def test_factory_matches_builder(self):
        """Test factory and builder produce equivalent configs."""
        factory_config = ConfigFactory.create_pr_config()

        builder_config = ConfigBuilder().with_pr_features().build()

        # Should have same core settings
        assert (
            factory_config.include_pull_requests == builder_config.include_pull_requests
        )
        assert (
            factory_config.include_pull_request_comments
            == builder_config.include_pull_request_comments
        )
        assert factory_config.operation == builder_config.operation

    def test_patterns_support_new_environment_variables(self):
        """Test patterns would handle new environment variables gracefully."""
        # This test validates that our patterns are extensible

        # Builder should work with custom values for existing fields
        config = ConfigBuilder().with_custom(data_path="/custom/path").build()

        assert config.data_path == "/custom/path"

        # Factory should work with overrides
        config = ConfigFactory.create_save_config(data_path="/factory/path")
        assert config.data_path == "/factory/path"

        # Environment patterns should handle additional vars
        env_vars = make_env_vars(DATA_PATH="/env/path")
        assert env_vars["DATA_PATH"] == "/env/path"
