"""
Restore actions for GitHub repository data.

Implements the restore functionality that reads JSON files and
recreates labels, issues, and comments in GitHub repositories.
"""

from typing import Optional
from src.github.protocols import RepositoryService
from src.storage.protocols import StorageService
from src.git.protocols import GitRepositoryService
from src.config.settings import ApplicationConfig
from src.operations.strategy_factory import StrategyFactory


def restore_repository_data_with_strategy_pattern(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    data_path: str,
    label_conflict_strategy: str = "fail-if-existing",
    include_original_metadata: bool = True,
    include_pull_requests: bool = False,
    include_sub_issues: bool = False,
    include_git_repo: bool = False,
    include_pull_request_comments: Optional[bool] = None,
    git_service: Optional[GitRepositoryService] = None,
) -> None:
    """Restore using strategy pattern approach (legacy interface)."""
    # For backward compatibility, create a temporary config from parameters
    # This will be removed in Phase 2 when we fully transition to config-driven approach
    # Handle PR comments - if not specified, default to same as PRs for
    # backward compatibility
    pr_comments_enabled = (
        include_pull_request_comments
        if include_pull_request_comments is not None
        else include_pull_requests
    )

    temp_config = ApplicationConfig(
        operation="restore",
        github_token="",  # Not used in restore operation
        github_repo=repo_name,
        data_path=data_path,
        label_conflict_strategy=label_conflict_strategy,
        include_git_repo=include_git_repo,
        include_issues=True,  # Default to include issues
        include_issue_comments=True,  # Default to include comments
        include_pull_requests=include_pull_requests,
        include_pull_request_comments=pr_comments_enabled,
        include_pr_reviews=include_pull_requests,  # Enable only if PRs
        include_pr_review_comments=include_pull_requests,  # Enable only if PRs
        include_sub_issues=include_sub_issues,
        include_milestones=True,  # Default to include milestones
        git_auth_method="token",
    )

    restore_repository_data_with_config(
        temp_config,
        github_service,
        storage_service,
        repo_name,
        data_path,
        include_original_metadata=include_original_metadata,
        include_pull_requests=include_pull_requests,
        include_sub_issues=include_sub_issues,
        git_service=git_service,
    )


def restore_repository_data_with_config(
    config: ApplicationConfig,
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    data_path: str,
    include_original_metadata: bool = True,
    include_pull_requests: bool = False,
    include_sub_issues: bool = False,
    git_service: Optional[GitRepositoryService] = None,
) -> None:
    """Restore using strategy pattern approach with configuration."""

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
        include_pr_reviews=config.include_pr_reviews,
        include_pr_review_comments=config.include_pr_review_comments,
        include_sub_issues=updated_include_sub_issues,
        include_milestones=config.include_milestones,
        git_auth_method=config.git_auth_method,
    )

    # Create orchestrator with updated configuration
    from .orchestrator import StrategyBasedRestoreOrchestrator

    orchestrator = StrategyBasedRestoreOrchestrator(
        updated_config,
        github_service,
        storage_service,
        include_original_metadata,
        git_service,
    )

    # Determine entities to restore based on updated configuration
    requested_entities = StrategyFactory.get_enabled_entities(updated_config)

    # Execute restoration
    results = orchestrator.execute_restore(repo_name, data_path, requested_entities)

    # Handle errors (maintain backward compatibility)
    failed_operations = [r for r in results if not r["success"]]
    if failed_operations:
        error_messages = [r["error"] for r in failed_operations if r.get("error")]
        raise Exception(f"Restore operation failed: {'; '.join(error_messages)}")
