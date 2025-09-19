"""
Save actions for GitHub repository data.

Implements the save functionality that extracts labels, issues,
and comments from GitHub repositories and saves them to JSON files.
"""

from pathlib import Path
from typing import List, Dict, Any

from src.github.protocols import RepositoryService
from src.github import converters
from src.entities import (
    RepositoryData,
    Label,
    Issue,
    Comment,
    PullRequest,
    PullRequestComment,
    SubIssue,
)
from src.storage.protocols import StorageService


def save_repository_data_with_services(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    data_path: str,
) -> None:
    """Save GitHub repository data using injected services."""
    # Create use case instances
    save_use_case = _create_save_repository_use_case(github_service, storage_service)

    # Execute with new use case
    from src.use_cases.requests import SaveRepositoryRequest

    request = SaveRepositoryRequest(repository_name=repo_name, output_path=data_path)

    results = save_use_case.execute(request)

    # Handle errors (maintain existing behavior)
    failed_operations = [r for r in results if not r.success]
    if failed_operations:
        error_messages = [r.error_message for r in failed_operations if r.error_message]
        raise Exception(f"Save operation failed: {'; '.join(error_messages)}")


def _create_save_repository_use_case(
    github_service: RepositoryService, storage_service: StorageService
) -> Any:
    """Factory function to create configured SaveRepositoryUseCase."""
    from src.use_cases.save.collection.collect_labels import CollectLabelsUseCase
    from src.use_cases.save.collection.collect_issues import CollectIssuesUseCase
    from src.use_cases.save.collection.collect_comments import CollectCommentsUseCase
    from src.use_cases.save.collection.collect_pull_requests import (
        CollectPullRequestsUseCase,
    )
    from src.use_cases.save.collection.collect_pr_comments import (
        CollectPRCommentsUseCase,
    )
    from src.use_cases.save.collection.collect_sub_issues import CollectSubIssuesUseCase
    from src.use_cases.save.persistence.save_labels import SaveLabelsUseCase
    from src.use_cases.save.persistence.save_issues import SaveIssuesUseCase
    from src.use_cases.save.persistence.save_comments import SaveCommentsUseCase
    from src.use_cases.save.persistence.save_pull_requests import (
        SavePullRequestsUseCase,
    )
    from src.use_cases.save.persistence.save_pr_comments import SavePRCommentsUseCase
    from src.use_cases.save.persistence.save_sub_issues import SaveSubIssuesUseCase
    from src.use_cases.shared.processing.validate_repository_access import (
        ValidateRepositoryAccessUseCase,
    )
    from src.use_cases.save.processing.associate_sub_issues import (
        AssociateSubIssuesUseCase,
    )
    from src.use_cases.save.orchestration.save_repository import SaveRepositoryUseCase

    # Create all use case instances with proper dependency injection
    validate_access = ValidateRepositoryAccessUseCase(github_service)
    collect_labels = CollectLabelsUseCase(github_service)
    collect_issues = CollectIssuesUseCase(github_service)
    collect_comments = CollectCommentsUseCase(github_service)
    collect_pull_requests = CollectPullRequestsUseCase(github_service)
    collect_pr_comments = CollectPRCommentsUseCase(github_service)
    collect_sub_issues = CollectSubIssuesUseCase(github_service)
    associate_sub_issues = AssociateSubIssuesUseCase()
    save_labels = SaveLabelsUseCase(storage_service)
    save_issues = SaveIssuesUseCase(storage_service)
    save_comments = SaveCommentsUseCase(storage_service)
    save_pull_requests = SavePullRequestsUseCase(storage_service)
    save_pr_comments = SavePRCommentsUseCase(storage_service)
    save_sub_issues = SaveSubIssuesUseCase(storage_service)

    # Return configured orchestrator
    return SaveRepositoryUseCase(
        validate_access=validate_access,
        collect_labels=collect_labels,
        collect_issues=collect_issues,
        collect_comments=collect_comments,
        collect_pull_requests=collect_pull_requests,
        collect_pr_comments=collect_pr_comments,
        collect_sub_issues=collect_sub_issues,
        associate_sub_issues=associate_sub_issues,
        save_labels=save_labels,
        save_issues=save_issues,
        save_comments=save_comments,
        save_pull_requests=save_pull_requests,
        save_pr_comments=save_pr_comments,
        save_sub_issues=save_sub_issues,
    )


def _collect_repository_data(
    github_service: RepositoryService, repo_name: str
) -> RepositoryData:
    """Collect all repository data from GitHub API."""
    labels = _fetch_repository_labels(github_service, repo_name)
    issues = _fetch_repository_issues(github_service, repo_name)
    comments = _fetch_all_issue_comments(github_service, repo_name)
    pull_requests = _fetch_repository_pull_requests(github_service, repo_name)
    pr_comments = _fetch_all_pr_comments(github_service, repo_name)
    sub_issues = _fetch_repository_sub_issues(github_service, repo_name)

    return _create_repository_data(
        repo_name, labels, issues, comments, pull_requests, pr_comments, sub_issues
    )


def _create_repository_data(
    repo_name: str,
    labels: List[Label],
    issues: List[Issue],
    comments: List[Comment],
    pull_requests: List[PullRequest],
    pr_comments: List[PullRequestComment],
    sub_issues: List[SubIssue],
) -> RepositoryData:
    """Create RepositoryData instance with current timestamp."""
    from datetime import datetime

    # Associate sub-issues with their parent issues
    issues_with_sub_issues = _associate_sub_issues_with_parents(issues, sub_issues)

    return RepositoryData(
        repository_name=repo_name,
        exported_at=datetime.now(),
        labels=labels,
        issues=issues_with_sub_issues,
        comments=comments,
        pull_requests=pull_requests,
        pr_comments=pr_comments,
        sub_issues=sub_issues,
    )


