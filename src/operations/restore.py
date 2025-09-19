"""
Restore actions for GitHub repository data.

Implements the restore functionality that reads JSON files and
recreates labels, issues, and comments in GitHub repositories.
"""

from pathlib import Path
from typing import List, Dict, Optional, TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from ..use_cases.restore.orchestration.restore_repository import (
        RestoreRepositoryUseCase,
    )

from ..github.protocols import RepositoryService
from ..github import converters
from ..entities import Label, Issue, Comment, PullRequest, PullRequestComment, SubIssue
from ..storage.protocols import StorageService


def restore_repository_data_with_services(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    data_path: str,
    label_conflict_strategy: str = "fail-if-existing",
    include_original_metadata: bool = True,
    include_prs: bool = False,
    include_sub_issues: bool = False,
) -> None:
    """Restore labels, issues, comments, PRs and sub-issues using injected services."""
    # Create orchestrator use case
    restore_use_case = _create_restore_repository_use_case(
        github_service, storage_service
    )

    # Execute with new use case architecture
    from ..use_cases.requests import RestoreRepositoryRequest

    request = RestoreRepositoryRequest(
        repository_name=repo_name,
        input_path=data_path,
        label_conflict_strategy=label_conflict_strategy,
        include_original_metadata=include_original_metadata,
        include_prs=include_prs,
        include_sub_issues=include_sub_issues,
    )

    results = restore_use_case.execute(request)

    # Handle errors (maintain existing behavior)
    failed_operations = [r for r in results if not r.success]
    if failed_operations:
        # Aggregate error messages maintaining backward compatibility
        error_messages = [r.error_message for r in failed_operations if r.error_message]
        raise Exception(f"Restore operation failed: {'; '.join(error_messages)}")


