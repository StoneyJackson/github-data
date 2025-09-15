"""
Save actions for GitHub repository data.

Implements the save functionality that extracts labels, issues,
and comments from GitHub repositories and saves them to JSON files.
"""

from pathlib import Path
from typing import List

from ..github import create_github_service
from ..github.service import GitHubService
from ..github import converters
from ..models import (
    RepositoryData,
    Label,
    Issue,
    Comment,
    PullRequest,
    PullRequestComment,
)
from ..storage.json_storage import save_json_data


def save_repository_data(github_token: str, repo_name: str, data_path: str) -> None:
    """Save GitHub repository labels, issues, and comments to JSON files."""
    client = create_github_service(github_token)
    output_dir = Path(data_path)

    repository_data = _collect_repository_data(client, repo_name)
    _save_data_to_files(repository_data, output_dir)


def _collect_repository_data(client: GitHubService, repo_name: str) -> RepositoryData:
    """Collect all repository data from GitHub API."""
    labels = _fetch_repository_labels(client, repo_name)
    issues = _fetch_repository_issues(client, repo_name)
    comments = _fetch_all_issue_comments(client, repo_name)
    pull_requests = _fetch_repository_pull_requests(client, repo_name)
    pr_comments = _fetch_all_pr_comments(client, repo_name)

    return _create_repository_data(
        repo_name, labels, issues, comments, pull_requests, pr_comments
    )


def _create_repository_data(
    repo_name: str,
    labels: List[Label],
    issues: List[Issue],
    comments: List[Comment],
    pull_requests: List[PullRequest],
    pr_comments: List[PullRequestComment],
) -> RepositoryData:
    """Create RepositoryData instance with current timestamp."""
    from datetime import datetime

    return RepositoryData(
        repository_name=repo_name,
        exported_at=datetime.now(),
        labels=labels,
        issues=issues,
        comments=comments,
        pull_requests=pull_requests,
        pr_comments=pr_comments,
    )


def _save_data_to_files(repository_data: RepositoryData, output_dir: Path) -> None:
    """Save repository data to separate JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    _save_labels_to_file(repository_data.labels, output_dir)
    _save_issues_to_file(repository_data.issues, output_dir)
    _save_comments_to_file(repository_data.comments, output_dir)
    _save_pull_requests_to_file(repository_data.pull_requests, output_dir)
    _save_pr_comments_to_file(repository_data.pr_comments, output_dir)


def _fetch_repository_labels(client: GitHubService, repo_name: str) -> List[Label]:
    """Fetch all labels from the repository."""
    raw_labels = client.get_repository_labels(repo_name)
    return [converters.convert_to_label(label_dict) for label_dict in raw_labels]


def _fetch_repository_issues(client: GitHubService, repo_name: str) -> List[Issue]:
    """Fetch all issues from the repository."""
    raw_issues = client.get_repository_issues(repo_name)
    return [converters.convert_to_issue(issue_dict) for issue_dict in raw_issues]


def _fetch_all_issue_comments(client: GitHubService, repo_name: str) -> List[Comment]:
    """Fetch all comments from all issues in the repository."""
    raw_comments = client.get_all_issue_comments(repo_name)
    return [
        converters.convert_to_comment(comment_dict) for comment_dict in raw_comments
    ]


def _fetch_repository_pull_requests(
    client: GitHubService, repo_name: str
) -> List[PullRequest]:
    """Fetch all pull requests from the repository."""
    raw_prs = client.get_repository_pull_requests(repo_name)
    return [converters.convert_to_pull_request(pr_dict) for pr_dict in raw_prs]


def _fetch_all_pr_comments(
    client: GitHubService, repo_name: str
) -> List[PullRequestComment]:
    """Fetch all comments from all pull requests in the repository."""
    raw_comments = client.get_all_pull_request_comments(repo_name)
    return [
        converters.convert_to_pr_comment(comment_dict) for comment_dict in raw_comments
    ]


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


def _save_pull_requests_to_file(
    pull_requests: List[PullRequest], output_dir: Path
) -> None:
    """Save pull requests to pull_requests.json file."""
    prs_file = output_dir / "pull_requests.json"
    save_json_data(pull_requests, prs_file)


def _save_pr_comments_to_file(
    pr_comments: List[PullRequestComment], output_dir: Path
) -> None:
    """Save PR comments to pr_comments.json file."""
    pr_comments_file = output_dir / "pr_comments.json"
    save_json_data(pr_comments, pr_comments_file)
