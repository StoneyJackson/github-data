"""Mock boundary factory for GitHub Data tests."""

import inspect
from unittest.mock import Mock
from src.github.protocols import GitHubApiBoundary


def add_pr_method_mocks(mock_boundary, sample_data=None):
    """Add PR method mocks to boundary for compatibility with new PR support."""
    if sample_data:
        mock_boundary.get_repository_pull_requests.return_value = sample_data.get(
            "pull_requests", []
        )
        mock_boundary.get_all_pull_request_comments.return_value = sample_data.get(
            "pr_comments", []
        )
        mock_boundary.get_all_pull_request_reviews.return_value = sample_data.get(
            "pr_reviews", []
        )
        mock_boundary.get_all_pull_request_review_comments.return_value = (
            sample_data.get("pr_review_comments", [])
        )
    else:
        mock_boundary.get_repository_pull_requests.return_value = []
        mock_boundary.get_all_pull_request_comments.return_value = []
        mock_boundary.get_all_pull_request_reviews.return_value = []
        mock_boundary.get_all_pull_request_review_comments.return_value = []


def add_sub_issues_method_mocks(mock_boundary):
    """Add sub-issues method mocks to boundary for compatibility."""
    mock_boundary.get_repository_sub_issues.return_value = []


class MockBoundaryFactory:
    """Factory for creating configured mock boundaries."""

    @staticmethod
    def _get_protocol_methods():
        """Discover all methods from GitHubApiBoundary protocol."""
        methods = []
        # Get all methods defined in the protocol class
        for name in dir(GitHubApiBoundary):
            if not name.startswith("_"):  # Skip private methods
                attr = getattr(GitHubApiBoundary, name)
                if callable(attr):
                    methods.append(name)
        return methods

    @staticmethod
    def _configure_all_methods(mock_boundary, sample_data=None):
        """Configure all protocol methods with appropriate return values."""
        if sample_data is None:
            sample_data = {}

        # Read methods (get_*)
        mock_boundary.get_repository_labels.return_value = sample_data.get("labels", [])
        mock_boundary.get_repository_issues.return_value = sample_data.get("issues", [])
        mock_boundary.get_all_issue_comments.return_value = sample_data.get(
            "comments", []
        )
        mock_boundary.get_issue_comments.return_value = []
        mock_boundary.get_repository_pull_requests.return_value = sample_data.get(
            "pull_requests", []
        )
        mock_boundary.get_all_pull_request_comments.return_value = sample_data.get(
            "pr_comments", []
        )
        mock_boundary.get_pull_request_comments.return_value = []
        mock_boundary.get_all_pull_request_reviews.return_value = sample_data.get(
            "pr_reviews", []
        )
        mock_boundary.get_pull_request_reviews.return_value = []
        mock_boundary.get_all_pull_request_review_comments.return_value = (
            sample_data.get("pr_review_comments", [])
        )
        mock_boundary.get_pull_request_review_comments.return_value = []
        mock_boundary.get_repository_sub_issues.return_value = sample_data.get(
            "sub_issues", []
        )
        mock_boundary.get_issue_sub_issues_graphql.return_value = []
        mock_boundary.get_issue_parent.return_value = None
        mock_boundary.get_rate_limit_status.return_value = {
            "remaining": 5000,
            "reset": 3600,
        }

        # Create methods (create_*)
        mock_boundary.create_label.return_value = {
            "id": 999,
            "name": "test-label",
            "color": "ffffff",
        }
        mock_boundary.create_issue.return_value = {
            "number": 999,
            "id": 999,
            "title": "test-issue",
        }
        mock_boundary.create_issue_comment.return_value = {
            "id": 888,
            "body": "test-comment",
        }
        mock_boundary.create_pull_request.return_value = {
            "id": 777,
            "number": 777,
            "title": "test-pr",
        }
        mock_boundary.create_pull_request_comment.return_value = {
            "id": 666,
            "body": "test-pr-comment",
        }
        mock_boundary.create_pull_request_review.return_value = {
            "id": 555,
            "body": "test-review",
        }
        mock_boundary.create_pull_request_review_comment.return_value = {
            "id": 444,
            "body": "test-review-comment",
        }

        # Sub-issue management methods
        mock_boundary.add_sub_issue.return_value = {"success": True}
        mock_boundary.remove_sub_issue.return_value = None
        mock_boundary.reprioritize_sub_issue.return_value = {"success": True}

        # Update/delete methods
        mock_boundary.update_label.return_value = {
            "id": 999,
            "name": "updated-label",
            "color": "000000",
        }
        mock_boundary.delete_label.return_value = None
        mock_boundary.close_issue.return_value = {"number": 999, "state": "closed"}

    @staticmethod
    def create_with_data(data_type="full", **kwargs):
        """Create configured mock boundary with test data.

        Args:
            data_type: Type of data configuration ("full", "empty", "labels_only", etc.)
            **kwargs: Additional configuration options (sample_data, etc.)
        """
        mock_boundary = Mock()
        sample_data = kwargs.get("sample_data", {})

        if data_type == "empty":
            # Configure all methods but with empty data
            MockBoundaryFactory._configure_all_methods(mock_boundary, {})
        elif data_type == "labels_only":
            # Configure all methods but only labels have data
            labels_only_data = {"labels": sample_data.get("labels", [])}
            MockBoundaryFactory._configure_all_methods(mock_boundary, labels_only_data)
        elif data_type == "full":
            # Configure all methods with full sample data
            MockBoundaryFactory._configure_all_methods(mock_boundary, sample_data)

        return mock_boundary

    @staticmethod
    def validate_protocol_completeness(mock_boundary):
        """Validate that mock boundary implements all required protocol methods.

        Returns:
            tuple: (is_complete, missing_methods)
        """
        protocol_methods = MockBoundaryFactory._get_protocol_methods()
        missing_methods = []

        for method_name in protocol_methods:
            try:
                # Check if method exists and is configured (has return_value or side_effect)
                method = getattr(mock_boundary, method_name)
                if not (
                    hasattr(method, "return_value") or hasattr(method, "side_effect")
                ):
                    missing_methods.append(method_name)
            except AttributeError:
                missing_methods.append(method_name)

        return len(missing_methods) == 0, missing_methods

    @staticmethod
    def create_protocol_complete(sample_data=None):
        """Create a protocol-complete mock boundary with all methods configured.

        This is the recommended method for new tests as it ensures 100% protocol coverage.

        Args:
            sample_data: Optional sample data dict to configure return values
        """
        mock_boundary = Mock()
        MockBoundaryFactory._configure_all_methods(mock_boundary, sample_data or {})

        # Validate completeness
        is_complete, missing = MockBoundaryFactory.validate_protocol_completeness(
            mock_boundary
        )
        if not is_complete:
            raise ValueError(f"Mock boundary missing methods: {missing}")

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
        # Start with a protocol-complete mock
        mock_boundary = MockBoundaryFactory.create_protocol_complete()

        # Override specific methods for restore scenario
        mock_boundary.get_repository_labels.return_value = (
            []
        )  # Empty repository for conflict detection

        if success_responses:
            # Override creation methods with detailed success responses
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

        return mock_boundary
