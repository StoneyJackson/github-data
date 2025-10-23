"""Tests for ConfigFactory Phase 2 extensions.

Comprehensive test suite for Phase 2 scenario-specific and feature-specific
factory methods added to ConfigFactory.
"""

import pytest
from tests.shared.builders.config_factory import ConfigFactory
from src.config.settings import ApplicationConfig


class TestConfigFactoryPhase2ScenarioMethods:
    """Test scenario-specific factory methods from Phase 2."""

    def test_dependency_validation_config_pull_request_comments_valid(self):
        """Test dependency validation with valid PR comments dependency."""
        config = ConfigFactory.create_dependency_validation_config(
            feature="pull_request_comments", enabled=True, dependency_enabled=True
        )

        assert isinstance(config, ApplicationConfig)
        assert config.include_pull_request_comments is True
        assert config.include_pull_requests is True

    def test_dependency_validation_config_pull_request_comments_invalid(self):
        """Test dependency validation with invalid PR comments dependency."""
        config = ConfigFactory.create_dependency_validation_config(
            feature="pull_request_comments", enabled=True, dependency_enabled=False
        )

        assert isinstance(config, ApplicationConfig)
        assert config.include_pull_request_comments is True
        assert config.include_pull_requests is False

    def test_dependency_validation_config_pr_review_comments_valid(self):
        """Test dependency validation with valid PR review comments dependency."""
        config = ConfigFactory.create_dependency_validation_config(
            feature="pr_review_comments", enabled=True, dependency_enabled=True
        )

        assert isinstance(config, ApplicationConfig)
        assert config.include_pr_review_comments is True
        assert config.include_pr_reviews is True

    def test_dependency_validation_config_pr_review_comments_invalid(self):
        """Test dependency validation with invalid PR review comments dependency."""
        config = ConfigFactory.create_dependency_validation_config(
            feature="pr_review_comments", enabled=True, dependency_enabled=False
        )

        assert isinstance(config, ApplicationConfig)
        assert config.include_pr_review_comments is True
        assert config.include_pr_reviews is False

    def test_dependency_validation_config_sub_issues_valid(self):
        """Test dependency validation with valid sub-issues dependency."""
        config = ConfigFactory.create_dependency_validation_config(
            feature="sub_issues", enabled=True, dependency_enabled=True
        )

        assert isinstance(config, ApplicationConfig)
        assert config.include_sub_issues is True
        assert config.include_issues is True

    def test_dependency_validation_config_sub_issues_invalid(self):
        """Test dependency validation with invalid sub-issues dependency."""
        config = ConfigFactory.create_dependency_validation_config(
            feature="sub_issues", enabled=True, dependency_enabled=False
        )

        assert isinstance(config, ApplicationConfig)
        assert config.include_sub_issues is True
        assert config.include_issues is False

    def test_dependency_validation_config_unknown_feature(self):
        """Test dependency validation with unknown feature raises error."""
        with pytest.raises(ValueError, match="Unknown feature: unknown_feature"):
            ConfigFactory.create_dependency_validation_config(
                feature="unknown_feature", enabled=True, dependency_enabled=True
            )

    def test_dependency_validation_config_with_overrides(self):
        """Test dependency validation with additional overrides."""
        config = ConfigFactory.create_dependency_validation_config(
            feature="sub_issues",
            enabled=True,
            dependency_enabled=True,
            OPERATION="restore",
            GITHUB_REPO="custom/repo",
        )

        assert config.operation == "restore"
        assert config.github_repo == "custom/repo"
        assert config.include_sub_issues is True
        assert config.include_issues is True

    def test_boolean_parsing_config_true_values(self):
        """Test boolean parsing config with various true value formats."""
        true_values = ["true", "TRUE", "True", "yes", "YES", "on", "ON"]

        for value in true_values:
            config = ConfigFactory.create_boolean_parsing_config(
                field="INCLUDE_MILESTONES", value=value
            )
            assert config.include_milestones is True, f"Failed for value: {value}"

    def test_boolean_parsing_config_false_values(self):
        """Test boolean parsing config with various false value formats."""
        false_values = ["false", "FALSE", "False", "no", "NO", "off", "OFF"]

        for value in false_values:
            config = ConfigFactory.create_boolean_parsing_config(
                field="INCLUDE_MILESTONES", value=value
            )
            assert config.include_milestones is False, f"Failed for value: {value}"

    def test_boolean_parsing_config_legacy_values_raise_error(self):
        """Test that legacy boolean values 0/1 raise helpful errors."""
        legacy_values = ["0", "1"]

        for value in legacy_values:
            with pytest.raises(ValueError, match="uses legacy format"):
                ConfigFactory.create_boolean_parsing_config(
                    field="INCLUDE_MILESTONES", value=value
                )

    def test_boolean_parsing_config_with_overrides(self):
        """Test boolean parsing config with additional overrides."""
        config = ConfigFactory.create_boolean_parsing_config(
            field="INCLUDE_ISSUES",
            value="true",
            OPERATION="restore",
            DATA_PATH="/custom/path",
        )

        assert config.include_issues is True
        assert config.operation == "restore"
        assert str(config.data_path) == "/custom/path"

    def test_error_scenario_config_invalid_operation(self):
        """Test error scenario config with invalid operation value."""
        config = ConfigFactory.create_error_scenario_config(
            invalid_field="OPERATION", invalid_value="invalid_operation"
        )
        # Config creation succeeds, but validation should fail
        with pytest.raises(ValueError, match="Operation must be one of"):
            config.validate()

    def test_error_scenario_config_invalid_boolean_format(self):
        """Test error scenario config with invalid boolean format."""
        with pytest.raises(ValueError, match="uses legacy format"):
            ConfigFactory.create_error_scenario_config(
                invalid_field="INCLUDE_MILESTONES", invalid_value="1"
            )

    def test_error_scenario_config_with_overrides(self):
        """Test error scenario config with additional overrides."""
        config = ConfigFactory.create_error_scenario_config(
            invalid_field="OPERATION",
            invalid_value="invalid_operation",
            GITHUB_REPO="test/repo",
        )

        assert config.operation == "invalid_operation"
        assert config.github_repo == "test/repo"
        # Validation should fail for the invalid operation
        with pytest.raises(ValueError):
            config.validate()