def _create_restore_repository_use_case(
    github_service: RepositoryService, storage_service: StorageService
) -> "RestoreRepositoryUseCase":
    """Factory function to create configured RestoreRepositoryUseCase."""
    from ..use_cases.restore.validation.validate_restore_data import (
        ValidateRestoreDataUseCase,
    )
    from ..use_cases.shared.processing.validate_repository_access import (
        ValidateRepositoryAccessUseCase,
    )
    from ..use_cases.restore.loading.load_labels import LoadLabelsUseCase
    from ..use_cases.restore.loading.load_issues import LoadIssuesUseCase
    from ..use_cases.restore.loading.load_comments import LoadCommentsUseCase
    from ..use_cases.restore.loading.load_pull_requests import LoadPullRequestsUseCase
    from ..use_cases.restore.loading.load_sub_issues import LoadSubIssuesUseCase
    from ..use_cases.restore.conflict_resolution.detect_conflicts import (
        DetectLabelConflictsUseCase,
    )
    from ..use_cases.restore.conflict_resolution.fail_if_existing_strategy import (
        FailIfExistingStrategyUseCase,
    )
    from ..use_cases.restore.conflict_resolution.fail_if_conflict_strategy import (
        FailIfConflictStrategyUseCase,
    )
    from ..use_cases.restore.conflict_resolution.delete_all_strategy import (
        DeleteAllStrategyUseCase,
    )
    from ..use_cases.restore.conflict_resolution.overwrite_strategy import (
        OverwriteStrategyUseCase,
    )
    from ..use_cases.restore.conflict_resolution.skip_strategy import (
        SkipStrategyUseCase,
    )
    from ..use_cases.restore.restoration.restore_labels import RestoreLabelsUseCase
    from ..use_cases.restore.restoration.restore_issues import RestoreIssuesUseCase
    from ..use_cases.restore.restoration.restore_comments import RestoreCommentsUseCase
    from ..use_cases.restore.restoration.restore_pull_requests import (
        RestorePullRequestsUseCase,
    )
    from ..use_cases.restore.restoration.restore_sub_issues import (
        RestoreSubIssuesUseCase,
    )
    from ..use_cases.restore.sub_issue_management.validate_sub_issue_data import (
        ValidateSubIssueDataUseCase,
    )
    from ..use_cases.restore.sub_issue_management.detect_circular_dependencies import (
        DetectCircularDependenciesUseCase,
    )
    from ..use_cases.restore.sub_issue_management.organize_by_depth import (
        OrganizeByDepthUseCase,
    )
    from ..use_cases.restore.orchestration.restore_repository import (
        RestoreRepositoryUseCase,
        RestoreJobFactory,
    )

    # Create validation use cases
    validate_data = ValidateRestoreDataUseCase()
    validate_access = ValidateRepositoryAccessUseCase(github_service)

    # Create loading use cases
    load_labels = LoadLabelsUseCase(storage_service)
    load_issues = LoadIssuesUseCase(storage_service)
    load_comments = LoadCommentsUseCase(storage_service)
    load_pull_requests = LoadPullRequestsUseCase(storage_service)
    load_sub_issues = LoadSubIssuesUseCase(storage_service)

    # Create conflict resolution use cases
    detect_conflicts = DetectLabelConflictsUseCase()
    fail_if_existing = FailIfExistingStrategyUseCase()
    fail_if_conflict = FailIfConflictStrategyUseCase(detect_conflicts)
    delete_all = DeleteAllStrategyUseCase(github_service)
    overwrite = OverwriteStrategyUseCase(github_service, detect_conflicts)
    skip = SkipStrategyUseCase(detect_conflicts)

    # Create restoration use cases
    restore_labels = RestoreLabelsUseCase(
        github_service, fail_if_existing, fail_if_conflict, delete_all, overwrite, skip
    )
    restore_issues = RestoreIssuesUseCase(github_service)
    restore_comments = RestoreCommentsUseCase(github_service)
    restore_pull_requests = RestorePullRequestsUseCase(github_service)
    restore_sub_issues = RestoreSubIssuesUseCase(github_service)

    # Create sub-issue management use cases
    validate_sub_issues = ValidateSubIssueDataUseCase()
    detect_circular_deps = DetectCircularDependenciesUseCase()
    organize_by_depth = OrganizeByDepthUseCase()

    # Create job factory with all use cases
    job_factory = RestoreJobFactory(
        load_labels=load_labels,
        load_issues=load_issues,
        load_comments=load_comments,
        load_pull_requests=load_pull_requests,
        load_sub_issues=load_sub_issues,
        restore_labels=restore_labels,
        restore_issues=restore_issues,
        restore_comments=restore_comments,
        restore_pull_requests=restore_pull_requests,
        restore_sub_issues=restore_sub_issues,
        validate_sub_issues=validate_sub_issues,
        detect_circular_deps=detect_circular_deps,
        organize_by_depth=organize_by_depth,
    )

    return RestoreRepositoryUseCase(
        validate_data=validate_data,
        validate_access=validate_access,
        job_factory=job_factory,
    )


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
    from ..strategies.restore_orchestrator import StrategyBasedRestoreOrchestrator

    orchestrator = StrategyBasedRestoreOrchestrator(github_service, storage_service)

    # Register strategies
    from ..entities.labels.restore_strategy import (
        LabelsRestoreStrategy,
        create_conflict_strategy,
    )
    from ..entities.issues.restore_strategy import IssuesRestoreStrategy
    from ..entities.comments.restore_strategy import CommentsRestoreStrategy

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
        from ..entities.pull_requests.restore_strategy import (
            PullRequestsRestoreStrategy,
            create_conflict_strategy as create_pr_conflict_strategy,
        )
        from ..entities.pr_comments.restore_strategy import (
            PullRequestCommentsRestoreStrategy,
            create_conflict_strategy as create_pr_comment_conflict_strategy,
        )

        pr_conflict_strategy = create_pr_conflict_strategy()
        pr_comment_conflict_strategy = create_pr_comment_conflict_strategy()

        orchestrator.register_strategy(
            PullRequestsRestoreStrategy(
                pr_conflict_strategy, include_original_metadata
            )
        )
        orchestrator.register_strategy(
            PullRequestCommentsRestoreStrategy(
                pr_comment_conflict_strategy, include_original_metadata
            )
        )

    # Add sub-issues strategy if requested
    if include_sub_issues:
        from ..entities.sub_issues.restore_strategy import SubIssuesRestoreStrategy

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


