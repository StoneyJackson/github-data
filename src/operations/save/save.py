"""
Save actions for GitHub repository data.

Implements the save functionality that collects GitHub data and
saves it to JSON files for backup purposes.
"""

from typing import List, Optional
from src.github.protocols import RepositoryService
from src.storage.protocols import StorageService
from src.git.protocols import GitRepositoryService


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
    """Save using strategy pattern approach."""

    # Create orchestrator
    from .orchestrator import StrategyBasedSaveOrchestrator

    orchestrator = StrategyBasedSaveOrchestrator(github_service, storage_service)

    # Register strategies directly in operations (not entities)
    from .strategies.labels_strategy import LabelsSaveStrategy
    from .strategies.issues_strategy import IssuesSaveStrategy
    from .strategies.comments_strategy import CommentsSaveStrategy

    # Register entity strategies
    orchestrator.register_strategy(LabelsSaveStrategy())
    orchestrator.register_strategy(IssuesSaveStrategy())
    orchestrator.register_strategy(CommentsSaveStrategy())

    # Add PR strategies if requested
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
    if include_git_repo and git_service:
        from .strategies.git_repository_strategy import GitRepositoryStrategy

        orchestrator.register_strategy(GitRepositoryStrategy(git_service))

    # Determine entities to save
    if data_types is None:
        requested_entities = ["labels", "issues", "comments"]
        if include_prs:
            requested_entities.extend(["pull_requests", "pr_comments"])
        if include_sub_issues:
            requested_entities.append("sub_issues")
        if include_git_repo and git_service:
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
