"""
Restore actions for GitHub repository data.

Implements the restore functionality that reads JSON files and
recreates labels, issues, and comments in GitHub repositories.
"""

from pathlib import Path
from typing import List

from ..github_client import GitHubClient
from ..models import Label, Issue, Comment
from ..storage.json_storage import load_json_data


def restore_repository_data(github_token: str, repo_name: str, data_path: str) -> None:
    """Restore GitHub repository labels, issues, and comments from JSON files."""
    client = GitHubClient(github_token)
    input_dir = Path(data_path)

    _validate_data_files_exist(input_dir)

    _restore_labels(client, repo_name, input_dir)
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


def _restore_labels(client: GitHubClient, repo_name: str, input_dir: Path) -> None:
    """Restore labels to the repository."""
    labels = _load_labels_from_file(input_dir)
    _create_repository_labels(client, repo_name, labels)


def _restore_issues(client: GitHubClient, repo_name: str, input_dir: Path) -> None:
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
    client: GitHubClient, repo_name: str, labels: List[Label]
) -> None:
    """Create labels in the repository."""
    for label in labels:
        try:
            client.create_label(repo_name, label)
            print(f"Created label: {label.name}")
        except Exception as e:
            print(f"Failed to create label {label.name}: {e}")


def _create_repository_issues(
    client: GitHubClient, repo_name: str, issues: List[Issue]
) -> None:
    """Create issues in the repository."""
    for issue in issues:
        try:
            created_issue = client.create_issue(repo_name, issue)
            print(f"Created issue #{created_issue.number}: {created_issue.title}")
        except Exception as e:
            print(f"Failed to create issue '{issue.title}': {e}")