def _validate_data_files_exist(
    input_dir: Path, include_prs: bool = False, include_sub_issues: bool = False
) -> None:
    """Validate that required data files exist."""
    required_files = ["labels.json", "issues.json", "comments.json"]

    if include_prs:
        required_files.extend(["pull_requests.json", "pr_comments.json"])

    if include_sub_issues:
        required_files.append("sub_issues.json")

    for filename in required_files:
        file_path = input_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Required data file not found: {file_path}")


def _restore_labels(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    input_dir: Path,
    conflict_strategy: str,
) -> None:
    """Restore labels to the repository using specified conflict strategy."""
    from ..conflict_strategies import parse_conflict_strategy, LabelConflictStrategy

    strategy = parse_conflict_strategy(conflict_strategy)
    labels_to_restore = _load_labels_from_file(storage_service, input_dir)

    print(f"Using label conflict strategy: {strategy.value}")

    # Get existing labels for conflict detection
    raw_existing_labels = github_service.get_repository_labels(repo_name)
    existing_labels = [
        converters.convert_to_label(label_dict) for label_dict in raw_existing_labels
    ]

    # Apply conflict resolution strategy
    if strategy == LabelConflictStrategy.FAIL_IF_EXISTING:
        _handle_fail_if_existing(existing_labels)
    elif strategy == LabelConflictStrategy.FAIL_IF_CONFLICT:
        _handle_fail_if_conflict(existing_labels, labels_to_restore)
    elif strategy == LabelConflictStrategy.DELETE_ALL:
        _handle_delete_all(github_service, repo_name, existing_labels)
        existing_labels = []  # No conflicts after deletion
    elif strategy == LabelConflictStrategy.OVERWRITE:
        _handle_overwrite(github_service, repo_name, existing_labels, labels_to_restore)
        return  # Overwrite strategy handles all label creation
    elif strategy == LabelConflictStrategy.SKIP:
        labels_to_restore = _handle_skip(existing_labels, labels_to_restore)

    # Create remaining labels (after filtering if using skip strategy)
    _create_repository_labels(github_service, repo_name, labels_to_restore)


def _restore_issues(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    input_dir: Path,
    include_original_metadata: bool = True,
) -> Dict[int, int]:
    """Restore issues and return mapping of original to new issue numbers."""
    issues = _load_issues_from_file(storage_service, input_dir)
    return _create_repository_issues(
        github_service, repo_name, issues, include_original_metadata
    )


def _load_labels_from_file(
    storage_service: StorageService, input_dir: Path
) -> List[Label]:
    """Load labels from labels.json file."""
    labels_file = input_dir / "labels.json"
    return storage_service.load_data(labels_file, Label)


def _load_issues_from_file(
    storage_service: StorageService, input_dir: Path
) -> List[Issue]:
    """Load issues from issues.json file."""
    issues_file = input_dir / "issues.json"
    return storage_service.load_data(issues_file, Issue)


def _load_comments_from_file(
    storage_service: StorageService, input_dir: Path
) -> List[Comment]:
    """Load comments from comments.json file."""
    comments_file = input_dir / "comments.json"
    return storage_service.load_data(comments_file, Comment)


def _load_pull_requests_from_file(
    storage_service: StorageService, input_dir: Path
) -> List[PullRequest]:
    """Load pull requests from pull_requests.json file."""
    prs_file = input_dir / "pull_requests.json"
    return storage_service.load_data(prs_file, PullRequest)


def _load_pr_comments_from_file(
    storage_service: StorageService, input_dir: Path
) -> List[PullRequestComment]:
    """Load PR comments from pr_comments.json file."""
    pr_comments_file = input_dir / "pr_comments.json"
    return storage_service.load_data(pr_comments_file, PullRequestComment)


