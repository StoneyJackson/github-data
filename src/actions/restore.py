"""
Restore actions for GitHub repository data.

Implements the restore functionality that reads JSON files and
recreates labels, issues, and comments in GitHub repositories.
"""

from pathlib import Path
from typing import List

from ..github import GitHubService
from ..models import Label, Issue, Comment
from ..storage.json_storage import load_json_data


def restore_repository_data(
    github_token: str,
    repo_name: str,
    data_path: str,
    label_conflict_strategy: str = "fail-if-existing",
) -> None:
    """Restore GitHub repository labels, issues, and comments from JSON files."""
    client = GitHubService(github_token)
    input_dir = Path(data_path)

    _validate_data_files_exist(input_dir)

    _restore_labels(client, repo_name, input_dir, label_conflict_strategy)
    _restore_issues(client, repo_name, input_dir)
    # Note: Comments are typically restored as part of issues
    # or through separate comment creation API calls


def _validate_data_files_exist(input_dir: Path) -> None:
    """Validate that required data files exist."""
    required_files = ["labels.json", "issues.json", "comments.json"]

    for filename in required_files:
        file_path = input_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Required data file not found: {file_path}")


def _restore_labels(
    client: GitHubService, repo_name: str, input_dir: Path, conflict_strategy: str
) -> None:
    """Restore labels to the repository using specified conflict strategy."""
    from ..conflict_strategies import parse_conflict_strategy, LabelConflictStrategy

    strategy = parse_conflict_strategy(conflict_strategy)
    labels_to_restore = _load_labels_from_file(input_dir)

    print(f"Using label conflict strategy: {strategy.value}")

    # Get existing labels for conflict detection
    existing_labels = client.get_repository_labels(repo_name)

    # Apply conflict resolution strategy
    if strategy == LabelConflictStrategy.FAIL_IF_EXISTING:
        _handle_fail_if_existing(existing_labels)
    elif strategy == LabelConflictStrategy.FAIL_IF_CONFLICT:
        _handle_fail_if_conflict(existing_labels, labels_to_restore)
    elif strategy == LabelConflictStrategy.DELETE_ALL:
        _handle_delete_all(client, repo_name, existing_labels)
        existing_labels = []  # No conflicts after deletion
    elif strategy == LabelConflictStrategy.OVERWRITE:
        _handle_overwrite(client, repo_name, existing_labels, labels_to_restore)
        return  # Overwrite strategy handles all label creation
    elif strategy == LabelConflictStrategy.SKIP:
        labels_to_restore = _handle_skip(existing_labels, labels_to_restore)

    # Create remaining labels (after filtering if using skip strategy)
    _create_repository_labels(client, repo_name, labels_to_restore)


def _restore_issues(client: GitHubService, repo_name: str, input_dir: Path) -> None:
    """Restore issues to the repository."""
    issues = _load_issues_from_file(input_dir)
    _create_repository_issues(client, repo_name, issues)


def _load_labels_from_file(input_dir: Path) -> List[Label]:
    """Load labels from labels.json file."""
    labels_file = input_dir / "labels.json"
    return load_json_data(labels_file, Label)


def _load_issues_from_file(input_dir: Path) -> List[Issue]:
    """Load issues from issues.json file."""
    issues_file = input_dir / "issues.json"
    return load_json_data(issues_file, Issue)


def _load_comments_from_file(input_dir: Path) -> List[Comment]:
    """Load comments from comments.json file."""
    comments_file = input_dir / "comments.json"
    return load_json_data(comments_file, Comment)


def _create_repository_labels(
    client: GitHubService, repo_name: str, labels: List[Label]
) -> None:
    """Create labels in the repository."""
    for label in labels:
        try:
            client.create_label(repo_name, label)
            print(f"Created label: {label.name}")
        except Exception as e:
            raise RuntimeError(f"Failed to create label '{label.name}': {e}") from e


def _create_repository_issues(
    client: GitHubService, repo_name: str, issues: List[Issue]
) -> None:
    """Create issues in the repository."""
    for issue in issues:
        try:
            created_issue = client.create_issue(repo_name, issue)
            print(f"Created issue #{created_issue.number}: {created_issue.title}")
        except Exception as e:
            raise RuntimeError(f"Failed to create issue '{issue.title}': {e}") from e


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
    client: GitHubService, repo_name: str, existing_labels: List[Label]
) -> None:
    """Handle delete-all strategy."""
    if existing_labels:
        print(f"Deleting {len(existing_labels)} existing labels...")
        for label in existing_labels:
            try:
                client.delete_label(repo_name, label.name)
                print(f"Deleted label: {label.name}")
            except Exception as e:
                raise RuntimeError(f"Failed to delete label '{label.name}': {e}") from e


def _handle_overwrite(
    client: GitHubService,
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
                client.update_label(repo_name, label.name, label)
                print(f"Updated label: {label.name}")
            else:
                # Create new label
                client.create_label(repo_name, label)
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
