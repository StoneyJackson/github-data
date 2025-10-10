"""
Save actions for GitHub repository data.

Implements the save functionality that collects GitHub data and
saves it to JSON files for backup purposes.
"""

from typing import List, Optional
from src.github.protocols import RepositoryService
from src.storage.protocols import StorageService
from src.git.protocols import GitRepositoryService
from src.config.settings import ApplicationConfig
from src.operations.strategy_factory import StrategyFactory


def save_repository_data_with_strategy_pattern(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    output_path: str,
    include_pull_requests: bool = True,
    include_sub_issues: bool = True,
    include_git_repo: bool = False,
    git_service: Optional[GitRepositoryService] = None,
    data_types: Optional[List[str]] = None,
) -> None:
    """Save using strategy pattern approach (legacy interface)."""
    # For backward compatibility, create a temporary config from parameters
    # This will be removed in Phase 2 when we fully transition to config-driven approach
    temp_config = ApplicationConfig(
        operation="save",
        github_token="",  # Not used in save operation
        github_repo=repo_name,
        data_path=output_path,
        label_conflict_strategy="fail-if-existing",
        include_git_repo=include_git_repo,
        include_issues=True,  # Default to include issues
        include_issue_comments=True,  # Default to include comments
        include_pull_requests=include_pull_requests,
        include_pull_request_comments=include_pull_requests,  # Enable only if PRs
        include_sub_issues=include_sub_issues,
        git_auth_method="token",
    )

    save_repository_data_with_config(
        temp_config,
        github_service,
        storage_service,
        repo_name,
        output_path,
        include_pull_requests=include_pull_requests,
        include_sub_issues=include_sub_issues,
        git_service=git_service,
        data_types=data_types,
    )


def save_repository_data_with_config(
    config: ApplicationConfig,
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    output_path: str,
    include_pull_requests: bool = False,
    include_sub_issues: bool = False,
    git_service: Optional[GitRepositoryService] = None,
    data_types: Optional[List[str]] = None,
) -> None:
    """Save using strategy pattern approach with configuration."""

    # Create updated configuration that considers legacy parameters
    # For boolean fields, use OR logic; for Union types, prioritize config over legacy
    updated_include_pull_requests = config.include_pull_requests
    if (
        isinstance(config.include_pull_requests, bool)
        and not config.include_pull_requests
        and include_pull_requests
    ):
        updated_include_pull_requests = include_pull_requests

    updated_include_sub_issues = config.include_sub_issues
    if not config.include_sub_issues and include_sub_issues:
        updated_include_sub_issues = include_sub_issues

    updated_config = ApplicationConfig(
        operation=config.operation,
        github_token=config.github_token,
        github_repo=config.github_repo,
        data_path=config.data_path,
        label_conflict_strategy=config.label_conflict_strategy,
        include_git_repo=config.include_git_repo,
        include_issues=config.include_issues,
        include_issue_comments=config.include_issue_comments,
        include_pull_requests=updated_include_pull_requests,
        include_pull_request_comments=config.include_pull_request_comments,
        include_sub_issues=updated_include_sub_issues,
        git_auth_method=config.git_auth_method,
    )

    # Create orchestrator with updated configuration
    from .orchestrator import StrategyBasedSaveOrchestrator

    orchestrator = StrategyBasedSaveOrchestrator(
        updated_config, github_service, storage_service, git_service
    )

    # Determine entities to save
    if data_types is None:
        requested_entities = StrategyFactory.get_enabled_entities(updated_config)
    else:
        requested_entities = data_types

    # Execute save operation
    results = orchestrator.execute_save(repo_name, output_path, requested_entities)

    # Handle errors
    failed_operations = [r for r in results if not r["success"]]
    if failed_operations:
        error_messages = []
        for r in failed_operations:
            entity_name = r.get("entity_name", "unknown entity")
            if r.get("error"):
                error_messages.append(f"{entity_name}: {r['error']}")
            else:
                error_messages.append(f"Unknown error in {entity_name}")
        raise Exception(f"Save operation failed: {'; '.join(error_messages)}")
