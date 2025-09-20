"""
Restore actions for GitHub repository data.

Implements the restore functionality that reads JSON files and
recreates labels, issues, and comments in GitHub repositories.
"""

from src.github.protocols import RepositoryService
from src.storage.protocols import StorageService


def restore_repository_data_with_strategy_pattern(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    data_path: str,
    label_conflict_strategy: str = "fail-if-existing",
    include_original_metadata: bool = True,
    include_prs: bool = False,
    include_sub_issues: bool = False,
) -> None:
    """Restore using strategy pattern approach."""

    # Create orchestrator
    from .orchestrator import StrategyBasedRestoreOrchestrator

    orchestrator = StrategyBasedRestoreOrchestrator(github_service, storage_service)

    # Register strategies
    from src.operations.restore.strategies.labels_strategy import (
        LabelsRestoreStrategy,
        create_conflict_strategy,
    )
    from src.operations.restore.strategies.issues_strategy import IssuesRestoreStrategy
    from src.operations.restore.strategies.comments_strategy import (
        CommentsRestoreStrategy,
    )

    # Create conflict resolution strategy
    conflict_strategy = create_conflict_strategy(
        label_conflict_strategy, github_service
    )

    # Register entity strategies
    orchestrator.register_strategy(LabelsRestoreStrategy(conflict_strategy))
    orchestrator.register_strategy(IssuesRestoreStrategy(include_original_metadata))
    orchestrator.register_strategy(CommentsRestoreStrategy(include_original_metadata))

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

    # Determine entities to restore
    requested_entities = ["labels", "issues", "comments"]
    if include_prs:
        requested_entities.extend(["pull_requests", "pr_comments"])
    if include_sub_issues:
        requested_entities.append("sub_issues")

    # Execute restoration
    results = orchestrator.execute_restore(repo_name, data_path, requested_entities)

    # Handle errors (maintain backward compatibility)
    failed_operations = [r for r in results if not r["success"]]
    if failed_operations:
        error_messages = [r["error"] for r in failed_operations if r.get("error")]
        raise Exception(f"Restore operation failed: {'; '.join(error_messages)}")
