"""Configuration factory for common test scenarios.

Provides static methods for creating ApplicationConfig instances for
common test scenarios without the verbosity of the builder pattern.
"""

from typing import Dict
from src.config.settings import ApplicationConfig


class ConfigFactory:
    """Factory for creating common ApplicationConfig test instances.

    Provides static methods for creating ApplicationConfig instances
    for common test scenarios with sensible defaults.

    Example usage:
        # Basic save configuration
        config = ConfigFactory.create_save_config()

        # Restore with custom repo
        config = ConfigFactory.create_restore_config(github_repo="owner/repo")

        # Minimal configuration for unit tests
        config = ConfigFactory.create_minimal_config()

        # Full feature configuration
        config = ConfigFactory.create_full_config()
    """

    @staticmethod
    def _get_base_defaults() -> Dict[str, any]:
        """Get base default configuration values."""
        return {
            "github_token": "test-token",
            "github_repo": "test-owner/test-repo",
            "data_path": "/tmp/test-data",
            "label_conflict_strategy": "skip",
            "include_git_repo": True,
            "include_issues": True,
            "include_issue_comments": True,
            "include_pull_requests": True,
            "include_pull_request_comments": True,
            "include_sub_issues": True,
            "git_auth_method": "token",
        }

    @staticmethod
    def create_save_config(**overrides) -> ApplicationConfig:
        """Create a save operation configuration.

        Args:
            **overrides: Any configuration values to override

        Returns:
            ApplicationConfig configured for save operation
        """
        defaults = {"operation": "save", **ConfigFactory._get_base_defaults()}
        return ApplicationConfig(**{**defaults, **overrides})

    @staticmethod
    def create_restore_config(**overrides) -> ApplicationConfig:
        """Create a restore operation configuration.

        Args:
            **overrides: Any configuration values to override

        Returns:
            ApplicationConfig configured for restore operation
        """
        defaults = {"operation": "restore", **ConfigFactory._get_base_defaults()}
        return ApplicationConfig(**{**defaults, **overrides})

    @staticmethod
    def create_minimal_config(**overrides) -> ApplicationConfig:
        """Create a minimal configuration for unit tests.

        Disables most features to focus on core functionality.

        Args:
            **overrides: Any configuration values to override

        Returns:
            ApplicationConfig with minimal features enabled
        """
        defaults = {
            "operation": "save",
            **ConfigFactory._get_base_defaults(),
            "include_git_repo": False,
            "include_issues": False,
            "include_issue_comments": False,
            "include_pull_requests": False,
            "include_pull_request_comments": False,
            "include_sub_issues": False,
        }
        return ApplicationConfig(**{**defaults, **overrides})

    @staticmethod
    def create_full_config(**overrides) -> ApplicationConfig:
        """Create a configuration with all features enabled.

        Args:
            **overrides: Any configuration values to override

        Returns:
            ApplicationConfig with all features enabled
        """
        defaults = {
            "operation": "save",
            **ConfigFactory._get_base_defaults(),
            "include_git_repo": True,
            "include_issues": True,
            "include_issue_comments": True,
            "include_pull_requests": True,
            "include_pull_request_comments": True,
            "include_sub_issues": True,
        }
        return ApplicationConfig(**{**defaults, **overrides})

    @staticmethod
    def create_pr_config(**overrides) -> ApplicationConfig:
        """Create a configuration with pull request features enabled.

        Args:
            **overrides: Any configuration values to override

        Returns:
            ApplicationConfig with PR features enabled
        """
        defaults = {
            "operation": "save",
            **ConfigFactory._get_base_defaults(),
            "include_pull_requests": True,
            "include_pull_request_comments": True,
        }
        return ApplicationConfig(**{**defaults, **overrides})

    @staticmethod
    def create_issues_only_config(**overrides) -> ApplicationConfig:
        """Create a configuration for issues and comments only.

        Args:
            **overrides: Any configuration values to override

        Returns:
            ApplicationConfig for issues and comments only
        """
        defaults = {
            "operation": "save",
            **ConfigFactory._get_base_defaults(),
            "include_git_repo": False,
            "include_issues": True,
            "include_issue_comments": True,
            "include_pull_requests": False,
            "include_pull_request_comments": False,
            "include_sub_issues": False,
        }
        return ApplicationConfig(**{**defaults, **overrides})

    @staticmethod
    def create_labels_only_config(**overrides) -> ApplicationConfig:
        """Create a configuration for labels only.

        Args:
            **overrides: Any configuration values to override

        Returns:
            ApplicationConfig for labels only
        """
        defaults = {
            "operation": "save",
            **ConfigFactory._get_base_defaults(),
            "include_git_repo": False,
            "include_issues": False,
            "include_issue_comments": False,
            "include_pull_requests": False,
            "include_pull_request_comments": False,
            "include_sub_issues": False,
        }
        return ApplicationConfig(**{**defaults, **overrides})