class TestConfigFactoryPhase2FeatureMethods:
    """Test feature-specific factory methods from Phase 2."""

    def test_milestone_config(self):
        """Test milestone configuration factory method."""
        config = ConfigFactory.create_milestone_config()

        assert isinstance(config, ApplicationConfig)
        assert config.include_milestones is True
        # Other features should use defaults
        assert config.include_issues is True
        assert config.include_pull_requests is True

    def test_milestone_config_with_overrides(self):
        """Test milestone configuration with overrides."""
        config = ConfigFactory.create_milestone_config(
            OPERATION="restore", INCLUDE_ISSUES="false"
        )

        assert config.include_milestones is True
        assert config.operation == "restore"
        assert config.include_issues is False

    def test_git_only_config(self):
        """Test git-only configuration factory method."""
        config = ConfigFactory.create_git_only_config()

        assert isinstance(config, ApplicationConfig)
        assert config.include_git_repo is True
        # All other features should be disabled
        assert config.include_issues is False
        assert config.include_issue_comments is False
        assert config.include_pull_requests is False
        assert config.include_pull_request_comments is False
        assert config.include_pr_reviews is False
        assert config.include_pr_review_comments is False
        assert config.include_sub_issues is False
        assert config.include_milestones is False

    def test_git_only_config_with_overrides(self):
        """Test git-only configuration with overrides."""
        config = ConfigFactory.create_git_only_config(
            OPERATION="restore",
            GITHUB_REPO="custom/repo",  # Override repo instead of conflicting field
        )

        assert config.include_git_repo is True
        assert config.operation == "restore"
        assert config.github_repo == "custom/repo"
        # Issues should still be disabled as per git_only_config
        assert config.include_issues is False

    def test_comments_disabled_config(self):
        """Test comments disabled configuration factory method."""
        config = ConfigFactory.create_comments_disabled_config()

        assert isinstance(config, ApplicationConfig)
        assert config.include_issue_comments is False
        assert config.include_pull_request_comments is False
        assert config.include_pr_review_comments is False
        # Other features should use defaults
        assert config.include_issues is True
        assert config.include_pull_requests is True

    def test_comments_disabled_config_with_overrides(self):
        """Test comments disabled configuration with overrides."""
        config = ConfigFactory.create_comments_disabled_config(
            OPERATION="restore",
            GITHUB_REPO="custom/repo",  # Override repo instead of conflicting field
        )

        assert config.operation == "restore"
        assert config.github_repo == "custom/repo"
        # Comments should still be disabled as per comments_disabled_config
        assert config.include_issue_comments is False
        assert config.include_pull_request_comments is False
        assert config.include_pr_review_comments is False

    def test_reviews_only_config(self):
        """Test reviews-only configuration factory method."""
        config = ConfigFactory.create_reviews_only_config()

        assert isinstance(config, ApplicationConfig)
        assert config.include_pr_reviews is True
        assert config.include_pr_review_comments is True
        assert config.include_pull_requests is True  # Required for reviews
        # Other features should be disabled
        assert config.include_git_repo is False
        assert config.include_issues is False
        assert config.include_issue_comments is False
        assert config.include_pull_request_comments is False
        assert config.include_sub_issues is False
        assert config.include_milestones is False

    def test_reviews_only_config_with_overrides(self):
        """Test reviews-only configuration with overrides."""
        config = ConfigFactory.create_reviews_only_config(
            OPERATION="restore",
            GITHUB_REPO="custom/repo",  # Override repo instead of conflicting field
        )

        assert config.include_pr_reviews is True
        assert config.include_pr_review_comments is True
        assert config.operation == "restore"
        assert config.github_repo == "custom/repo"
        # Issues should still be disabled as per reviews_only_config
        assert config.include_issues is False

    def test_sub_issues_config(self):
        """Test sub-issues configuration factory method."""
        config = ConfigFactory.create_sub_issues_config()

        assert isinstance(config, ApplicationConfig)
        assert config.include_sub_issues is True
        assert config.include_issues is True  # Required for sub-issues
        # Other features use defaults
        assert config.include_pull_requests is True

    def test_sub_issues_config_with_overrides(self):
        """Test sub-issues configuration with overrides."""
        config = ConfigFactory.create_sub_issues_config(
            OPERATION="restore", INCLUDE_PULL_REQUESTS="false"
        )

        assert config.include_sub_issues is True
        assert config.include_issues is True
        assert config.operation == "restore"
        assert config.include_pull_requests is False


