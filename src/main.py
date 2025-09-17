#!/usr/bin/env python3
"""
GitHub Data - Main entry point for the container.

This script handles saving and restoring GitHub repository labels, issues,
subissues, and comments based on environment variables.
"""

import os
import sys
from typing import Optional


def main() -> None:
    """Main entry point for the github-data container."""
    try:
        config = _setup_and_validate_configuration()
        _execute_operation(config)
        _print_completion_message(config.operation)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _setup_and_validate_configuration() -> "Configuration":
    """Set up and validate configuration for the operation."""
    config = _load_configuration()
    _validate_operation(config.operation)
    _print_operation_info(config)
    return config


def _execute_operation(config: "Configuration") -> None:
    """Execute the requested operation based on configuration."""
    if config.operation == "save":
        _perform_save_operation(config)
    else:
        _perform_restore_operation(config)


def _perform_save_operation(config: "Configuration") -> None:
    """Perform the save operation to backup GitHub data."""
    print("Saving GitHub data...")
    from .operations.save import save_repository_data_with_services
    from .github import create_github_service
    from .storage import create_storage_service

    # Create services using dependency injection
    github_service = create_github_service(config.github_token)
    storage_service = create_storage_service("json")

    save_repository_data_with_services(
        github_service, storage_service, config.github_repo, config.data_path
    )


def _perform_restore_operation(config: "Configuration") -> None:
    """Perform the restore operation to restore GitHub data."""
    print("Restoring GitHub data...")
    from .operations.restore import restore_repository_data_with_services
    from .github import create_github_service
    from .storage import create_storage_service

    # Create services using dependency injection
    github_service = create_github_service(config.github_token)
    storage_service = create_storage_service("json")

    restore_repository_data_with_services(
        github_service,
        storage_service,
        config.github_repo,
        config.data_path,
        config.label_conflict_strategy,
    )


def _print_operation_info(config: "Configuration") -> None:
    """Print information about the operation being performed."""
    print(f"GitHub Data - {config.operation.capitalize()} operation")
    print(f"Repository: {config.github_repo}")
    print(f"Data path: {config.data_path}")


def _print_completion_message(operation: str) -> None:
    """Print completion message for the operation."""
    print(f"{operation.capitalize()} operation completed successfully")


def _load_configuration() -> "Configuration":
    """Load configuration from environment variables."""
    operation = _get_required_env_var("OPERATION")
    github_token = _get_required_env_var("GITHUB_TOKEN")
    github_repo = _get_required_env_var("GITHUB_REPO")
    data_path = _get_env_var("DATA_PATH", required=False) or "/data"
    label_conflict_strategy = (
        _get_env_var("LABEL_CONFLICT_STRATEGY", required=False) or "fail-if-existing"
    )

    return Configuration(
        operation=operation,
        github_token=github_token,
        github_repo=github_repo,
        data_path=data_path,
        label_conflict_strategy=label_conflict_strategy,
    )


def _validate_operation(operation: str) -> None:
    """Validate that the operation is supported."""
    if operation not in ["save", "restore"]:
        print(
            f"Error: OPERATION must be 'save' or 'restore', got '{operation}'",
            file=sys.stderr,
        )
        sys.exit(1)


def _get_env_var(name: str, required: bool = True) -> Optional[str]:
    """Get environment variable with optional requirement check."""
    value = os.getenv(name)
    if required and not value:
        print(f"Error: Required environment variable {name} not set", file=sys.stderr)
        sys.exit(1)
    return value


def _get_required_env_var(name: str) -> str:
    """Get required environment variable, guaranteed to return non-None value."""
    value = os.getenv(name)
    if not value:
        print(f"Error: Required environment variable {name} not set", file=sys.stderr)
        sys.exit(1)
    return value


class Configuration:
    """Configuration data class for application settings."""

    def __init__(
        self,
        operation: str,
        github_token: str,
        github_repo: str,
        data_path: str,
        label_conflict_strategy: str,
    ):
        self.operation = operation
        self.github_token = github_token
        self.github_repo = github_repo
        self.data_path = data_path
        self.label_conflict_strategy = label_conflict_strategy


if __name__ == "__main__":
    main()