def _load_sub_issues_from_file(
    storage_service: StorageService, input_dir: Path
) -> List[SubIssue]:
    """Load sub-issues from sub_issues.json file."""
    sub_issues_file = input_dir / "sub_issues.json"
    return storage_service.load_data(sub_issues_file, SubIssue)


def _restore_comments(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    input_dir: Path,
    issue_number_mapping: Dict[int, int],
    include_original_metadata: bool = True,
) -> None:
    """Restore comments to the repository using issue number mapping."""
    comments = _load_comments_from_file(storage_service, input_dir)
    # Sort comments by creation time to maintain chronological conversation order
    sorted_comments = sorted(comments, key=lambda comment: comment.created_at)
    _create_repository_comments(
        github_service,
        repo_name,
        sorted_comments,
        issue_number_mapping,
        include_original_metadata,
    )


def _create_repository_labels(
    github_service: RepositoryService, repo_name: str, labels: List[Label]
) -> None:
    """Create labels in the repository."""
    for label in labels:
        try:
            github_service.create_label(
                repo_name, label.name, label.color, label.description or ""
            )
            print(f"Created label: {label.name}")
        except Exception as e:
            raise RuntimeError(f"Failed to create label '{label.name}': {e}") from e


def _create_repository_issues(
    github_service: RepositoryService,
    repo_name: str,
    issues: List[Issue],
    include_original_metadata: bool = True,
) -> Dict[int, int]:
    """Create issues and return mapping of original to new issue numbers."""
    issue_number_mapping = {}

    for issue in issues:
        try:
            # Prepare issue data for creation
            if include_original_metadata:
                from ..github.metadata import add_issue_metadata_footer

                issue_body = add_issue_metadata_footer(issue)
            else:
                issue_body = issue.body or ""

            # Convert labels to string names
            label_names = [label.name for label in issue.labels]

            created_issue_data = github_service.create_issue(
                repo_name, issue.title, issue_body, label_names
            )
            issue_number_mapping[issue.number] = created_issue_data["number"]
            print(
                f"Created issue #{created_issue_data['number']}: "
                f"{created_issue_data['title']} (was #{issue.number})"
            )

            # Close the issue if it was originally closed
            if issue.state == "closed":
                try:
                    github_service.close_issue(
                        repo_name, created_issue_data["number"], issue.state_reason
                    )
                    reason_text = (
                        f"with reason: {issue.state_reason}"
                        if issue.state_reason
                        else ""
                    )
                    print(f"Closed issue #{created_issue_data['number']} {reason_text}")
                except Exception as e:
                    print(
                        f"Warning: Failed to close issue "
                        f"#{created_issue_data['number']}: {e}"
                    )

        except Exception as e:
            raise RuntimeError(f"Failed to create issue '{issue.title}': {e}") from e

    return issue_number_mapping


def _handle_fail_if_existing(existing_labels: List[Label]) -> None:
    """Handle fail-if-existing strategy."""
    if existing_labels:
        raise RuntimeError(
            f"Repository has {len(existing_labels)} existing labels. "
            f"Set LABEL_CONFLICT_STRATEGY to allow restoration with existing labels."
        )


def _handle_fail_if_conflict(
    existing_labels: List[Label], labels_to_restore: List[Label]
) -> None:
    """Handle fail-if-conflict strategy."""
    from ..conflict_strategies import detect_label_conflicts

    conflicts = detect_label_conflicts(existing_labels, labels_to_restore)
    if conflicts:
        raise RuntimeError(
            f"Label name conflicts detected: {', '.join(conflicts)}. "
            f"Set LABEL_CONFLICT_STRATEGY to resolve conflicts automatically."
        )


def _handle_delete_all(
    github_service: RepositoryService, repo_name: str, existing_labels: List[Label]
) -> None:
    """Handle delete-all strategy."""
    if existing_labels:
        print(f"Deleting {len(existing_labels)} existing labels...")
        for label in existing_labels:
            try:
                github_service.delete_label(repo_name, label.name)
                print(f"Deleted label: {label.name}")
            except Exception as e:
                raise RuntimeError(f"Failed to delete label '{label.name}': {e}") from e


