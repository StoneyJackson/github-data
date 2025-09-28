#!/usr/bin/env python3
"""
GitHub Data - Main entry point for the container.

This script handles saving and restoring GitHub repository labels, issues,
subissues, and comments based on environment variables.
"""

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.git.service import GitRepositoryServiceImpl

from src.config.settings import ApplicationConfig


def main() -> None:
    """Main entry point for the github-data container."""
    try:
        config = _setup_and_validate_configuration()
        _execute_operation(config)
        _print_completion_message(config.operation)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _setup_and_validate_configuration() -> ApplicationConfig:
    """Set up and validate configuration for the operation."""
    config = ApplicationConfig.from_environment()
    config.validate()
    _print_operation_info(config)
    return config


def _execute_operation(config: ApplicationConfig) -> None:
    """Execute the requested operation based on configuration."""
    if config.operation == "save":
        _perform_save_operation(config)
    else:
        _perform_restore_operation(config)


def _perform_save_operation(config: ApplicationConfig) -> None:
    """Perform the save operation to backup GitHub data."""
    print("Saving GitHub data...")
    from .operations.save import save_repository_data_with_strategy_pattern
    from .github import create_github_service
    from .storage import create_storage_service

    # Create services using dependency injection
    github_service = create_github_service(config.github_token)
    storage_service = create_storage_service("json")
    git_service = (
        _create_git_repository_service(config) if config.include_git_repo else None
    )

    save_repository_data_with_strategy_pattern(
        github_service,
        storage_service,
        config.github_repo,
        config.data_path,
        include_git_repo=config.include_git_repo,
        git_service=git_service,
    )


def _perform_restore_operation(config: ApplicationConfig) -> None:
    """Perform the restore operation to restore GitHub data."""
    print("Restoring GitHub data...")
    from .operations.restore.restore import (
        restore_repository_data_with_strategy_pattern,
    )
    from .github import create_github_service
    from .storage import create_storage_service

    # Create services using dependency injection
    github_service = create_github_service(config.github_token)
    storage_service = create_storage_service("json")
    git_service = (
        _create_git_repository_service(config) if config.include_git_repo else None
    )

    restore_repository_data_with_strategy_pattern(
        github_service,
        storage_service,
        config.github_repo,
        config.data_path,
        config.label_conflict_strategy,
        include_original_metadata=True,
        include_prs=False,
        include_sub_issues=False,
        include_git_repo=config.include_git_repo,
        git_service=git_service,
    )


def _create_git_repository_service(
    config: ApplicationConfig,
) -> "GitRepositoryServiceImpl":
    """Create Git repository service with configuration."""
    from src.git.service import GitRepositoryServiceImpl

    return GitRepositoryServiceImpl(auth_token=config.github_token)


def _print_operation_info(config: ApplicationConfig) -> None:
    """Print information about the operation being performed."""
    print(f"GitHub Data - {config.operation.capitalize()} operation")
    print(f"Repository: {config.github_repo}")
    print(f"Data path: {config.data_path}")
    if config.include_git_repo:
        print("Git repository backup: enabled (mirror format)")


def _print_completion_message(operation: str) -> None:
    """Print completion message for the operation."""
    print(f"{operation.capitalize()} operation completed successfully")


if __name__ == "__main__":
    main()
