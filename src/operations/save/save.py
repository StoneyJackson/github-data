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
    include_prs: bool = True,
    include_sub_issues: bool = True,
    include_git_repo: bool = True,
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
        include_issue_comments=True,  # Default to include comments
        git_auth_method="token",
    )

    save_repository_data_with_config(
        temp_config,
        github_service,
        storage_service,
        repo_name,
        output_path,
        include_prs=include_prs,
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
    include_prs: bool = True,
    include_sub_issues: bool = True,
    git_service: Optional[GitRepositoryService] = None,
    data_types: Optional[List[str]] = None,
) -> None:
    """Save using strategy pattern approach with configuration."""

    # Create orchestrator with configuration
    from .orchestrator import StrategyBasedSaveOrchestrator

    orchestrator = StrategyBasedSaveOrchestrator(
        config, github_service, storage_service
    )

    # Add additional strategies not yet in the factory
    if include_prs:
        from .strategies.pull_requests_strategy import PullRequestsSaveStrategy
        from .strategies.pr_comments_strategy import PullRequestCommentsSaveStrategy

        orchestrator.register_strategy(PullRequestsSaveStrategy())
        orchestrator.register_strategy(PullRequestCommentsSaveStrategy())

    # Add sub-issues strategy if requested
    if include_sub_issues:
        from .strategies.sub_issues_strategy import SubIssuesSaveStrategy

        orchestrator.register_strategy(SubIssuesSaveStrategy())

    # Add Git repository strategy if requested
    if config.include_git_repo and git_service:
        from .strategies.git_repository_strategy import GitRepositoryStrategy

        orchestrator.register_strategy(GitRepositoryStrategy(git_service))

    # Determine entities to save
    if data_types is None:
        # Start with config-based entities
        requested_entities = StrategyFactory.get_enabled_entities(config)

        # Add additional entities based on parameters
        if include_prs:
            requested_entities.extend(["pull_requests", "pr_comments"])
        if include_sub_issues:
            requested_entities.append("sub_issues")
        if config.include_git_repo and git_service:
            requested_entities.append("git_repository")
    else:
        requested_entities = data_types

    # Execute save operation
    results = orchestrator.execute_save(repo_name, output_path, requested_entities)

    # Handle errors
    failed_operations = [r for r in results if not r["success"]]
    if failed_operations:
        error_messages = [r["error"] for r in failed_operations if r.get("error")]
        raise Exception(f"Save operation failed: {'; '.join(error_messages)}")