def _handle_overwrite(
    github_service: RepositoryService,
    repo_name: str,
    existing_labels: List[Label],
    labels_to_restore: List[Label],
) -> None:
    """Handle overwrite strategy."""
    existing_names = {label.name for label in existing_labels}

    for label in labels_to_restore:
        try:
            if label.name in existing_names:
                # Update existing label
                github_service.update_label(
                    repo_name,
                    label.name,
                    label.name,
                    label.color,
                    label.description or "",
                )
                print(f"Updated label: {label.name}")
            else:
                # Create new label
                github_service.create_label(
                    repo_name, label.name, label.color, label.description or ""
                )
                print(f"Created label: {label.name}")
        except Exception as e:
            action = "update" if label.name in existing_names else "create"
            raise RuntimeError(f"Failed to {action} label '{label.name}': {e}") from e


def _handle_skip(
    existing_labels: List[Label], labels_to_restore: List[Label]
) -> List[Label]:
    """Handle skip strategy."""
    existing_names = {label.name for label in existing_labels}
    non_conflicting_labels = [
        label for label in labels_to_restore if label.name not in existing_names
    ]

    skipped_count = len(labels_to_restore) - len(non_conflicting_labels)
    if skipped_count > 0:
        print(f"Skipping {skipped_count} labels that already exist")

    return non_conflicting_labels


def _create_repository_comments(
    github_service: RepositoryService,
    repo_name: str,
    comments: List[Comment],
    issue_number_mapping: Dict[int, int],
    include_original_metadata: bool = True,
) -> None:
    """Create comments in the repository using issue number mapping."""
    for comment in comments:
        try:
            original_issue_number = _extract_issue_number_from_url(comment.issue_url)
            new_issue_number = issue_number_mapping.get(original_issue_number)

            if new_issue_number is None:
                print(
                    f"Warning: Skipping comment for unmapped issue "
                    f"#{original_issue_number}"
                )
                continue

            # Prepare comment body with metadata if needed
            if include_original_metadata:
                from ..github.metadata import add_comment_metadata_footer

                comment_body = add_comment_metadata_footer(comment)
            else:
                comment_body = comment.body

            github_service.create_issue_comment(
                repo_name, new_issue_number, comment_body
            )
            print(
                f"Created comment for issue #{new_issue_number} "
                f"(was #{original_issue_number})"
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to create comment for issue #{original_issue_number}: {e}"
            ) from e


def _restore_pull_requests(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    input_dir: Path,
    include_original_metadata: bool = True,
) -> Dict[int, int]:
    """Restore pull requests and return mapping of original to new PR numbers."""
    pull_requests = _load_pull_requests_from_file(storage_service, input_dir)
    return _create_repository_pull_requests(
        github_service, repo_name, pull_requests, include_original_metadata
    )


def _restore_pr_comments(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    input_dir: Path,
    pr_number_mapping: Dict[int, int],
    include_original_metadata: bool = True,
) -> None:
    """Restore PR comments to the repository using PR number mapping."""
    pr_comments = _load_pr_comments_from_file(storage_service, input_dir)
    # Sort comments by creation time to maintain chronological conversation order
    sorted_comments = sorted(pr_comments, key=lambda comment: comment.created_at)
    _create_repository_pr_comments(
        github_service,
        repo_name,
        sorted_comments,
        pr_number_mapping,
        include_original_metadata,
    )


