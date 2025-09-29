"""Integration tests for issues and comments functionality."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.github import create_github_service
from src.storage import create_storage_service
from src.operations.restore.restore import restore_repository_data_with_strategy_pattern

from tests.shared.builders import GitHubDataBuilder

pytestmark = [pytest.mark.integration, pytest.mark.issues]


class TestIssuesIntegration:
    """Integration tests for issues and comments functionality."""

    @patch("src.github.service.GitHubApiBoundary")
    def test_comments_restored_in_chronological_order(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test comments restored in chronological order regardless of JSON order."""
        data_path = Path(temp_data_dir)

        # Create test data with comments in REVERSE chronological order in JSON
        # but they should be restored in correct chronological order
        labels_data = [
            {
                "name": "bug",
                "id": 1001,
                "color": "d73a4a",
                "description": "Something isn't working",
                "url": "https://api.github.com/repos/owner/repo/labels/bug",
            }
        ]

        issues_data = [
            {
                "number": 1,
                "title": "Test issue",
                "id": 2001,
                "body": "Test issue body",
                "state": "open",
                "user": {
                    "login": "testuser",
                    "id": 1,
                    "avatar_url": "https://github.com/testuser.png",
                    "html_url": "https://github.com/testuser",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-10T10:00:00Z",
                "updated_at": "2023-01-10T10:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/1",
                "comments": 3,
            }
        ]

        # Comments in REVERSE chronological order (latest first)
        comments_data = [
            {
                "id": 4003,
                "body": "Third comment (latest)",
                "user": {
                    "login": "user3",
                    "id": 3003,
                    "avatar_url": "https://github.com/user3.png",
                    "html_url": "https://github.com/user3",
                },
                "created_at": "2023-01-10T14:00:00Z",  # Latest timestamp
                "updated_at": "2023-01-10T14:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/1#issuecomment-4003",
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
            },
            {
                "id": 4002,
                "body": "Second comment (middle)",
                "user": {
                    "login": "user2",
                    "id": 3002,
                    "avatar_url": "https://github.com/user2.png",
                    "html_url": "https://github.com/user2",
                },
                "created_at": "2023-01-10T12:00:00Z",  # Middle timestamp
                "updated_at": "2023-01-10T12:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/1#issuecomment-4002",
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
            },
            {
                "id": 4001,
                "body": "First comment (earliest)",
                "user": {
                    "login": "user1",
                    "id": 3001,
                    "avatar_url": "https://github.com/user1.png",
                    "html_url": "https://github.com/user1",
                },
                "created_at": "2023-01-10T10:30:00Z",  # Earliest timestamp
                "updated_at": "2023-01-10T10:30:00Z",
                "html_url": "https://github.com/owner/repo/issues/1#issuecomment-4001",
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
            },
        ]

        # Write test data to JSON files
        with open(data_path / "labels.json", "w") as f:
            json.dump(labels_data, f)
        with open(data_path / "issues.json", "w") as f:
            json.dump(issues_data, f)
        with open(data_path / "comments.json", "w") as f:
            json.dump(comments_data, f)  # Comments in reverse chronological order
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []

        mock_boundary.create_label.return_value = {
            "name": "bug",
            "id": 5001,
            "color": "d73a4a",
            "description": "Something isn't working",
            "url": "https://api.github.com/repos/owner/target_repo/labels/bug",
        }

        mock_boundary.create_issue.return_value = {
            "number": 10,
            "title": "Test issue",
            "id": 6001,
            "body": "Test issue body",
            "state": "open",
            "user": {
                "login": "testuser",
                "id": 1,
                "avatar_url": "https://github.com/testuser.png",
                "html_url": "https://github.com/testuser",
            },
            "assignees": [],
            "labels": [],
            "created_at": "2023-01-10T10:00:00Z",
            "updated_at": "2023-01-10T10:00:00Z",
            "closed_at": None,
            "html_url": "https://github.com/owner/target_repo/issues/10",
            "comments": 0,
        }

        mock_boundary.create_issue_comment.return_value = {
            "id": 7001,
            "body": "test comment",
            "user": {
                "login": "testuser",
                "id": 1,
                "avatar_url": "https://github.com/testuser.png",
                "html_url": "https://github.com/testuser",
            },
            "created_at": "2023-01-10T10:30:00Z",
            "updated_at": "2023-01-10T10:30:00Z",
            "html_url": (
                "https://github.com/owner/target_repo/issues/10#issuecomment-7001"
            ),
            "issue_url": "https://api.github.com/repos/owner/target_repo/issues/10",
        }

        # Execute restore
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/target_repo",
            temp_data_dir,
            include_original_metadata=False,
            include_pull_requests=True,
        )

        # Verify comments were called in chronological order (earliest first)
        comment_calls = mock_boundary.create_issue_comment.call_args_list
        assert len(comment_calls) == 3

        # First call should be the earliest comment (2023-01-10T10:30:00Z)
        first_call = comment_calls[0][
            0
        ]  # positional arguments: (repo_name, issue_number, body)
        assert (
            first_call[2] == "First comment (earliest)"
        )  # body is third positional arg

        # Second call should be the middle comment (2023-01-10T12:00:00Z)
        second_call = comment_calls[1][
            0
        ]  # positional arguments: (repo_name, issue_number, body)
        assert (
            second_call[2] == "Second comment (middle)"
        )  # body is third positional arg

        # Third call should be the latest comment (2023-01-10T14:00:00Z)
        third_call = comment_calls[2][
            0
        ]  # positional arguments: (repo_name, issue_number, body)
        assert third_call[2] == "Third comment (latest)"  # body is third positional arg

    @patch("src.github.service.GitHubApiBoundary")
    def test_closed_issue_restoration_with_metadata(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test closed issues are restored with their state and metadata."""
        from src.entities import Issue, GitHubUser
        from datetime import datetime

        # Setup boundary mock
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []

        # Mock raw GitHub API responses for boundary
        created_issue_raw = {
            "id": 2001,
            "number": 101,
            "title": "Closed issue with all metadata",
            "body": (
                "This issue was completed successfully\n\n---\n"
                "*Originally created by @reporter on 2023-01-01 10:00:00 UTC*\n"
                "*Last updated on 2023-01-02 15:30:00 UTC*\n"
                "*Closed on 2023-01-02 15:30:00 UTC by @admin-user as completed*"
            ),
            "state": "open",
            "user": {
                "login": "test-bot",
                "id": 9001,
                "avatar_url": "https://github.com/test-bot.png",
                "html_url": "https://github.com/test-bot",
            },
            "assignees": [],
            "labels": [],
            "created_at": "2023-01-03T10:00:00Z",
            "updated_at": "2023-01-03T10:00:00Z",
            "closed_at": None,
            "html_url": "https://github.com/owner/repo/issues/101",
            "comments": 0,
        }

        closed_issue_raw = {
            "id": 2001,
            "number": 101,
            "title": "Closed issue with all metadata",
            "body": (
                "This issue was completed successfully\n\n---\n"
                "*Originally created by @reporter on 2023-01-01 10:00:00 UTC*\n"
                "*Last updated on 2023-01-02 15:30:00 UTC*\n"
                "*Closed on 2023-01-02 15:30:00 UTC by @admin-user as completed*"
            ),
            "state": "closed",
            "user": {
                "login": "test-bot",
                "id": 9001,
                "avatar_url": "https://github.com/test-bot.png",
                "html_url": "https://github.com/test-bot",
            },
            "assignees": [],
            "labels": [],
            "created_at": "2023-01-03T10:00:00Z",
            "updated_at": "2023-01-03T10:00:00Z",
            "closed_at": "2023-01-03T10:05:00Z",
            "html_url": "https://github.com/owner/repo/issues/101",
            "comments": 0,
        }

        mock_boundary.create_issue.return_value = created_issue_raw
        mock_boundary.close_issue.return_value = closed_issue_raw

        # Create test data with closed issue containing all closure metadata
        closed_issue = Issue(
            id=1001,
            number=1,
            title="Closed issue with all metadata",
            body="This issue was completed successfully",
            state="closed",
            user=GitHubUser(
                login="reporter",
                id=4001,
                avatar_url="https://github.com/reporter.png",
                html_url="https://github.com/reporter",
            ),
            assignees=[],
            labels=[],
            created_at=datetime(2023, 1, 1, 10, 0, 0),
            updated_at=datetime(2023, 1, 2, 15, 30, 0),
            closed_at=datetime(2023, 1, 2, 15, 30, 0),
            closed_by=GitHubUser(
                login="admin-user",
                id=5001,
                avatar_url="https://github.com/admin-user.png",
                html_url="https://github.com/admin-user",
            ),
            state_reason="completed",
            html_url="https://github.com/owner/repo/issues/1",
            comments_count=0,
        )

        # Create test data files
        data_path = Path(temp_data_dir) / "test_data"
        data_path.mkdir()

        with open(data_path / "labels.json", "w") as f:
            json.dump([], f)

        with open(data_path / "issues.json", "w") as f:
            json.dump([closed_issue.model_dump(mode="json")], f, default=str)

        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)

        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)

        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)

        # Test restoration
        github_service = create_github_service("fake-token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            str(data_path),
            include_original_metadata=True,
            include_pull_requests=True,
        )

        # Verify boundary methods were called
        mock_boundary.create_issue.assert_called_once()
        create_call_args = mock_boundary.create_issue.call_args

        # Check that metadata footer was added to body
        created_body = create_call_args[0][
            2
        ]  # positional arguments: (repo_name, title, body, labels) - body is 3rd
        assert (
            "Originally created by @reporter on 2023-01-01 10:00:00 UTC" in created_body
        )
        assert (
            "Closed on 2023-01-02 15:30:00 UTC by @admin-user as completed"
            in created_body
        )

        # Verify issue was closed with correct state reason
        mock_boundary.close_issue.assert_called_once_with(
            "owner/repo",
            101,
            "completed",  # positional args: (repo_name, issue_number, state_reason)
        )

    @patch("src.github.service.GitHubApiBoundary")
    def test_closed_issue_restoration_minimal_metadata(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test closed issue restoration with minimal closure metadata."""
        from src.entities import Issue, GitHubUser
        from datetime import datetime

        # Setup boundary mock
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []

        # Mock raw GitHub API response
        created_issue_raw = {
            "id": 2002,
            "number": 102,
            "title": "Closed issue minimal metadata",
            "body": (
                "Basic closed issue\n\n---\n"
                "*Originally created by @test-user on 2023-01-01 10:00:00 UTC*\n"
                "*Closed on 2023-01-01 16:00:00 UTC*"
            ),
            "state": "open",
            "user": {
                "login": "test-user",
                "id": 4001,
                "avatar_url": "https://github.com/test-user.png",
                "html_url": "https://github.com/test-user",
            },
            "assignees": [],
            "labels": [],
            "created_at": "2023-01-03T10:00:00Z",
            "updated_at": "2023-01-03T10:00:00Z",
            "closed_at": None,
            "html_url": "https://github.com/owner/repo/issues/102",
            "comments": 0,
        }

        mock_boundary.create_issue.return_value = created_issue_raw
        mock_boundary.close_issue.return_value = created_issue_raw

        # Closed issue with minimal metadata (no closed_by or state_reason)
        closed_issue = Issue(
            id=1002,
            number=2,
            title="Closed issue minimal metadata",
            body="Basic closed issue",
            state="closed",
            user=GitHubUser(
                login="test-user",
                id=4001,
                avatar_url="https://github.com/test-user.png",
                html_url="https://github.com/test-user",
            ),
            assignees=[],
            labels=[],
            created_at=datetime(2023, 1, 1, 10, 0, 0),
            updated_at=datetime(2023, 1, 1, 10, 0, 0),
            closed_at=datetime(2023, 1, 1, 16, 0, 0),
            closed_by=None,  # No closer info
            state_reason=None,  # No reason
            html_url="https://github.com/owner/repo/issues/2",
            comments_count=0,
        )

        # Create test data files
        data_path = Path(temp_data_dir) / "test_data_minimal"
        data_path.mkdir()

        with open(data_path / "labels.json", "w") as f:
            json.dump([], f)

        with open(data_path / "issues.json", "w") as f:
            json.dump([closed_issue.model_dump(mode="json")], f, default=str)

        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)

        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)

        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)

        # Test restoration
        github_service = create_github_service("fake-token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            str(data_path),
            include_original_metadata=True,
            include_pull_requests=True,
        )

        # Verify boundary methods were called
        mock_boundary.create_issue.assert_called_once()
        create_call_args = mock_boundary.create_issue.call_args

        # Check metadata footer - should have closed date but no closer or reason
        created_body = create_call_args[0][
            2
        ]  # positional arguments: (repo_name, title, body, labels) - body is 3rd
        assert "Closed on 2023-01-01 16:00:00 UTC*" in created_body
        # Check that there's no "closed by" info (only "created by" should be present)
        assert "Closed on 2023-01-01 16:00:00 UTC by @" not in created_body
        assert " as " not in created_body  # No reason

        # Verify issue was closed without state reason (None passed)
        mock_boundary.close_issue.assert_called_once_with(
            "owner/repo",
            102,
            None,  # positional args: (repo_name, issue_number, state_reason)
        )

    @patch("src.github.service.GitHubApiBoundary")
    def test_issues_with_multiple_assignees_and_labels(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test issues with multiple assignees and labels are handled correctly."""
        # Create test data with complex issue relationships
        builder = GitHubDataBuilder()

        # Add custom issue with multiple assignees and labels
        custom_issue = {
            "id": 2001,
            "number": 1,
            "title": "Complex issue with multiple relationships",
            "body": "This issue has multiple assignees and labels",
            "state": "open",
            "user": {
                "login": "issue-creator",
                "id": 3001,
                "avatar_url": "https://github.com/issue-creator.png",
                "html_url": "https://github.com/issue-creator",
            },
            "assignees": [
                {
                    "login": "assignee1",
                    "id": 3002,
                    "avatar_url": "https://github.com/assignee1.png",
                    "html_url": "https://github.com/assignee1",
                },
                {
                    "login": "assignee2",
                    "id": 3003,
                    "avatar_url": "https://github.com/assignee2.png",
                    "html_url": "https://github.com/assignee2",
                },
            ],
            "labels": [
                {
                    "name": "bug",
                    "color": "d73a4a",
                    "description": "Something isn't working",
                    "url": "https://api.github.com/repos/owner/repo/labels/bug",
                    "id": 1001,
                },
                {
                    "name": "priority-high",
                    "color": "ff0000",
                    "description": "High priority",
                    "url": (
                        "https://api.github.com/repos/owner/repo/labels/priority-high"
                    ),
                    "id": 1003,
                },
            ],
            "created_at": "2023-01-15T10:00:00Z",
            "updated_at": "2023-01-15T10:00:00Z",
            "closed_at": None,
            "html_url": "https://github.com/owner/repo/issues/1",
            "comments": 0,
        }

        test_data = (
            builder.with_labels(3)  # Add standard labels
            .with_issues(1, custom_issues=[custom_issue])
            .build()
        )

        # Write test data to files
        data_path = Path(temp_data_dir)
        for key, data in test_data.items():
            with open(data_path / f"{key}.json", "w") as f:
                json.dump(data, f)

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []

        # Mock successful responses
        mock_boundary.create_label.return_value = {"id": 999, "name": "test"}
        mock_boundary.create_issue.return_value = {"number": 10, "id": 999}

        # Execute restore
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_pull_requests=True,
        )

        # Verify that issue was created with correct labels
        issue_calls = mock_boundary.create_issue.call_args_list
        assert len(issue_calls) == 1

        # Check that labels were extracted correctly from the complex issue
        issue_call_args = issue_calls[0][0]  # positional arguments
        expected_labels = ["bug", "priority-high"]
        assert sorted(issue_call_args[3]) == sorted(
            expected_labels
        )  # labels is 4th arg
