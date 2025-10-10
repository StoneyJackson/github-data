from dataclasses import dataclass
import os
import logging
from typing import Union, Set
from .number_parser import NumberSpecificationParser


@dataclass
class ApplicationConfig:
    """Centralized configuration for GitHub Data operations."""

    operation: str
    github_token: str
    github_repo: str
    data_path: str
    label_conflict_strategy: str
    include_git_repo: bool
    include_issues: Union[bool, Set[int]]
    include_issue_comments: bool
    include_pull_requests: Union[bool, Set[int]]
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
                "LABEL_CONFLICT_STRATEGY", "skip"
            ),
            include_git_repo=cls._parse_enhanced_bool_env(
                "INCLUDE_GIT_REPO", default=True
            ),
            include_issues=cls._parse_number_or_bool_env(
                "INCLUDE_ISSUES", default=True
            ),
            include_issue_comments=cls._parse_enhanced_bool_env(
                "INCLUDE_ISSUE_COMMENTS", default=True
            ),
            include_pull_requests=cls._parse_number_or_bool_env(
                "INCLUDE_PULL_REQUESTS", default=True
            ),
            include_pull_request_comments=cls._parse_enhanced_bool_env(
                "INCLUDE_PULL_REQUEST_COMMENTS", default=True
            ),
            include_sub_issues=cls._parse_enhanced_bool_env(
                "INCLUDE_SUB_ISSUES", default=True
            ),
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

    @staticmethod
    def _parse_enhanced_bool_env(key: str, default: bool = False) -> bool:
        """Parse boolean environment variable with enhanced format support.

        Supported formats (case-insensitive):
        - True values: "true", "yes", "on"
        - False values: "false", "no", "off"

        Args:
            key: Environment variable name
            default: Default value if variable not set

        Returns:
            Boolean value

        Raises:
            ValueError: For unsupported boolean formats (e.g., "0", "1")
        """
        value = os.getenv(key)
        if value is None:
            return default

        # Check for legacy "0"/"1" usage and raise error with guidance
        if value in ("0", "1"):
            raise ValueError(
                f"Environment variable {key} uses legacy format '{value}'. "
                f"Please use enhanced boolean formats: "
                f"true/false, yes/no, or on/off (case-insensitive)"
            )

        try:
            return NumberSpecificationParser.parse_boolean_value(value)
        except ValueError as e:
            raise ValueError(f"Environment variable {key}: {str(e)}")

    @classmethod
    def _parse_number_or_bool_env(
        cls, key: str, default: bool = False
    ) -> Union[bool, Set[int]]:
        """Parse environment variable as number specification or boolean.

        Args:
            key: Environment variable name
            default: Default boolean value if variable not set

        Returns:
            Boolean for all/none behavior, or set of integers for selective behavior

        Raises:
            ValueError: For invalid number specifications
        """
        value = os.getenv(key)
        if value is None:
            return default

        # Check if it's a boolean value first
        if NumberSpecificationParser.is_boolean_value(value):
            return NumberSpecificationParser.parse_boolean_value(value)
        else:
            # Try to parse as number specification
            try:
                return NumberSpecificationParser.parse(value)
            except ValueError as e:
                raise ValueError(f"Environment variable {key}: {str(e)}")

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

        # Validate number specifications
        if isinstance(self.include_issues, set):
            if not self.include_issues:
                raise ValueError("INCLUDE_ISSUES number specification cannot be empty")
            if any(n <= 0 for n in self.include_issues):
                raise ValueError("INCLUDE_ISSUES numbers must be positive integers")

        if isinstance(self.include_pull_requests, set):
            if not self.include_pull_requests:
                raise ValueError(
                    "INCLUDE_PULL_REQUESTS number specification cannot be empty"
                )
            if any(n <= 0 for n in self.include_pull_requests):
                raise ValueError(
                    "INCLUDE_PULL_REQUESTS numbers must be positive integers"
                )

        # Enhanced comment dependency validation
        if self.include_issue_comments:
            if isinstance(self.include_issues, bool) and not self.include_issues:
                # Boolean false for issues
                logging.warning(
                    "Warning: INCLUDE_ISSUE_COMMENTS=true requires "
                    "INCLUDE_ISSUES=true. Ignoring issue comments."
                )
                self.include_issue_comments = False
            elif isinstance(self.include_issues, set) and not self.include_issues:
                # Empty number specification for issues
                logging.warning(
                    "Warning: INCLUDE_ISSUE_COMMENTS=true requires "
                    "INCLUDE_ISSUES to specify issues. Ignoring issue comments."
                )
                self.include_issue_comments = False

        # Enhanced PR comments dependency validation
        if self.include_pull_request_comments:
            if (
                isinstance(self.include_pull_requests, bool)
                and not self.include_pull_requests
            ):
                # Boolean false for PRs
                logging.warning(
                    "Warning: INCLUDE_PULL_REQUEST_COMMENTS=true requires "
                    "INCLUDE_PULL_REQUESTS=true. Ignoring PR comments."
                )
                self.include_pull_request_comments = False
            elif (
                isinstance(self.include_pull_requests, set)
                and not self.include_pull_requests
            ):
                # Empty number specification for PRs
                logging.warning(
                    "Warning: INCLUDE_PULL_REQUEST_COMMENTS=true requires "
                    "INCLUDE_PULL_REQUESTS to specify PRs. Ignoring PR comments."
                )
                self.include_pull_request_comments = False
