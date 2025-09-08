"""
GitHub API client wrapper.

Provides a clean interface to GitHub API operations, abstracting away
the complexity of PyGithub and providing type-safe data access.
"""

from typing import List, Any
from github import Github
from github.Repository import Repository
from github.Issue import Issue as PyGithubIssue
from github.Label import Label as PyGithubLabel
from github.IssueComment import IssueComment as PyGithubComment
from github.PaginatedList import PaginatedList

from .models import Issue, Label, Comment, GitHubUser


class GitHubClient:
    """GitHub API client for repository data operations."""

    def __init__(self, token: str):
        """Initialize GitHub client with authentication token."""
        self._github = Github(token)

    def get_repository_labels(self, repo_name: str) -> List[Label]:
        """Get all labels from the specified repository."""
        repo = self._get_repository(repo_name)
        labels = self._fetch_all_labels(repo)
        return self._convert_labels_to_models(labels)

    def get_repository_issues(self, repo_name: str) -> List[Issue]:
        """Get all issues from the specified repository."""
        repo = self._get_repository(repo_name)
        issues = self._fetch_all_issues(repo)
        return self._convert_issues_to_models(issues)

    def get_issue_comments(self, repo_name: str, issue_number: int) -> List[Comment]:
        """Get all comments for a specific issue."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)
        comments = self._fetch_issue_comments(issue)
        return self._convert_comments_to_models(comments)

    def get_all_issue_comments(self, repo_name: str) -> List[Comment]:
        """Get all comments from all issues in the repository."""
        repo = self._get_repository(repo_name)
        all_comments = []

        for issue in self._fetch_all_issues(repo):
            if issue.comments > 0:
                comments = self._fetch_issue_comments(issue)
                issue_comments = self._convert_comments_to_models(comments)
                all_comments.extend(issue_comments)

        return all_comments

    def create_label(self, repo_name: str, label: Label) -> Label:
        """Create a new label in the repository."""
        repo = self._get_repository(repo_name)
        created_label = repo.create_label(
            name=label.name, color=label.color, description=label.description or ""
        )
        return self._convert_label_to_model(created_label)

    def create_issue(self, repo_name: str, issue: Issue) -> Issue:
        """Create a new issue in the repository."""
        repo = self._get_repository(repo_name)

        # Extract label names for issue creation
        label_names = [label.name for label in issue.labels]

        created_issue = repo.create_issue(
            title=issue.title,
            body=issue.body or "",
            labels=label_names,
        )
        return self._convert_issue_to_model(created_issue)

    def _get_repository(self, repo_name: str) -> Repository:
        """Get repository object from GitHub API."""
        return self._github.get_repo(repo_name)

    def _fetch_all_labels(self, repo: Repository) -> PaginatedList[PyGithubLabel]:
        """Fetch all labels from a repository."""
        return repo.get_labels()

    def _fetch_all_issues(self, repo: Repository) -> PaginatedList[PyGithubIssue]:
        """Fetch all issues from a repository."""
        return repo.get_issues(state="all")

    def _fetch_issue_comments(
        self, issue: PyGithubIssue
    ) -> PaginatedList[PyGithubComment]:
        """Fetch all comments from a specific issue."""
        return issue.get_comments()

    def _convert_labels_to_models(
        self, labels: PaginatedList[PyGithubLabel]
    ) -> List[Label]:
        """Convert PyGithub label objects to our data models."""
        return [self._convert_label_to_model(label) for label in labels]

    def _convert_label_to_model(self, label: PyGithubLabel) -> Label:
        """Convert a single PyGithub label to our data model."""
        return Label(
            name=label.name,
            color=label.color,
            description=label.description,
            url=label.url,
            id=label.id,
        )

    def _convert_issues_to_models(
        self, issues: PaginatedList[PyGithubIssue]
    ) -> List[Issue]:
        """Convert PyGithub issue objects to our data models."""
        return [self._convert_issue_to_model(issue) for issue in issues]

    def _convert_issue_to_model(self, issue: PyGithubIssue) -> Issue:
        """Convert a single PyGithub issue to our data model."""
        return Issue(
            id=issue.id,
            number=issue.number,
            title=issue.title,
            body=issue.body,
            state=issue.state,
            user=self._convert_user_to_model(issue.user),
            assignees=[
                self._convert_user_to_model(assignee) for assignee in issue.assignees
            ],
            labels=[self._convert_label_to_model(label) for label in issue.labels],
            created_at=issue.created_at,
            updated_at=issue.updated_at,
            closed_at=issue.closed_at,
            html_url=issue.html_url,
            comments=issue.comments,
        )

    def _convert_comments_to_models(
        self, comments: PaginatedList[PyGithubComment]
    ) -> List[Comment]:
        """Convert PyGithub comment objects to our data models."""
        return [self._convert_comment_to_model(comment) for comment in comments]

    def _convert_comment_to_model(self, comment: PyGithubComment) -> Comment:
        """Convert a single PyGithub comment to our data model."""
        return Comment(
            id=comment.id,
            body=comment.body,
            user=self._convert_user_to_model(comment.user),
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            html_url=comment.html_url,
            issue_url=comment.issue_url,
        )

    def _convert_user_to_model(self, user: Any) -> GitHubUser:
        """Convert PyGithub user object to our data model."""
        return GitHubUser(
            login=user.login,
            id=user.id,
            avatar_url=user.avatar_url,
            html_url=user.html_url,
        )
