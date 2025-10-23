"""Tests for ConfigFactory Phase 1 extensions.

Tests the new environment variable factory methods and mock configuration
factory methods added in Phase 1 of the ConfigFactory implementation plan.
"""

from pathlib import Path
from unittest.mock import Mock, patch
from src.config.settings import ApplicationConfig
from tests.shared.builders.config_factory import ConfigFactory


class TestEnvironmentVariableFactories:
    """Test environment variable factory methods."""

    def test_create_base_env_dict_defaults(self):
        """Test create_base_env_dict returns correct defaults."""
        env_dict = ConfigFactory.create_base_env_dict()

        expected = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
            "DATA_PATH": "/tmp/test",
            "INCLUDE_GIT_REPO": "true",
            "INCLUDE_ISSUES": "true",
            "INCLUDE_ISSUE_COMMENTS": "true",
            "INCLUDE_PULL_REQUESTS": "true",
            "INCLUDE_PULL_REQUEST_COMMENTS": "true",
            "INCLUDE_PR_REVIEWS": "true",
            "INCLUDE_PR_REVIEW_COMMENTS": "true",
            "INCLUDE_SUB_ISSUES": "true",
            "INCLUDE_MILESTONES": "true",
        }

        assert env_dict == expected

    def test_create_base_env_dict_with_overrides(self):
        """Test create_base_env_dict applies overrides correctly."""
        env_dict = ConfigFactory.create_base_env_dict(
            OPERATION="restore", INCLUDE_MILESTONES="true", CUSTOM_FIELD="custom_value"
        )

        assert env_dict["OPERATION"] == "restore"
        assert env_dict["INCLUDE_MILESTONES"] == "true"
        assert env_dict["CUSTOM_FIELD"] == "custom_value"
        # Verify other defaults preserved
        assert env_dict["GITHUB_TOKEN"] == "test-token"
        assert env_dict["INCLUDE_ISSUES"] == "true"

    def test_create_save_env_dict(self):
        """Test create_save_env_dict sets operation to save."""
        env_dict = ConfigFactory.create_save_env_dict()

        assert env_dict["OPERATION"] == "save"
        # Should include all base defaults
        assert "GITHUB_TOKEN" in env_dict
        assert "INCLUDE_ISSUES" in env_dict

    def test_create_restore_env_dict(self):
        """Test create_restore_env_dict sets operation to restore."""
        env_dict = ConfigFactory.create_restore_env_dict()

        assert env_dict["OPERATION"] == "restore"
        # Should include all base defaults
        assert "GITHUB_TOKEN" in env_dict
        assert "INCLUDE_ISSUES" in env_dict

    def test_create_container_env_dict(self):
        """Test create_container_env_dict sets container-specific path."""
        env_dict = ConfigFactory.create_container_env_dict()

        assert env_dict["DATA_PATH"] == "/data"
        # Should include all base defaults
        assert env_dict["OPERATION"] == "save"
        assert "GITHUB_TOKEN" in env_dict

    def test_create_validation_env_dict(self):
        """Test create_validation_env_dict sets specific field."""
        env_dict = ConfigFactory.create_validation_env_dict(
            "INCLUDE_PULL_REQUESTS", "true"
        )

        assert env_dict["INCLUDE_PULL_REQUESTS"] == "true"
        # Should include all base defaults
        assert "GITHUB_TOKEN" in env_dict
        assert "OPERATION" in env_dict

    def test_create_validation_env_dict_with_overrides(self):
        """Test create_validation_env_dict with additional overrides."""
        env_dict = ConfigFactory.create_validation_env_dict(
            "INCLUDE_PULL_REQUESTS", "true", OPERATION="restore", CUSTOM_FIELD="test"
        )

        assert env_dict["INCLUDE_PULL_REQUESTS"] == "true"
        assert env_dict["OPERATION"] == "restore"
        assert env_dict["CUSTOM_FIELD"] == "test"


