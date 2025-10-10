#!/usr/bin/env python3
"""
GitHub Data - Main entry point for the container.

This script handles saving and restoring GitHub repository labels, issues,
subissues, and comments based on environment variables.
"""

import sys
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from src.git.service import GitRepositoryServiceImpl

from src.config.settings import ApplicationConfig
from src.operations.strategy_factory import StrategyFactory


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
    """Execute save operation to backup GitHub repository data."""
    _print_save_operation_start()

    github_service = _create_github_service(config)
    storage_service = _create_storage_service()
    git_service = _create_git_service_if_needed(config)

    _execute_save_with_config(config, github_service, storage_service, git_service)


def _print_save_operation_start() -> None:
    """Print start message for save operation."""
    print("Saving GitHub data...")


def _create_github_service(config: ApplicationConfig) -> Any:
    """Create GitHub service with token from configuration."""
    from .github import create_github_service

    return create_github_service(config.github_token)


def _create_storage_service() -> Any:
    """Create JSON storage service."""
    from .storage import create_storage_service

    return create_storage_service("json")


def _create_git_service_if_needed(config: ApplicationConfig) -> Optional[Any]:
    """Create git service if git repository backup is enabled."""
    return _create_git_repository_service(config) if config.include_git_repo else None


def _execute_save_with_config(
    config: ApplicationConfig,
    github_service: Any,
    storage_service: Any,
    git_service: Optional[Any],
) -> None:
    """Execute save operation using configuration-based approach."""
    from .operations.save import save_repository_data_with_config

    save_repository_data_with_config(
        config,
        github_service,
        storage_service,
        config.github_repo,
        config.data_path,
        include_pull_requests=StrategyFactory._is_enabled(config.include_pull_requests),
        include_sub_issues=config.include_sub_issues,
        git_service=git_service,
    )


def _perform_restore_operation(config: ApplicationConfig) -> None:
    """Execute restore operation to restore GitHub repository data."""
    _print_restore_operation_start()

    github_service = _create_github_service(config)
    storage_service = _create_storage_service()
    git_service = _create_git_service_if_needed(config)

    _execute_restore_with_config(config, github_service, storage_service, git_service)


def _print_restore_operation_start() -> None:
    """Print start message for restore operation."""
    print("Restoring GitHub data...")


def _execute_restore_with_config(
    config: ApplicationConfig,
    github_service: Any,
    storage_service: Any,
    git_service: Optional[Any],
) -> None:
    """Execute restore operation using configuration-based approach."""
    from .operations.restore.restore import restore_repository_data_with_config

    restore_repository_data_with_config(
        config,
        github_service,
        storage_service,
        config.github_repo,
        config.data_path,
        include_original_metadata=True,
        include_pull_requests=StrategyFactory._is_enabled(config.include_pull_requests),
        include_sub_issues=config.include_sub_issues,
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

    # Feature status information
    features = []
    if config.include_git_repo:
        features.append("Git repository backup")
    if config.include_issue_comments:
        features.append("Issue comments")
    else:
        print("Issue comments: excluded")

    if features:
        print(f"Enabled features: {', '.join(features)}")


def _print_completion_message(operation: str) -> None:
    """Print completion message for the operation."""
    print(f"{operation.capitalize()} operation completed successfully")


if __name__ == "__main__":
    main()
