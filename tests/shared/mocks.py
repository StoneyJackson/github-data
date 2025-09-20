"""Mock utilities for GitHub Data tests."""

from unittest.mock import Mock


def add_pr_method_mocks(mock_boundary, sample_data=None):
    """Add PR method mocks to boundary for compatibility with new PR support."""
    if sample_data:
        mock_boundary.get_repository_pull_requests.return_value = sample_data.get(
            "pull_requests", []
        )
        mock_boundary.get_all_pull_request_comments.return_value = sample_data.get(
            "pr_comments", []
        )
    else:
        mock_boundary.get_repository_pull_requests.return_value = []
        mock_boundary.get_all_pull_request_comments.return_value = []


def add_sub_issues_method_mocks(mock_boundary):
    """Add sub-issues method mocks to boundary for compatibility."""
    mock_boundary.get_repository_sub_issues.return_value = []


class MockBoundaryFactory:
    """Factory for creating configured mock boundaries."""

    @staticmethod
    def create_with_data(data_type="full", **kwargs):
        """Create configured mock boundary with test data.

        Args:
            data_type: Type of data configuration ("full", "empty", "labels_only", etc.)
            **kwargs: Additional configuration options
        """
        mock_boundary = Mock()

        if data_type == "empty":
            mock_boundary.get_repository_labels.return_value = []
            mock_boundary.get_repository_issues.return_value = []
            mock_boundary.get_all_issue_comments.return_value = []
            add_pr_method_mocks(mock_boundary)
            add_sub_issues_method_mocks(mock_boundary)
        elif data_type == "labels_only":
            sample_data = kwargs.get("sample_data", {})
            mock_boundary.get_repository_labels.return_value = sample_data.get(
                "labels", []
            )
            mock_boundary.get_repository_issues.return_value = []
            mock_boundary.get_all_issue_comments.return_value = []
            add_pr_method_mocks(mock_boundary)
            add_sub_issues_method_mocks(mock_boundary)
        elif data_type == "full":
            sample_data = kwargs.get("sample_data", {})
            mock_boundary.get_repository_labels.return_value = sample_data.get(
                "labels", []
            )
            mock_boundary.get_repository_issues.return_value = sample_data.get(
                "issues", []
            )
            mock_boundary.get_all_issue_comments.return_value = sample_data.get(
                "comments", []
            )
            add_pr_method_mocks(mock_boundary, sample_data)
            add_sub_issues_method_mocks(mock_boundary)

        return mock_boundary

    @staticmethod
    def add_pr_support(mock_boundary, data=None):
        """Add PR method mocks to existing boundary."""
        add_pr_method_mocks(mock_boundary, data)

    @staticmethod
    def add_sub_issues_support(mock_boundary):
        """Add sub-issues mocks to existing boundary."""
        add_sub_issues_method_mocks(mock_boundary)

    @staticmethod
    def create_for_restore(success_responses=True):
        """Create mock boundary configured for restore operations.

        Args:
            success_responses: If True, configure successful API responses
        """
        mock_boundary = Mock()

        # Mock get_repository_labels for conflict detection (default: empty repository)
        mock_boundary.get_repository_labels.return_value = []

        if success_responses:
            # Configure successful creation responses
            mock_boundary.create_label.return_value = {
                "id": 999,
                "name": "test",
                "color": "ffffff",
                "description": "test",
                "url": "https://api.github.com/repos/owner/repo/labels/test",
            }

            mock_boundary.create_issue.return_value = {
                "number": 999,
                "title": "test",
                "id": 999,
                "body": "test",
                "state": "open",
                "user": {
                    "login": "testuser",
                    "id": 1,
                    "avatar_url": "https://github.com/images/error/testuser_happy.gif",
                    "url": "https://api.github.com/users/testuser",
                    "html_url": "https://github.com/testuser",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/999",
                "comments": 0,
            }

            mock_boundary.create_issue_comment.return_value = {
                "id": 888,
                "body": "test comment",
                "user": {
                    "login": "testuser",
                    "id": 1,
                    "avatar_url": "https://github.com/images/error/testuser_happy.gif",
                    "url": "https://api.github.com/users/testuser",
                    "html_url": "https://github.com/testuser",
                },
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/999#issuecomment-888",
                "issue_url": "https://api.github.com/repos/owner/repo/issues/999",
            }

            mock_boundary.create_pull_request.return_value = {
                "id": 777,
                "number": 777,
                "title": "test PR",
                "body": "test PR body",
                "state": "open",
                "user": {
                    "login": "testuser",
                    "id": 1,
                    "avatar_url": "https://github.com/images/error/testuser_happy.gif",
                    "url": "https://api.github.com/users/testuser",
                    "html_url": "https://github.com/testuser",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "closed_at": None,
                "merged_at": None,
                "merge_commit_sha": None,
                "base_ref": "main",
                "head_ref": "test-branch",
                "html_url": "https://github.com/owner/repo/pull/777",
                "comments": 0,
            }

            mock_boundary.create_pull_request_comment.return_value = {
                "id": 666,
                "body": "test PR comment",
                "user": {
                    "login": "testuser",
                    "id": 1,
                    "avatar_url": "https://github.com/images/error/testuser_happy.gif",
                    "url": "https://api.github.com/users/testuser",
                    "html_url": "https://github.com/testuser",
                },
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "html_url": "https://github.com/owner/repo/pull/777#issuecomment-666",
                "pull_request_url": "https://github.com/owner/repo/pull/777",
            }

        return mock_boundary