class TestMockConfigurationFactories:
    """Test mock configuration factory methods."""

    def test_create_mock_config_defaults(self):
        """Test create_mock_config creates mock with correct defaults."""
        mock_config = ConfigFactory.create_mock_config()

        assert isinstance(mock_config, Mock)
        assert mock_config._spec_class == ApplicationConfig

        # Verify default values
        assert mock_config.operation == "save"
        assert mock_config.github_token == "test-token"
        assert mock_config.repository_owner == "test-owner"
        assert mock_config.repository_name == "test-repo"
        assert mock_config.data_path == Path("/tmp/test")
        assert mock_config.include_git_repo is True
        assert mock_config.include_issues is True
        assert mock_config.include_issue_comments is True
        assert mock_config.include_pull_requests is True
        assert mock_config.include_pull_request_comments is True
        assert mock_config.include_pr_reviews is True
        assert mock_config.include_pr_review_comments is True
        assert mock_config.include_sub_issues is True
        assert mock_config.include_milestones is True

    def test_create_mock_config_with_overrides(self):
        """Test create_mock_config applies overrides correctly."""
        mock_config = ConfigFactory.create_mock_config(
            operation="restore",
            include_milestones=True,
            repository_owner="custom-owner",
        )

        assert mock_config.operation == "restore"
        assert mock_config.include_milestones is True
        assert mock_config.repository_owner == "custom-owner"
        # Verify other defaults preserved
        assert mock_config.github_token == "test-token"
        assert mock_config.include_issues is True

    def test_create_milestone_mock_config(self):
        """Test create_milestone_mock_config enables milestones."""
        mock_config = ConfigFactory.create_milestone_mock_config()

        assert mock_config.include_milestones is True
        # Should include all base defaults
        assert mock_config.operation == "save"
        assert mock_config.github_token == "test-token"

    def test_create_milestone_mock_config_with_overrides(self):
        """Test create_milestone_mock_config with additional overrides."""
        mock_config = ConfigFactory.create_milestone_mock_config(
            operation="restore", repository_owner="milestone-owner"
        )

        assert mock_config.include_milestones is True
        assert mock_config.operation == "restore"
        assert mock_config.repository_owner == "milestone-owner"

    def test_create_pr_mock_config(self):
        """Test create_pr_mock_config enables PR features."""
        mock_config = ConfigFactory.create_pr_mock_config()

        assert mock_config.include_pull_requests is True
        assert mock_config.include_pull_request_comments is True
        # Should include all base defaults
        assert mock_config.operation == "save"
        assert mock_config.github_token == "test-token"

    def test_create_pr_mock_config_with_overrides(self):
        """Test create_pr_mock_config with additional overrides."""
        mock_config = ConfigFactory.create_pr_mock_config(
            operation="restore", repository_name="pr-repo"
        )

        assert mock_config.include_pull_requests is True
        assert mock_config.include_pull_request_comments is True
        assert mock_config.operation == "restore"
        assert mock_config.repository_name == "pr-repo"


class TestUpdatedFactoryMethods:
    """Test updated factory methods use new environment variable patterns."""

    def test_create_save_config_uses_environment(self):
        """Test create_save_config uses environment variables."""
        config = ConfigFactory.create_save_config()

        assert config.operation == "save"
        assert config.github_token == "test-token"
        assert config.github_repo == "owner/repo"
        assert config.data_path == "/tmp/test"

    def test_create_restore_config_uses_environment(self):
        """Test create_restore_config uses environment variables."""
        config = ConfigFactory.create_restore_config()

        assert config.operation == "restore"
        assert config.github_token == "test-token"
        assert config.github_repo == "owner/repo"

    def test_create_minimal_config_disables_features(self):
        """Test create_minimal_config disables most features."""
        config = ConfigFactory.create_minimal_config()

        assert config.operation == "save"
        assert config.include_git_repo is False
        assert config.include_issues is False
        assert config.include_issue_comments is False
        assert config.include_pull_requests is False
        assert config.include_pull_request_comments is False
        assert config.include_pr_reviews is False
        assert config.include_pr_review_comments is False
        assert config.include_sub_issues is False
        assert config.include_milestones is False

    def test_create_full_config_enables_all_features(self):
        """Test create_full_config enables all features."""
        config = ConfigFactory.create_full_config()

        assert config.operation == "save"
        assert config.include_git_repo is True
        assert config.include_issues is True
        assert config.include_issue_comments is True
        assert config.include_pull_requests is True
        assert config.include_pull_request_comments is True
        assert config.include_pr_reviews is True
        assert config.include_pr_review_comments is True
        assert config.include_sub_issues is True
        assert config.include_milestones is True

    def test_create_pr_config_enables_pr_features(self):
        """Test create_pr_config enables PR features."""
        config = ConfigFactory.create_pr_config()

        assert config.include_pull_requests is True
        assert config.include_pull_request_comments is True
        assert config.include_pr_reviews is True
        assert config.include_pr_review_comments is True

    def test_create_issues_only_config_disables_non_issue_features(self):
        """Test create_issues_only_config disables non-issue features."""
        config = ConfigFactory.create_issues_only_config()

        # Issues and comments should be enabled (from base defaults)
        assert config.include_issues is True
        assert config.include_issue_comments is True

        # Other features should be disabled
        assert config.include_git_repo is False
        assert config.include_pull_requests is False
        assert config.include_pull_request_comments is False
        assert config.include_pr_reviews is False
        assert config.include_pr_review_comments is False
        assert config.include_sub_issues is False
        assert config.include_milestones is False

    def test_create_labels_only_config_enables_git_only(self):
        """Test create_labels_only_config enables minimal features."""
        config = ConfigFactory.create_labels_only_config()

        # Git repo should be disabled (set explicitly)
        assert config.include_git_repo is False

        # Other features should be disabled
        assert config.include_issues is False
        assert config.include_issue_comments is False
        assert config.include_pull_requests is False
        assert config.include_pull_request_comments is False
        assert config.include_pr_reviews is False
        assert config.include_pr_review_comments is False
        assert config.include_sub_issues is False
        assert config.include_milestones is False

    def test_factory_methods_accept_overrides(self):
        """Test that all factory methods accept override parameters."""
        # Test save config with overrides
        config = ConfigFactory.create_save_config(GITHUB_REPO="custom/repo")
        assert config.github_repo == "custom/repo"

        # Test restore config with overrides
        config = ConfigFactory.create_restore_config(DATA_PATH="/custom/path")
        assert config.data_path == "/custom/path"

        # Test minimal config with overrides
        config = ConfigFactory.create_minimal_config(GITHUB_REPO="custom/minimal-repo")
        assert config.github_repo == "custom/minimal-repo"

        # Test full config with overrides
        config = ConfigFactory.create_full_config(GITHUB_REPO="custom/full-repo")
        assert config.github_repo == "custom/full-repo"