def _create_repository_pull_requests(
    github_service: RepositoryService,
    repo_name: str,
    pull_requests: List[PullRequest],
    include_original_metadata: bool = True,
) -> Dict[int, int]:
    """Create pull requests and return mapping of original to new PR numbers."""
    pr_number_mapping = {}

    for pr in pull_requests:
        try:
            # Prepare PR data for creation
            if include_original_metadata:
                from ..github.metadata import add_pr_metadata_footer

                pr_body = add_pr_metadata_footer(pr)
            else:
                pr_body = pr.body or ""

            # Note: PR creation has limitations - branches must exist and
            # original timestamps/merge status cannot be restored
            print(
                f"Warning: Creating PR will have current timestamp, "
                f"not original {pr.created_at}"
            )
            print(f"Warning: Ensure branches '{pr.base_ref}' and '{pr.head_ref}' exist")

            created_pr_data = github_service.create_pull_request(
                repo_name, pr.title, pr_body, pr.head_ref, pr.base_ref
            )
            pr_number_mapping[pr.number] = created_pr_data["number"]
            print(
                f"Created PR #{created_pr_data['number']}: "
                f"{created_pr_data['title']} (was #{pr.number})"
            )

        except Exception as e:
            print(f"Warning: Failed to create PR '{pr.title}': {e}")
            print(f"Skipping PR #{pr.number} and its comments")
            continue

    return pr_number_mapping


def _create_repository_pr_comments(
    github_service: RepositoryService,
    repo_name: str,
    pr_comments: List[PullRequestComment],
    pr_number_mapping: Dict[int, int],
    include_original_metadata: bool = True,
) -> None:
    """Create PR comments in the repository using PR number mapping."""
    for comment in pr_comments:
        try:
            original_pr_number = _extract_pr_number_from_url(comment.pull_request_url)
            new_pr_number = pr_number_mapping.get(original_pr_number)

            if new_pr_number is None:
                print(
                    f"Warning: Skipping comment for unmapped PR "
                    f"#{original_pr_number}"
                )
                continue

            # Prepare comment body with metadata if needed
            if include_original_metadata:
                from ..github.metadata import add_pr_comment_metadata_footer

                comment_body = add_pr_comment_metadata_footer(comment)
            else:
                comment_body = comment.body

            github_service.create_pull_request_comment(
                repo_name, new_pr_number, comment_body
            )
            print(
                f"Created PR comment for PR #{new_pr_number} "
                f"(was #{original_pr_number})"
            )
        except Exception as e:
            print(f"Warning: Failed to create PR comment: {e}")
            continue


def _extract_issue_number_from_url(issue_url: str) -> int:
    """Extract issue number from GitHub issue URL."""
    # Example URL: https://api.github.com/repos/owner/repo/issues/123
    try:
        parsed_url = urlparse(issue_url)
        path_parts = parsed_url.path.strip("/").split("/")

        # Find 'issues' in path and get the next part
        if "issues" in path_parts:
            issues_index = path_parts.index("issues")
            if issues_index + 1 < len(path_parts):
                return int(path_parts[issues_index + 1])

        raise ValueError(f"Could not find issue number in URL path: {parsed_url.path}")
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid issue URL format: {issue_url}") from e


def _extract_pr_number_from_url(pr_url: str) -> int:
    """Extract PR number from GitHub pull request URL."""
    # Example URL: https://github.com/owner/repo/pull/123
    try:
        parsed_url = urlparse(pr_url)
        path_parts = parsed_url.path.strip("/").split("/")

        # Find 'pull' in path and get the next part
        if "pull" in path_parts:
            pull_index = path_parts.index("pull")
            if pull_index + 1 < len(path_parts):
                return int(path_parts[pull_index + 1])

        raise ValueError(f"Could not find PR number in URL path: {parsed_url.path}")
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid PR URL format: {pr_url}") from e


