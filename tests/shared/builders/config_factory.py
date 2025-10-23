"""Configuration factory for common test scenarios.

Provides static methods for creating ApplicationConfig instances for
common test scenarios without the verbosity of the builder pattern.
"""

from typing import Dict
from unittest.mock import Mock, patch
from pathlib import Path
from src.config.settings import ApplicationConfig


class ConfigFactory:
    """Factory for creating ApplicationConfig instances for testing.

    Provides static methods for creating ApplicationConfig instances
    for common test scenarios with sensible defaults. Includes Phase 1
    environment variable factories and Phase 2 scenario-specific methods.

    Basic Usage Examples:
        # Basic configurations
        save_config = ConfigFactory.create_save_config()
        restore_config = ConfigFactory.create_restore_config()

        # Feature-specific configurations
        pr_config = ConfigFactory.create_pr_config()
        milestone_config = ConfigFactory.create_milestone_config()

    Phase 2 Scenario-Specific Examples:
        # Dependency validation testing
        invalid_config = ConfigFactory.create_dependency_validation_config(
            feature="pull_request_comments",
            enabled=True,
            dependency_enabled=False
        )

        # Boolean parsing testing
        config = ConfigFactory.create_boolean_parsing_config(
            field="INCLUDE_MILESTONES",
            value="yes"
        )

        # Error scenario testing
        config = ConfigFactory.create_error_scenario_config(
            invalid_field="OPERATION",
            invalid_value="invalid_op"
        )

    Phase 2 Feature-Specific Examples:
        # Git repository only
        git_config = ConfigFactory.create_git_only_config()

        # Comments disabled
        no_comments_config = ConfigFactory.create_comments_disabled_config()

        # PR reviews only
        reviews_config = ConfigFactory.create_reviews_only_config()

        # Sub-issues enabled
        sub_issues_config = ConfigFactory.create_sub_issues_config()

    Environment Variable Generation:
        # Generate environment dictionaries
        env_dict = ConfigFactory.create_container_env_dict(
            DATA_PATH="/custom/path"
        )

    Mock Configuration Generation:
        # Generate mock configurations
        mock_config = ConfigFactory.create_milestone_mock_config(
            repository_owner="custom-owner"
        )
    """

    @staticmethod
    def _normalize_env_overrides(**overrides) -> Dict[str, str]:
        """Normalize override values to environment variable strings.

        Handles both old-style direct parameters (github_repo, include_pull_requests)
        and new-style environment variables (GITHUB_REPO, INCLUDE_PULL_REQUESTS).
        """
        normalized = {}

        # Mapping from old parameter names to environment variable names
        param_to_env = {
            "github_repo": "GITHUB_REPO",
            "github_token": "GITHUB_TOKEN",
            "data_path": "DATA_PATH",
            "operation": "OPERATION",
            "include_git_repo": "INCLUDE_GIT_REPO",
            "include_issues": "INCLUDE_ISSUES",
            "include_issue_comments": "INCLUDE_ISSUE_COMMENTS",
            "include_pull_requests": "INCLUDE_PULL_REQUESTS",
            "include_pull_request_comments": "INCLUDE_PULL_REQUEST_COMMENTS",
            "include_pr_reviews": "INCLUDE_PR_REVIEWS",
            "include_pr_review_comments": "INCLUDE_PR_REVIEW_COMMENTS",
            "include_sub_issues": "INCLUDE_SUB_ISSUES",
            "include_milestones": "INCLUDE_MILESTONES",
        }

        for key, value in overrides.items():
            # Convert old parameter names to environment variable names
            env_key = param_to_env.get(key, key)

            # Convert values to strings
            if isinstance(value, bool):
                normalized[env_key] = str(value).lower()
            elif isinstance(value, Path):
                normalized[env_key] = str(value)
            else:
                normalized[env_key] = str(value)

        return normalized

    @staticmethod
    def create_base_env_dict(**overrides) -> Dict[str, str]:
        """Create base environment variables dict for testing."""
        base = {
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
        normalized_overrides = ConfigFactory._normalize_env_overrides(**overrides)
        base.update(normalized_overrides)
        return base

    @staticmethod
    def create_save_env_dict(**overrides) -> Dict[str, str]:
        """Create environment variables for save operations."""
        return ConfigFactory.create_base_env_dict(OPERATION="save", **overrides)

    @staticmethod
    def create_restore_env_dict(**overrides) -> Dict[str, str]:
        """Create environment variables for restore operations."""
        return ConfigFactory.create_base_env_dict(OPERATION="restore", **overrides)

    @staticmethod
    def create_container_env_dict(**overrides) -> Dict[str, str]:
        """Create environment variables for container tests."""
        return ConfigFactory.create_base_env_dict(DATA_PATH="/data", **overrides)

    @staticmethod
    def create_validation_env_dict(
        field: str, value: str, **overrides
    ) -> Dict[str, str]:
        """Create environment variables for field validation testing."""
        env_dict = ConfigFactory.create_base_env_dict(**overrides)
        env_dict[field] = value
        return env_dict

    @staticmethod
    def create_mock_config(**overrides) -> Mock:
        """Create a mock ApplicationConfig with realistic defaults."""
        mock_config = Mock(spec=ApplicationConfig)

        # Set realistic defaults
        mock_config.operation = "save"
        mock_config.github_token = "test-token"
        mock_config.repository_owner = "test-owner"
        mock_config.repository_name = "test-repo"
        mock_config.data_path = Path("/tmp/test")
        mock_config.include_git_repo = True
        mock_config.include_issues = True
        mock_config.include_issue_comments = True
        mock_config.include_pull_requests = True
        mock_config.include_pull_request_comments = True
        mock_config.include_pr_reviews = True
        mock_config.include_pr_review_comments = True
        mock_config.include_sub_issues = True
        mock_config.include_milestones = True

        # Apply overrides
        for key, value in overrides.items():
            setattr(mock_config, key, value)

        return mock_config

    @staticmethod
    def create_milestone_mock_config(**overrides) -> Mock:
        """Create a mock config specifically for milestone testing."""
        return ConfigFactory.create_mock_config(include_milestones=True, **overrides)

    @staticmethod
    def create_pr_mock_config(**overrides) -> Mock:
        """Create a mock config for pull request testing."""
        return ConfigFactory.create_mock_config(
            include_pull_requests=True, include_pull_request_comments=True, **overrides
        )

    @staticmethod
    def create_save_config_direct(**overrides) -> ApplicationConfig:
        """Create save configuration using direct constructor.

        For testing that mocks from_environment.
        """
        defaults = {
            "operation": "save",
            "github_token": "test-token",
            "github_repo": "owner/repo",
            "data_path": "/tmp/test",
            "label_conflict_strategy": "skip",
            "include_git_repo": True,
            "include_issues": True,
            "include_issue_comments": True,
            "include_pull_requests": True,
            "include_pull_request_comments": True,
            "include_pr_reviews": True,
            "include_pr_review_comments": True,
            "include_sub_issues": True,
            "include_milestones": True,
            "git_auth_method": "token",
        }
        return ApplicationConfig(**{**defaults, **overrides})

    @staticmethod
    def create_restore_config_direct(**overrides) -> ApplicationConfig:
        """Create restore configuration using direct constructor.

        For testing that mocks from_environment.
        """
        defaults = {
            "operation": "restore",
            "github_token": "test-token",
            "github_repo": "owner/repo",
            "data_path": "/tmp/test",
            "label_conflict_strategy": "skip",
            "include_git_repo": True,
            "include_issues": True,
            "include_issue_comments": True,
            "include_pull_requests": True,
            "include_pull_request_comments": True,
            "include_pr_reviews": True,
            "include_pr_review_comments": True,
            "include_sub_issues": True,
            "include_milestones": True,
            "git_auth_method": "token",
        }
        return ApplicationConfig(**{**defaults, **overrides})

    @staticmethod
    def create_save_config(**overrides) -> ApplicationConfig:
        """Create save operation configuration."""
        env_dict = ConfigFactory.create_save_env_dict(**overrides)

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_restore_config(**overrides) -> ApplicationConfig:
        """Create restore operation configuration."""
        env_dict = ConfigFactory.create_restore_env_dict(**overrides)

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_minimal_config(**overrides) -> ApplicationConfig:
        """Create minimal features configuration for unit tests."""
        env_dict = ConfigFactory.create_base_env_dict(
            INCLUDE_GIT_REPO="false",
            INCLUDE_ISSUES="false",
            INCLUDE_ISSUE_COMMENTS="false",
            INCLUDE_PULL_REQUESTS="false",
            INCLUDE_PULL_REQUEST_COMMENTS="false",
            INCLUDE_PR_REVIEWS="false",
            INCLUDE_PR_REVIEW_COMMENTS="false",
            INCLUDE_SUB_ISSUES="false",
            INCLUDE_MILESTONES="false",
            **overrides,
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_full_config(**overrides) -> ApplicationConfig:
        """Create configuration with all features enabled."""
        env_dict = ConfigFactory.create_base_env_dict(
            INCLUDE_GIT_REPO="true",
            INCLUDE_ISSUES="true",
            INCLUDE_ISSUE_COMMENTS="true",
            INCLUDE_PULL_REQUESTS="true",
            INCLUDE_PULL_REQUEST_COMMENTS="true",
            INCLUDE_PR_REVIEWS="true",
            INCLUDE_PR_REVIEW_COMMENTS="true",
            INCLUDE_SUB_ISSUES="true",
            INCLUDE_MILESTONES="true",
            **overrides,
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_pr_config(**overrides) -> ApplicationConfig:
        """Create configuration with pull request features enabled."""
        env_dict = ConfigFactory.create_base_env_dict(
            INCLUDE_PULL_REQUESTS="true",
            INCLUDE_PULL_REQUEST_COMMENTS="true",
            INCLUDE_PR_REVIEWS="true",
            INCLUDE_PR_REVIEW_COMMENTS="true",
            **overrides,
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_issues_only_config(**overrides) -> ApplicationConfig:
        """Create configuration for issues and comments only."""
        env_dict = ConfigFactory.create_base_env_dict(
            INCLUDE_GIT_REPO="false",
            INCLUDE_PULL_REQUESTS="false",
            INCLUDE_PULL_REQUEST_COMMENTS="false",
            INCLUDE_PR_REVIEWS="false",
            INCLUDE_PR_REVIEW_COMMENTS="false",
            INCLUDE_SUB_ISSUES="false",
            INCLUDE_MILESTONES="false",
            **overrides,
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_labels_only_config(**overrides) -> ApplicationConfig:
        """Create configuration for labels only."""
        env_dict = ConfigFactory.create_base_env_dict(
            INCLUDE_GIT_REPO="false",
            INCLUDE_ISSUES="false",
            INCLUDE_ISSUE_COMMENTS="false",
            INCLUDE_PULL_REQUESTS="false",
            INCLUDE_PULL_REQUEST_COMMENTS="false",
            INCLUDE_PR_REVIEWS="false",
            INCLUDE_PR_REVIEW_COMMENTS="false",
            INCLUDE_SUB_ISSUES="false",
            INCLUDE_MILESTONES="false",
            **overrides,
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    # Phase 2: Scenario-Specific Factory Methods

    @staticmethod
    def create_dependency_validation_config(
        feature: str, enabled: bool, dependency_enabled: bool, **overrides
    ) -> ApplicationConfig:
        """Create config for testing feature dependency validation.

        Args:
            feature: Feature to test (e.g., 'pull_request_comments', 'sub_issues')
            enabled: Whether the feature should be enabled
            dependency_enabled: Whether the dependency should be enabled
        """
        feature_map = {
            "pull_request_comments": (
                "INCLUDE_PULL_REQUEST_COMMENTS",
                "INCLUDE_PULL_REQUESTS",
            ),
            "pr_review_comments": (
                "INCLUDE_PR_REVIEW_COMMENTS",
                "INCLUDE_PR_REVIEWS",
            ),
            "sub_issues": ("INCLUDE_SUB_ISSUES", "INCLUDE_ISSUES"),
        }

        if feature not in feature_map:
            raise ValueError(
                f"Unknown feature: {feature}. Available: {list(feature_map.keys())}"
            )

        feature_var, dependency_var = feature_map[feature]

        env_dict = ConfigFactory.create_base_env_dict(
            **{feature_var: str(enabled).lower()},
            **{dependency_var: str(dependency_enabled).lower()},
            **overrides,
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_boolean_parsing_config(
        field: str, value: str, **overrides
    ) -> ApplicationConfig:
        """Create config for testing boolean field parsing with various formats."""
        env_dict = ConfigFactory.create_validation_env_dict(field, value, **overrides)

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_error_scenario_config(
        invalid_field: str, invalid_value: str, **overrides
    ) -> ApplicationConfig:
        """Create config with invalid values for error testing."""
        env_dict = ConfigFactory.create_validation_env_dict(
            invalid_field, invalid_value, **overrides
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    # Phase 2: Feature-Specific Factory Methods

    @staticmethod
    def create_milestone_config(**overrides) -> ApplicationConfig:
        """Create configuration for milestone testing."""
        env_dict = ConfigFactory.create_base_env_dict(
            INCLUDE_MILESTONES="true", **overrides
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_git_only_config(**overrides) -> ApplicationConfig:
        """Create configuration for git repository testing only."""
        env_dict = ConfigFactory.create_base_env_dict(
            INCLUDE_GIT_REPO="true",
            INCLUDE_ISSUES="false",
            INCLUDE_ISSUE_COMMENTS="false",
            INCLUDE_PULL_REQUESTS="false",
            INCLUDE_PULL_REQUEST_COMMENTS="false",
            INCLUDE_PR_REVIEWS="false",
            INCLUDE_PR_REVIEW_COMMENTS="false",
            INCLUDE_SUB_ISSUES="false",
            INCLUDE_MILESTONES="false",
            **overrides,
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_comments_disabled_config(**overrides) -> ApplicationConfig:
        """Create configuration with all comment features disabled."""
        env_dict = ConfigFactory.create_base_env_dict(
            INCLUDE_ISSUE_COMMENTS="false",
            INCLUDE_PULL_REQUEST_COMMENTS="false",
            INCLUDE_PR_REVIEW_COMMENTS="false",
            **overrides,
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_reviews_only_config(**overrides) -> ApplicationConfig:
        """Create configuration for PR reviews testing only."""
        env_dict = ConfigFactory.create_base_env_dict(
            INCLUDE_GIT_REPO="false",
            INCLUDE_ISSUES="false",
            INCLUDE_ISSUE_COMMENTS="false",
            INCLUDE_PULL_REQUESTS="true",
            INCLUDE_PULL_REQUEST_COMMENTS="false",
            INCLUDE_PR_REVIEWS="true",
            INCLUDE_PR_REVIEW_COMMENTS="true",
            INCLUDE_SUB_ISSUES="false",
            INCLUDE_MILESTONES="false",
            **overrides,
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()

    @staticmethod
    def create_sub_issues_config(**overrides) -> ApplicationConfig:
        """Create configuration for sub-issues testing."""
        env_dict = ConfigFactory.create_base_env_dict(
            INCLUDE_ISSUES="true",
            INCLUDE_SUB_ISSUES="true",
            **overrides,
        )

        with patch.dict("os.environ", env_dict, clear=True):
            return ApplicationConfig.from_environment()