def _save_data_to_files(
    repository_data: RepositoryData, output_dir: Path, storage_service: StorageService
) -> None:
    """Save repository data to separate JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    _save_labels_to_file(repository_data.labels, output_dir, storage_service)
    _save_issues_to_file(repository_data.issues, output_dir, storage_service)
    _save_comments_to_file(repository_data.comments, output_dir, storage_service)
    _save_pull_requests_to_file(
        repository_data.pull_requests, output_dir, storage_service
    )
    _save_pr_comments_to_file(repository_data.pr_comments, output_dir, storage_service)
    _save_sub_issues_to_file(repository_data.sub_issues, output_dir, storage_service)


def _fetch_repository_labels(
    github_service: RepositoryService, repo_name: str
) -> List[Label]:
    """Fetch all labels from the repository."""
    raw_labels = github_service.get_repository_labels(repo_name)
    return [converters.convert_to_label(label_dict) for label_dict in raw_labels]


def _fetch_repository_issues(
    github_service: RepositoryService, repo_name: str
) -> List[Issue]:
    """Fetch all issues from the repository."""
    raw_issues = github_service.get_repository_issues(repo_name)
    return [converters.convert_to_issue(issue_dict) for issue_dict in raw_issues]


def _fetch_all_issue_comments(
    github_service: RepositoryService, repo_name: str
) -> List[Comment]:
    """Fetch all comments from all issues in the repository."""
    raw_comments = github_service.get_all_issue_comments(repo_name)
    return [
        converters.convert_to_comment(comment_dict) for comment_dict in raw_comments
    ]


def _fetch_repository_pull_requests(
    github_service: RepositoryService, repo_name: str
) -> List[PullRequest]:
    """Fetch all pull requests from the repository."""
    raw_prs = github_service.get_repository_pull_requests(repo_name)
    return [converters.convert_to_pull_request(pr_dict) for pr_dict in raw_prs]


def _fetch_all_pr_comments(
    github_service: RepositoryService, repo_name: str
) -> List[PullRequestComment]:
    """Fetch all comments from all pull requests in the repository."""
    raw_comments = github_service.get_all_pull_request_comments(repo_name)
    return [
        converters.convert_to_pr_comment(comment_dict) for comment_dict in raw_comments
    ]


def _fetch_repository_sub_issues(
    github_service: RepositoryService, repo_name: str
) -> List[SubIssue]:
    """Fetch all sub-issue relationships from the repository."""
    raw_sub_issues = github_service.get_repository_sub_issues(repo_name)
    return [
        converters.convert_to_sub_issue(sub_issue_dict)
        for sub_issue_dict in raw_sub_issues
    ]


def _associate_sub_issues_with_parents(
    issues: List[Issue], sub_issues: List[SubIssue]
) -> List[Issue]:
    """Associate sub-issues with their parent issues."""
    # Create a copy of issues to avoid modifying the original list
    issues_copy = [issue.model_copy() for issue in issues]

    # Create a mapping from issue number to issue index
    issue_number_to_index = {issue.number: i for i, issue in enumerate(issues_copy)}

    # Group sub-issues by parent issue number
    sub_issues_by_parent: Dict[int, List[SubIssue]] = {}
    for sub_issue in sub_issues:
        parent_number = sub_issue.parent_issue_number
        if parent_number not in sub_issues_by_parent:
            sub_issues_by_parent[parent_number] = []
        sub_issues_by_parent[parent_number].append(sub_issue)

    # Associate sub-issues with their parent issues
    for parent_number, child_sub_issues in sub_issues_by_parent.items():
        if parent_number in issue_number_to_index:
            parent_index = issue_number_to_index[parent_number]
            # Sort sub-issues by position
            sorted_sub_issues = sorted(child_sub_issues, key=lambda si: si.position)
            issues_copy[parent_index].sub_issues = sorted_sub_issues

    return issues_copy


def _save_labels_to_file(
    labels: List[Label], output_dir: Path, storage_service: StorageService
) -> None:
    """Save labels to labels.json file."""
    labels_file = output_dir / "labels.json"
    storage_service.save_data(labels, labels_file)


def _save_issues_to_file(
    issues: List[Issue], output_dir: Path, storage_service: StorageService
) -> None:
    """Save issues to issues.json file."""
    issues_file = output_dir / "issues.json"
    storage_service.save_data(issues, issues_file)


def _save_comments_to_file(
    comments: List[Comment], output_dir: Path, storage_service: StorageService
) -> None:
    """Save comments to comments.json file."""
    comments_file = output_dir / "comments.json"
    storage_service.save_data(comments, comments_file)


def _save_pull_requests_to_file(
    pull_requests: List[PullRequest], output_dir: Path, storage_service: StorageService
) -> None:
    """Save pull requests to pull_requests.json file."""
    prs_file = output_dir / "pull_requests.json"
    storage_service.save_data(pull_requests, prs_file)


def _save_pr_comments_to_file(
    pr_comments: List[PullRequestComment],
    output_dir: Path,
    storage_service: StorageService,
) -> None:
    """Save PR comments to pr_comments.json file."""
    pr_comments_file = output_dir / "pr_comments.json"
    storage_service.save_data(pr_comments, pr_comments_file)


def _save_sub_issues_to_file(
    sub_issues: List[SubIssue], output_dir: Path, storage_service: StorageService
) -> None:
    """Save sub-issues to sub_issues.json file."""
    sub_issues_file = output_dir / "sub_issues.json"
    storage_service.save_data(sub_issues, sub_issues_file)
