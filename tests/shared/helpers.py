"""Common test utilities and helper functions."""

import pytest
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from unittest.mock import Mock
from github_data.entities import (
    GitHubUser,
    Issue,
    Comment,
    Label,
    PullRequest,
    PullRequestComment,
)


class TestDataHelper:
    """Helper for creating standardized test data."""

    @staticmethod
    def create_test_user(
        login: str = "testuser",
        user_id: int = 123,
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> GitHubUser:
        """Create a standardized test user."""
        fields = {
            "login": login,
            "id": user_id,
            "avatar_url": f"https://github.com/{login}.png",
            "html_url": f"https://github.com/{login}",
        }
        if custom_fields:
            fields.update(custom_fields)

        return GitHubUser(**fields)

    @staticmethod
    def create_test_issue(
        issue_id: int = 1001,
        number: int = 1,
        title: str = "Test Issue",
        body: str = "Test issue body",
        state: str = "open",
        user: Optional[GitHubUser] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> Issue:
        """Create a standardized test issue."""
        if user is None:
            user = TestDataHelper.create_test_user()

        base_time = datetime(2023, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        fields = {
            "id": issue_id,
            "number": number,
            "title": title,
            "body": body,
            "state": state,
            "user": user,
            "created_at": base_time,
            "updated_at": base_time,
            "html_url": f"https://github.com/owner/repo/issues/{number}",
            "comments_count": 0,
        }
        if custom_fields:
            fields.update(custom_fields)

        return Issue(**fields)

    @staticmethod
    def create_test_comment(
        comment_id: int = 4001,
        body: str = "Test comment body",
        user: Optional[GitHubUser] = None,
        issue_number: int = 1,
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> Comment:
        """Create a standardized test comment."""
        if user is None:
            user = TestDataHelper.create_test_user()

        base_time = datetime(2023, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        fields = {
            "id": comment_id,
            "body": body,
            "user": user,
            "created_at": base_time,
            "updated_at": base_time,
            "html_url": (
                f"https://github.com/owner/repo/issues/"
                f"{issue_number}#issuecomment-{comment_id}"
            ),
            "issue_url": (
                f"https://api.github.com/repos/owner/repo/issues/{issue_number}"
            ),
        }
        if custom_fields:
            fields.update(custom_fields)

        return Comment(**fields)

    @staticmethod
    def create_test_label(
        name: str = "test-label",
        color: str = "ff0000",
        description: str = "Test label description",
        url: str = "https://api.github.com/repos/owner/repo/labels/test-label",
        label_id: int = 1000,
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> Label:
        """Create a standardized test label."""
        fields = {
            "name": name,
            "color": color,
            "description": description,
            "url": url,
            "id": label_id,
        }
        if custom_fields:
            fields.update(custom_fields)

        return Label(**fields)

    @staticmethod
    def create_test_pull_request(
        pr_id: int = 2001,
        number: int = 100,
        title: str = "Test Pull Request",
        body: str = "Test PR body",
        state: str = "OPEN",
        user: Optional[GitHubUser] = None,
        base_ref: str = "main",
        head_ref: str = "feature/test",
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> PullRequest:
        """Create a standardized test pull request."""
        if user is None:
            user = TestDataHelper.create_test_user()

        base_time = datetime(2023, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        fields = {
            "id": pr_id,
            "number": number,
            "title": title,
            "body": body,
            "state": state,
            "user": user,
            "created_at": base_time,
            "updated_at": base_time,
            "base_ref": base_ref,
            "head_ref": head_ref,
            "html_url": f"https://github.com/owner/repo/pull/{number}",
            "comments_count": 0,
        }
        if custom_fields:
            fields.update(custom_fields)

        return PullRequest(**fields)

    @staticmethod
    def create_test_pr_comment(
        comment_id: int = 5001,
        body: str = "Test PR comment body",
        user: Optional[GitHubUser] = None,
        pull_request_number: int = 100,
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> PullRequestComment:
        """Create a standardized test PR comment."""
        if user is None:
            user = TestDataHelper.create_test_user()

        base_time = datetime(2023, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        fields = {
            "id": comment_id,
            "body": body,
            "user": user,
            "created_at": base_time,
            "updated_at": base_time,
            "html_url": (
                f"https://github.com/owner/repo/pull/"
                f"{pull_request_number}#issuecomment-{comment_id}"
            ),
            "pull_request_url": (
                f"https://api.github.com/repos/owner/repo/pulls/{pull_request_number}"
            ),
        }
        if custom_fields:
            fields.update(custom_fields)

        return PullRequestComment(**fields)


class MockHelper:
    """Helper for creating standardized mocks."""

    @staticmethod
    def create_github_client_mock() -> Mock:
        """Create a mock GitHub client with common methods."""
        mock_client = Mock()

        # Set up common mock methods
        mock_client.get_repository_labels.return_value = []
        mock_client.get_repository_issues.return_value = []
        mock_client.get_all_issue_comments.return_value = []
        mock_client.get_repository_pull_requests.return_value = []
        mock_client.get_all_pull_request_comments.return_value = []
        mock_client.get_repository_sub_issues.return_value = []

        # Mock API responses
        mock_client.create_label.return_value = {"name": "test-label"}
        mock_client.create_issue.return_value = {"number": 1, "title": "Test Issue"}
        mock_client.create_issue_comment.return_value = {"id": 4001}

        return mock_client

    @staticmethod
    def create_storage_service_mock() -> Mock:
        """Create a mock storage service with common methods."""
        mock_storage = Mock()

        # Set up common mock methods (using actual interface)
        mock_storage.write.return_value = None
        mock_storage.read.return_value = []

        return mock_storage


class TestMarkerHelper:
    """Helper for working with test markers."""

    @staticmethod
    def has_marker(request, marker_name: str) -> bool:
        """Check if a test has a specific marker."""
        return request.node.get_closest_marker(marker_name) is not None

    @staticmethod
    def get_marker_value(request, marker_name: str, default=None):
        """Get the value of a test marker."""
        marker = request.node.get_closest_marker(marker_name)
        if marker is None:
            return default
        return marker.args[0] if marker.args else default

    @staticmethod
    def requires_marker(marker_name: str):
        """Decorator to skip test if marker is not present."""

        def decorator(func):
            return pytest.mark.skipif(
                not hasattr(pytest.mark, marker_name),
                reason=f"Test requires {marker_name} marker",
            )(func)

        return decorator


class AssertionHelper:
    """Helper for common test assertions."""

    @staticmethod
    def assert_valid_github_user(user: GitHubUser) -> None:
        """Assert that a GitHubUser object is valid."""
        assert user.login is not None
        assert user.id is not None
        assert user.avatar_url is not None
        assert user.html_url is not None
        assert user.login in user.avatar_url
        assert user.login in user.html_url

    @staticmethod
    def assert_valid_issue(issue: Issue) -> None:
        """Assert that an Issue object is valid."""
        assert issue.id is not None
        assert issue.number is not None
        assert issue.title is not None
        assert issue.state in ["open", "closed"]
        assert issue.user is not None
        assert issue.created_at is not None
        assert issue.updated_at is not None
        assert issue.html_url is not None
        AssertionHelper.assert_valid_github_user(issue.user)

    @staticmethod
    def assert_valid_comment(comment: Comment) -> None:
        """Assert that a Comment object is valid."""
        assert comment.id is not None
        assert comment.body is not None
        assert comment.user is not None
        assert comment.created_at is not None
        assert comment.updated_at is not None
        assert comment.html_url is not None
        assert comment.issue_url is not None
        AssertionHelper.assert_valid_github_user(comment.user)

    @staticmethod
    def assert_valid_label(label: Label) -> None:
        """Assert that a Label object is valid."""
        assert label.name is not None
        assert label.color is not None
        # Color should be a valid hex color (6 digits)
        assert len(label.color) == 6
        assert all(c in "0123456789abcdefABCDEF" for c in label.color)

    @staticmethod
    def assert_mock_called_with_repo(mock_method, expected_repo: str) -> None:
        """Assert that a mock method was called with the expected repository."""
        mock_method.assert_called_once()
        call_args = mock_method.call_args[0]
        assert len(call_args) >= 1
        assert call_args[0] == expected_repo


class FixtureHelper:
    """Helper for working with fixtures in tests."""

    @staticmethod
    def create_minimal_test_data() -> Dict[str, List[Dict[str, Any]]]:
        """Create minimal test data structure."""
        return {
            "labels": [],
            "issues": [],
            "comments": [],
            "pull_requests": [],
            "sub_issues": [],
        }

    @staticmethod
    def create_sample_test_data() -> Dict[str, List[Dict[str, Any]]]:
        """Create sample test data with basic items."""
        user_data = {
            "login": "testuser",
            "id": 123,
            "avatar_url": "https://github.com/testuser.png",
            "html_url": "https://github.com/testuser",
        }

        return {
            "labels": [
                {
                    "name": "bug",
                    "color": "ff0000",
                    "description": "Bug label",
                    "url": "https://api.github.com/repos/owner/repo/labels/bug",
                    "id": 1000,
                },
                {
                    "name": "feature",
                    "color": "00ff00",
                    "description": "Feature label",
                    "url": "https://api.github.com/repos/owner/repo/labels/feature",
                    "id": 1001,
                },
            ],
            "issues": [
                {
                    "id": 1001,
                    "number": 1,
                    "title": "Test Issue 1",
                    "body": "Test issue body 1",
                    "state": "open",
                    "user": user_data,
                    "assignees": [],
                    "labels": [],
                    "created_at": "2023-01-15T10:30:00Z",
                    "updated_at": "2023-01-15T10:30:00Z",
                    "html_url": "https://github.com/owner/repo/issues/1",
                    "comments": 0,
                }
            ],
            "comments": [
                {
                    "id": 4001,
                    "body": "Test comment 1",
                    "user": user_data,
                    "created_at": "2023-01-15T12:00:00Z",
                    "updated_at": "2023-01-15T12:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/1#issuecomment-4001"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                }
            ],
            "pull_requests": [],
            "sub_issues": [],
        }
