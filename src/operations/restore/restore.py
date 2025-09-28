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
    include_prs: bool = False,
    include_sub_issues: bool = False,
    include_git_repo: bool = False,
    git_service: Optional[GitRepositoryService] = None,
) -> None:
    """Restore using strategy pattern approach (legacy interface)."""
    # For backward compatibility, create a temporary config from parameters
    # This will be removed in Phase 2 when we fully transition to config-driven approach
    temp_config = ApplicationConfig(
        operation="restore",
        github_token="",  # Not used in restore operation
        github_repo=repo_name,
        data_path=data_path,
        label_conflict_strategy=label_conflict_strategy,
        include_git_repo=include_git_repo,
        include_issue_comments=True,  # Default to include comments
        git_auth_method="token",
    )

    restore_repository_data_with_config(
        temp_config,
        github_service,
        storage_service,
        repo_name,
        data_path,
        include_original_metadata=include_original_metadata,
        include_prs=include_prs,
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
    include_prs: bool = False,
    include_sub_issues: bool = False,
    git_service: Optional[GitRepositoryService] = None,
) -> None:
    """Restore using strategy pattern approach with configuration."""

    # Create orchestrator with configuration
    from .orchestrator import StrategyBasedRestoreOrchestrator

    orchestrator = StrategyBasedRestoreOrchestrator(
        config, github_service, storage_service, include_original_metadata
    )

    # The orchestrator now auto-registers strategies based on config
    # Additional strategies for features not yet fully integrated:

    # Add PR and PR comment strategies if requested
    if include_prs:
        from src.operations.restore.strategies.pull_requests_strategy import (
            PullRequestsRestoreStrategy,
            create_conflict_strategy as create_pr_conflict_strategy,
        )
        from src.operations.restore.strategies.pr_comments_strategy import (
            PullRequestCommentsRestoreStrategy,
            create_conflict_strategy as create_pr_comment_conflict_strategy,
        )

        pr_conflict_strategy = create_pr_conflict_strategy()
        pr_comment_conflict_strategy = create_pr_comment_conflict_strategy()

        orchestrator.register_strategy(
            PullRequestsRestoreStrategy(pr_conflict_strategy, include_original_metadata)
        )
        orchestrator.register_strategy(
            PullRequestCommentsRestoreStrategy(
                pr_comment_conflict_strategy, include_original_metadata
            )
        )

    # Add sub-issues strategy if requested
    if include_sub_issues:
        from src.operations.restore.strategies.sub_issues_strategy import (
            SubIssuesRestoreStrategy,
        )

        orchestrator.register_strategy(SubIssuesRestoreStrategy())

    # Add Git repository strategy if requested
    if config.include_git_repo and git_service:
        from src.operations.restore.strategies.git_repository_strategy import (
            GitRepositoryRestoreStrategy,
        )

        orchestrator.register_strategy(GitRepositoryRestoreStrategy(git_service))

    # Determine entities to restore
    requested_entities = StrategyFactory.get_enabled_entities(config)
    if include_prs:
        requested_entities.extend(["pull_requests", "pr_comments"])
    if include_sub_issues:
        requested_entities.append("sub_issues")
    if config.include_git_repo and git_service:
        requested_entities.append("git_repository")

    # Execute restoration
    results = orchestrator.execute_restore(repo_name, data_path, requested_entities)

    # Handle errors (maintain backward compatibility)
    failed_operations = [r for r in results if not r["success"]]
    if failed_operations:
        error_messages = [r["error"] for r in failed_operations if r.get("error")]
        raise Exception(f"Restore operation failed: {'; '.join(error_messages)}")