class TestDirectConstructorMethods:
    """Test direct constructor methods for mocking scenarios."""

    def test_create_save_config_direct(self):
        """Test create_save_config_direct creates config with direct constructor."""
        config = ConfigFactory.create_save_config_direct(
            github_repo="direct/repo", include_milestones=False
        )

        assert config.operation == "save"
        assert config.github_repo == "direct/repo"
        assert config.include_milestones is False
        assert config.label_conflict_strategy == "skip"  # Should have real string value
        assert config.git_auth_method == "token"

    def test_create_restore_config_direct(self):
        """Test create_restore_config_direct creates config with direct constructor."""
        config = ConfigFactory.create_restore_config_direct(
            data_path="/direct/path", include_git_repo=False
        )

        assert config.operation == "restore"
        assert config.data_path == "/direct/path"
        assert config.include_git_repo is False
        assert config.label_conflict_strategy == "skip"  # Should have real string value
        assert config.git_auth_method == "token"

    def test_direct_methods_have_real_string_values(self):
        """Test that direct constructor methods create configs with real string values.

        Ensures configs have real strings, not mocks.
        """
        config = ConfigFactory.create_save_config_direct()

        # These should be real strings, not mocks
        assert isinstance(config.label_conflict_strategy, str)
        assert isinstance(config.git_auth_method, str)
        assert isinstance(config.github_token, str)
        assert isinstance(config.github_repo, str)
        assert isinstance(config.data_path, str)


class TestFactoryMethodIntegration:
    """Test integration between different factory methods."""

    def test_environment_and_config_consistency(self):
        """Test environment variables produce expected config values."""
        # Test that save environment produces save config
        env_dict = ConfigFactory.create_save_env_dict(INCLUDE_MILESTONES="true")

        with patch.dict("os.environ", env_dict, clear=True):
            config = ApplicationConfig.from_environment()

        assert config.operation == "save"
        assert config.include_milestones is True

    def test_container_environment_integration(self):
        """Test container environment variables work with config creation."""
        env_dict = ConfigFactory.create_container_env_dict(
            OPERATION="restore", INCLUDE_PULL_REQUESTS="true"
        )

        with patch.dict("os.environ", env_dict, clear=True):
            config = ApplicationConfig.from_environment()

        assert config.operation == "restore"
        assert config.data_path == "/data"
        assert config.include_pull_requests is True

    def test_validation_environment_integration(self):
        """Test validation environment variables work with config creation."""
        env_dict = ConfigFactory.create_validation_env_dict(
            "INCLUDE_SUB_ISSUES", "true", OPERATION="restore"
        )

        with patch.dict("os.environ", env_dict, clear=True):
            config = ApplicationConfig.from_environment()

        assert config.operation == "restore"
        assert config.include_sub_issues is True
