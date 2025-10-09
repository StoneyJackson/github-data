from dataclasses import dataclass
import os
import logging


@dataclass
class ApplicationConfig:
    """Centralized configuration for GitHub Data operations."""

    operation: str
    github_token: str
    github_repo: str
    data_path: str
    label_conflict_strategy: str
    include_git_repo: bool
    include_issues: bool
    include_issue_comments: bool
    include_pull_requests: bool
    include_pull_request_comments: bool
    include_sub_issues: bool
    git_auth_method: str

    @classmethod
    def from_environment(cls) -> "ApplicationConfig":
        """Create configuration from environment variables."""
        return cls(
            operation=cls._get_required_env("OPERATION"),
            github_token=cls._get_required_env("GITHUB_TOKEN"),
            github_repo=cls._get_required_env("GITHUB_REPO"),
            data_path=cls._get_env_with_default("DATA_PATH", "/data"),
            label_conflict_strategy=cls._get_env_with_default(
                "LABEL_CONFLICT_STRATEGY", "fail-if-existing"
            ),
            include_git_repo=cls._parse_bool_env("INCLUDE_GIT_REPO", default=True),
            include_issues=cls._parse_bool_env("INCLUDE_ISSUES", default=True),
            include_issue_comments=cls._parse_bool_env(
                "INCLUDE_ISSUE_COMMENTS", default=True
            ),
            include_pull_requests=cls._parse_bool_env(
                "INCLUDE_PULL_REQUESTS", default=False
            ),
            include_pull_request_comments=cls._parse_bool_env(
                "INCLUDE_PULL_REQUEST_COMMENTS", default=True
            ),
            include_sub_issues=cls._parse_bool_env("INCLUDE_SUB_ISSUES", default=False),
            git_auth_method=cls._get_env_with_default("GIT_AUTH_METHOD", "token"),
        )

    @staticmethod
    def _get_required_env(key: str) -> str:
        """Get required environment variable."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

    @staticmethod
    def _get_env_with_default(key: str, default: str) -> str:
        """Get environment variable with default value."""
        return os.getenv(key, default)

    @staticmethod
    def _parse_bool_env(key: str, default: bool = False) -> bool:
        """Parse boolean environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def validate(self) -> None:
        """Validate configuration values."""
        valid_operations = ["save", "restore"]
        if self.operation not in valid_operations:
            raise ValueError(
                f"Operation must be one of {valid_operations}, got: {self.operation}"
            )

        # Use the conflict strategies from the enum
        valid_strategies = [
            "fail-if-existing",
            "fail-if-conflict",
            "overwrite",
            "skip",
            "delete-all",
        ]
        if self.label_conflict_strategy not in valid_strategies:
            raise ValueError(
                f"Label conflict strategy must be one of {valid_strategies}, "
                f"got: {self.label_conflict_strategy}"
            )

        # Use the auth methods from the enum
        valid_auth_methods = ["token", "ssh"]
        if self.git_auth_method not in valid_auth_methods:
            raise ValueError(
                f"Git auth method must be one of {valid_auth_methods}, "
                f"got: {self.git_auth_method}"
            )

        # Validate issue comments dependency
        if self.include_issue_comments and not self.include_issues:
            logging.warning(
                "Warning: INCLUDE_ISSUE_COMMENTS=true requires "
                "INCLUDE_ISSUES=true. Ignoring issue comments."
            )
            # Disable issue comments when dependency is not met
            self.include_issue_comments = False

        # Validate PR comments dependency
        if self.include_pull_request_comments and not self.include_pull_requests:
            logging.warning(
                "Warning: INCLUDE_PULL_REQUEST_COMMENTS=true requires "
                "INCLUDE_PULL_REQUESTS=true. Ignoring PR comments."
            )
            # Disable PR comments when dependency is not met
            self.include_pull_request_comments = False