def _restore_sub_issues(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    input_dir: Path,
    issue_number_mapping: Dict[int, int],
) -> None:
    """Restore sub-issue relationships using issue number mapping (two-phase)."""
    sub_issues = _load_sub_issues_from_file(storage_service, input_dir)

    if not sub_issues:
        print("No sub-issues to restore")
        return

    print(f"Restoring {len(sub_issues)} sub-issue relationships...")

    # Group sub-issues by hierarchy depth for proper dependency order
    sub_issues_by_depth = _organize_sub_issues_by_depth(
        sub_issues, issue_number_mapping
    )

    for depth in sorted(sub_issues_by_depth.keys()):
        depth_sub_issues = sub_issues_by_depth[depth]
        print(f"Processing depth {depth}: {len(depth_sub_issues)} relationships")

        for sub_issue in depth_sub_issues:
            try:
                original_parent_number = sub_issue.parent_issue_number
                original_sub_issue_number = sub_issue.sub_issue_number

                new_parent_number = issue_number_mapping.get(original_parent_number)
                new_sub_issue_number = issue_number_mapping.get(
                    original_sub_issue_number
                )

                if new_parent_number is None:
                    print(
                        f"Warning: Skipping sub-issue - "
                        f"parent issue #{original_parent_number} not found"
                    )
                    continue

                if new_sub_issue_number is None:
                    print(
                        f"Warning: Skipping sub-issue - "
                        f"sub-issue #{original_sub_issue_number} not found"
                    )
                    continue

                # Validate hierarchy depth (GitHub limit is 8 levels)
                if depth > 8:
                    print(
                        f"Warning: Sub-issue depth {depth} exceeds "
                        f"GitHub limit of 8 levels, skipping"
                    )
                    continue

                github_service.add_sub_issue(
                    repo_name, new_parent_number, new_sub_issue_number
                )
                print(
                    f"Added sub-issue #{new_sub_issue_number} to "
                    f"parent #{new_parent_number} "
                    f"(was #{original_sub_issue_number} -> #{original_parent_number})"
                )

            except Exception as e:
                print(
                    f"Warning: Failed to restore sub-issue relationship "
                    f"#{original_sub_issue_number} -> #{original_parent_number}: {e}"
                )
                continue


def _organize_sub_issues_by_depth(
    sub_issues: List[SubIssue], issue_number_mapping: Dict[int, int]
) -> Dict[int, List[SubIssue]]:
    """Organize sub-issues by hierarchy depth to ensure proper dependency order."""
    # Build parent-child mapping for depth calculation
    children_by_parent: Dict[int, List[int]] = {}
    parents_by_child: Dict[int, int] = {}

    for sub_issue in sub_issues:
        parent_id = sub_issue.parent_issue_number
        child_id = sub_issue.sub_issue_number

        # Only include if both issues exist in mapping
        if parent_id in issue_number_mapping and child_id in issue_number_mapping:
            if parent_id not in children_by_parent:
                children_by_parent[parent_id] = []
            children_by_parent[parent_id].append(child_id)
            parents_by_child[child_id] = parent_id

    # Calculate depth for each sub-issue
    depth_by_sub_issue: Dict[int, int] = {}

    def calculate_depth(issue_id: int, visited: Optional[set[int]] = None) -> int:
        if visited is None:
            visited = set()

        if issue_id in visited:
            # Circular dependency detected
            print(f"Warning: Circular dependency detected involving issue #{issue_id}")
            return 1

        if issue_id in depth_by_sub_issue:
            return depth_by_sub_issue[issue_id]

        visited.add(issue_id)

        if issue_id not in parents_by_child:
            # Root issue (no parent)
            depth = 1
        else:
            parent_id = parents_by_child[issue_id]
            depth = calculate_depth(parent_id, visited.copy()) + 1

        depth_by_sub_issue[issue_id] = depth
        return depth

    # Calculate depths for all sub-issues
    for sub_issue in sub_issues:
        if (
            sub_issue.parent_issue_number in issue_number_mapping
            and sub_issue.sub_issue_number in issue_number_mapping
        ):
            calculate_depth(sub_issue.sub_issue_number)

    # Group by depth
    sub_issues_by_depth: Dict[int, List[SubIssue]] = {}
    for sub_issue in sub_issues:
        if (
            sub_issue.parent_issue_number in issue_number_mapping
            and sub_issue.sub_issue_number in issue_number_mapping
        ):
            depth = depth_by_sub_issue.get(sub_issue.sub_issue_number, 1)
            if depth not in sub_issues_by_depth:
                sub_issues_by_depth[depth] = []
            sub_issues_by_depth[depth].append(sub_issue)

    return sub_issues_by_depth
