"""
Save actions for GitHub repository data.

Implements the save functionality that extracts labels, issues,
and comments from GitHub repositories and saves them to JSON files.
"""

from pathlib import Path
from typing import List

from ..github import GitHubService
from ..models import RepositoryData, Label, Issue, Comment
from ..storage.json_storage import save_json_data


def save_repository_data(github_token: str, repo_name: str, data_path: str) -> None:
    """Save GitHub repository labels, issues, and comments to JSON files."""
    client = GitHubService(github_token)
    output_dir = Path(data_path)

    repository_data = _collect_repository_data(client, repo_name)
    _save_data_to_files(repository_data, output_dir)


def _collect_repository_data(client: GitHubService, repo_name: str) -> RepositoryData:
    """Collect all repository data from GitHub API."""
    from datetime import datetime

    labels = _fetch_repository_labels(client, repo_name)
    issues = _fetch_repository_issues(client, repo_name)
    comments = _fetch_all_issue_comments(client, repo_name)

    return RepositoryData(
        repository_name=repo_name,
        exported_at=datetime.now(),
        labels=labels,
        issues=issues,
        comments=comments,
    )


def _save_data_to_files(repository_data: RepositoryData, output_dir: Path) -> None:
    """Save repository data to separate JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    _save_labels_to_file(repository_data.labels, output_dir)
    _save_issues_to_file(repository_data.issues, output_dir)
    _save_comments_to_file(repository_data.comments, output_dir)


def _fetch_repository_labels(client: GitHubService, repo_name: str) -> List[Label]:
    """Fetch all labels from the repository."""
    return client.get_repository_labels(repo_name)


def _fetch_repository_issues(client: GitHubService, repo_name: str) -> List[Issue]:
    """Fetch all issues from the repository."""
    return client.get_repository_issues(repo_name)


def _fetch_all_issue_comments(client: GitHubService, repo_name: str) -> List[Comment]:
    """Fetch all comments from all issues in the repository."""
    return client.get_all_issue_comments(repo_name)


def _save_labels_to_file(labels: List[Label], output_dir: Path) -> None:
    """Save labels to labels.json file."""
    labels_file = output_dir / "labels.json"
    save_json_data(labels, labels_file)


def _save_issues_to_file(issues: List[Issue], output_dir: Path) -> None:
    """Save issues to issues.json file."""
    issues_file = output_dir / "issues.json"
    save_json_data(issues, issues_file)


def _save_comments_to_file(comments: List[Comment], output_dir: Path) -> None:
    """Save comments to comments.json file."""
    comments_file = output_dir / "comments.json"
    save_json_data(comments, comments_file)