class TestConfigFactoryPhase2Integration:
    """Test integration between Phase 2 methods and existing functionality."""

    def test_phase2_methods_use_environment_pattern(self):
        """Test that all Phase 2 methods use environment variable pattern."""
        # Test that dependency validation creates proper environment
        config1 = ConfigFactory.create_dependency_validation_config(
            feature="sub_issues", enabled=True, dependency_enabled=True
        )

        # Test that feature-specific methods also work
        config2 = ConfigFactory.create_milestone_config()

        assert isinstance(config1, ApplicationConfig)
        assert isinstance(config2, ApplicationConfig)

    def test_phase2_methods_support_overrides(self):
        """Test that all Phase 2 methods support override parameters."""
        test_cases = [
            (ConfigFactory.create_milestone_config, {}),
            (ConfigFactory.create_git_only_config, {}),
            (ConfigFactory.create_comments_disabled_config, {}),
            (ConfigFactory.create_reviews_only_config, {}),
            (ConfigFactory.create_sub_issues_config, {}),
        ]

        for factory_method, kwargs in test_cases:
            config = factory_method(
                OPERATION="restore", GITHUB_REPO="test/override", **kwargs
            )

            assert config.operation == "restore"
            assert config.github_repo == "test/override"

    def test_phase2_methods_consistency_with_phase1(self):
        """Test that Phase 2 methods are consistent with Phase 1 patterns."""
        # Both should create valid ApplicationConfig instances
        phase1_config = ConfigFactory.create_save_config()
        phase2_config = ConfigFactory.create_milestone_config()

        assert isinstance(phase1_config, type(phase2_config))
        assert hasattr(phase1_config, "operation")
        assert hasattr(phase2_config, "operation")

    def test_boolean_parsing_config_consistency(self):
        """Test boolean parsing config consistency with ApplicationConfig behavior."""
        # Test that our boolean parsing matches ApplicationConfig's actual parsing
        config_true = ConfigFactory.create_boolean_parsing_config(
            field="INCLUDE_ISSUES", value="yes"
        )
        config_false = ConfigFactory.create_boolean_parsing_config(
            field="INCLUDE_ISSUES", value="no"
        )

        assert config_true.include_issues is True
        assert config_false.include_issues is False
