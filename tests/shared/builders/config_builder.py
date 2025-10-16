"""Configuration builder for test scenarios.

Provides a fluent API for creating ApplicationConfig instances with sensible defaults
and easy customization for specific test scenarios.
"""

from typing import Dict, Union, Set
from src.config.settings import ApplicationConfig


class ConfigBuilder:
    """Fluent builder for ApplicationConfig instances in tests.

    Provides sensible defaults for all configuration fields and allows
    overriding only the fields relevant to specific test scenarios.

    Example usage:
        # Basic configuration
        config = ConfigBuilder().build()

        # Save operation with PR features
        config = ConfigBuilder().with_operation("save").with_pr_features().build()

        # Restore operation with minimal features
        config = (
            ConfigBuilder()
            .with_operation("restore")
            .with_minimal_features()
            .build()
        )

        # Environment variables for container tests
        env_vars = ConfigBuilder().with_pr_features().as_env_dict()
    """

    def __init__(self):
        """Initialize with sensible test defaults."""
        self._config = {
            "operation": "save",
            "github_token": "test-token",
            "github_repo": "test-owner/test-repo",
            "data_path": "/tmp/test-data",
            "label_conflict_strategy": "skip",
            "include_git_repo": True,
            "include_issues": True,
            "include_issue_comments": True,
            "include_pull_requests": True,
            "include_pull_request_comments": True,
            "include_pr_reviews": True,
            "include_pr_review_comments": True,
            "include_sub_issues": True,
            "git_auth_method": "token",
        }

    def with_operation(self, operation: str) -> "ConfigBuilder":
        """Set the operation (save/restore)."""
        self._config["operation"] = operation
        return self

    def with_repo(self, repo: str) -> "ConfigBuilder":
        """Set the GitHub repository."""
        self._config["github_repo"] = repo
        return self

    def with_token(self, token: str) -> "ConfigBuilder":
        """Set the GitHub token."""
        self._config["github_token"] = token
        return self

    def with_data_path(self, path: str) -> "ConfigBuilder":
        """Set the data path."""
        self._config["data_path"] = path
        return self

    def with_label_strategy(self, strategy: str) -> "ConfigBuilder":
        """Set the label conflict strategy."""
        self._config["label_conflict_strategy"] = strategy
        return self

    def with_git_auth_method(self, method: str) -> "ConfigBuilder":
        """Set the git authentication method."""
        self._config["git_auth_method"] = method
        return self

    def with_git_repo(self, enabled: bool = True) -> "ConfigBuilder":
        """Enable/disable git repository inclusion."""
        self._config["include_git_repo"] = enabled
        return self

    def with_issues(self, enabled: Union[bool, Set[int]] = True) -> "ConfigBuilder":
        """Enable/disable issues inclusion or specify issue numbers."""
        self._config["include_issues"] = enabled
        return self

    def with_issue_comments(self, enabled: bool = True) -> "ConfigBuilder":
        """Enable/disable issue comments inclusion."""
        self._config["include_issue_comments"] = enabled
        return self

    def with_pull_requests(
        self, enabled: Union[bool, Set[int]] = True
    ) -> "ConfigBuilder":
        """Enable/disable pull requests inclusion or specify PR numbers."""
        self._config["include_pull_requests"] = enabled
        return self

    def with_pull_request_comments(self, enabled: bool = True) -> "ConfigBuilder":
        """Enable/disable pull request comments inclusion."""
        self._config["include_pull_request_comments"] = enabled
        return self

    def with_pr_reviews(self, enabled: bool = True) -> "ConfigBuilder":
        """Enable/disable pull request reviews inclusion."""
        self._config["include_pr_reviews"] = enabled
        return self

    def with_pr_review_comments(self, enabled: bool = True) -> "ConfigBuilder":
        """Enable/disable pull request review comments inclusion."""
        self._config["include_pr_review_comments"] = enabled
        return self

    def with_sub_issues(self, enabled: bool = True) -> "ConfigBuilder":
        """Enable/disable sub-issues inclusion."""
        self._config["include_sub_issues"] = enabled
        return self

    def with_pr_features(
        self,
        prs: bool = True,
        pr_comments: bool = True,
        pr_reviews: bool = True,
        pr_review_comments: bool = True,
    ) -> "ConfigBuilder":
        """Enable pull request features (PRs, comments, reviews, review comments)."""
        self._config["include_pull_requests"] = prs
        self._config["include_pull_request_comments"] = pr_comments
        self._config["include_pr_reviews"] = pr_reviews
        self._config["include_pr_review_comments"] = pr_review_comments
        return self

    def with_minimal_features(self) -> "ConfigBuilder":
        """Configure with minimal features enabled."""
        self._config.update(
            {
                "include_git_repo": False,
                "include_issues": False,
                "include_issue_comments": False,
                "include_pull_requests": False,
                "include_pull_request_comments": False,
                "include_pr_reviews": False,
                "include_pr_review_comments": False,
                "include_sub_issues": False,
            }
        )
        return self

    def with_all_features(self) -> "ConfigBuilder":
        """Configure with all features enabled."""
        self._config.update(
            {
                "include_git_repo": True,
                "include_issues": True,
                "include_issue_comments": True,
                "include_pull_requests": True,
                "include_pull_request_comments": True,
                "include_pr_reviews": True,
                "include_pr_review_comments": True,
                "include_sub_issues": True,
            }
        )
        return self

    def with_custom(self, **kwargs) -> "ConfigBuilder":
        """Set arbitrary configuration values."""
        self._config.update(kwargs)
        return self

    def build(self) -> ApplicationConfig:
        """Build the ApplicationConfig instance."""
        return ApplicationConfig(**self._config)

    def as_env_dict(self) -> Dict[str, str]:
        """Build as environment variable dictionary for container tests."""
        env_mapping = {
            "operation": "OPERATION",
            "github_token": "GITHUB_TOKEN",
            "github_repo": "GITHUB_REPO",
            "data_path": "DATA_PATH",
            "label_conflict_strategy": "LABEL_CONFLICT_STRATEGY",
            "include_git_repo": "INCLUDE_GIT_REPO",
            "include_issues": "INCLUDE_ISSUES",
            "include_issue_comments": "INCLUDE_ISSUE_COMMENTS",
            "include_pull_requests": "INCLUDE_PULL_REQUESTS",
            "include_pull_request_comments": "INCLUDE_PULL_REQUEST_COMMENTS",
            "include_pr_reviews": "INCLUDE_PR_REVIEWS",
            "include_pr_review_comments": "INCLUDE_PR_REVIEW_COMMENTS",
            "include_sub_issues": "INCLUDE_SUB_ISSUES",
            "git_auth_method": "GIT_AUTH_METHOD",
        }

        env_vars = {}
        for config_key, env_key in env_mapping.items():
            value = self._config[config_key]
            if isinstance(value, bool):
                env_vars[env_key] = "true" if value else "false"
            else:
                env_vars[env_key] = str(value)

        return env_vars
