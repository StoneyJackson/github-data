"""Integration tests for GitHub Data save/restore workflows."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.operations.save import save_repository_data_with_services
from src.github import create_github_service
from src.storage import create_storage_service
from operations.restore.restore import restore_repository_data_with_strategy_pattern

pytestmark = [pytest.mark.integration]


def _add_pr_method_mocks(mock_boundary, sample_data=None):
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


def _add_sub_issues_method_mocks(mock_boundary):
    """Add sub-issues method mocks to boundary for compatibility."""
    mock_boundary.get_repository_sub_issues.return_value = []


class TestSaveRestoreIntegration:
    """Integration tests for complete save/restore workflows."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def sample_github_data(self):
        """Sample GitHub API JSON data that boundary would return."""
        return {
            "labels": [
                {
                    "name": "bug",
                    "color": "d73a4a",
                    "description": "Something isn't working",
                    "url": "https://api.github.com/repos/owner/repo/labels/bug",
                    "id": 1001,
                },
                {
                    "name": "enhancement",
                    "color": "a2eeef",
                    "description": "New feature or request",
                    "url": "https://api.github.com/repos/owner/repo/labels/enhancement",
                    "id": 1002,
                },
            ],
            "issues": [
                {
                    "id": 2001,
                    "number": 1,
                    "title": "Fix authentication bug",
                    "body": "Users cannot login with valid credentials",
                    "state": "open",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "assignees": [],
                    "labels": [
                        {
                            "name": "bug",
                            "color": "d73a4a",
                            "description": "Something isn't working",
                            "url": "https://api.github.com/repos/owner/repo/labels/bug",
                            "id": 1001,
                        }
                    ],
                    "created_at": "2023-01-15T10:30:00Z",
                    "updated_at": "2023-01-15T14:20:00Z",
                    "closed_at": None,
                    "html_url": "https://github.com/owner/repo/issues/1",
                    "comments": 2,
                },
                {
                    "id": 2002,
                    "number": 2,
                    "title": "Add user dashboard",
                    "body": None,
                    "state": "closed",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "assignees": [
                        {
                            "login": "alice",
                            "id": 3001,
                            "avatar_url": "https://github.com/alice.png",
                            "html_url": "https://github.com/alice",
                        }
                    ],
                    "labels": [
                        {
                            "name": "enhancement",
                            "color": "a2eeef",
                            "description": "New feature or request",
                            "url": (
                                "https://api.github.com/repos/owner/repo/"
                                "labels/enhancement"
                            ),
                            "id": 1002,
                        }
                    ],
                    "created_at": "2023-01-10T09:00:00Z",
                    "updated_at": "2023-01-12T16:45:00Z",
                    "closed_at": "2023-01-12T16:45:00Z",
                    "html_url": "https://github.com/owner/repo/issues/2",
                    "comments": 0,
                },
            ],
            "comments": [
                {
                    "id": 4001,
                    "body": "I can reproduce this issue",
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "created_at": "2023-01-15T12:00:00Z",
                    "updated_at": "2023-01-15T12:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/1#issuecomment-4001"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                },
                {
                    "id": 4002,
                    "body": "Fixed in PR #3",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "created_at": "2023-01-15T14:00:00Z",
                    "updated_at": "2023-01-15T14:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/2#issuecomment-4002"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/2",
                },
            ],
            "pull_requests": [
                {
                    "id": 5001,
                    "number": 3,
                    "title": "Implement API rate limiting",
                    "body": "This PR adds rate limiting to prevent API abuse",
                    "state": "MERGED",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "assignees": [
                        {
                            "login": "bob",
                            "id": 3002,
                            "avatar_url": "https://github.com/bob.png",
                            "html_url": "https://github.com/bob",
                        }
                    ],
                    "labels": [
                        {
                            "name": "enhancement",
                            "color": "a2eeef",
                            "description": "New feature or request",
                            "url": (
                                "https://api.github.com/repos/owner/repo/"
                                "labels/enhancement"
                            ),
                            "id": 1002,
                        }
                    ],
                    "created_at": "2023-01-16T10:00:00Z",
                    "updated_at": "2023-01-18T15:30:00Z",
                    "closed_at": "2023-01-18T15:30:00Z",
                    "merged_at": "2023-01-18T15:30:00Z",
                    "merge_commit_sha": "abc123def456",
                    "base_ref": "main",
                    "head_ref": "feature/rate-limiting",
                    "html_url": "https://github.com/owner/repo/pull/3",
                    "comments": 1,
                },
                {
                    "id": 5002,
                    "number": 4,
                    "title": "Fix security vulnerability",
                    "body": "Address XSS vulnerability in user input",
                    "state": "OPEN",
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "assignees": [],
                    "labels": [
                        {
                            "name": "bug",
                            "color": "d73a4a",
                            "description": "Something isn't working",
                            "url": "https://api.github.com/repos/owner/repo/labels/bug",
                            "id": 1001,
                        }
                    ],
                    "created_at": "2023-01-17T14:00:00Z",
                    "updated_at": "2023-01-17T16:45:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "merge_commit_sha": None,
                    "base_ref": "main",
                    "head_ref": "fix/xss-vulnerability",
                    "html_url": "https://github.com/owner/repo/pull/4",
                    "comments": 2,
                },
            ],
            "pr_comments": [
                {
                    "id": 6001,
                    "body": "Great work on the rate limiting implementation!",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "created_at": "2023-01-18T14:00:00Z",
                    "updated_at": "2023-01-18T14:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/pull/3#issuecomment-6001"
                    ),
                    "pull_request_url": "https://github.com/owner/repo/pull/3",
                },
                {
                    "id": 6002,
                    "body": "Need to add more tests for edge cases",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "created_at": "2023-01-17T15:30:00Z",
                    "updated_at": "2023-01-17T15:30:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/pull/4#issuecomment-6002"
                    ),
                    "pull_request_url": "https://github.com/owner/repo/pull/4",
                },
                {
                    "id": 6003,
                    "body": "Updated the implementation to handle edge cases",
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "created_at": "2023-01-17T16:45:00Z",
                    "updated_at": "2023-01-17T16:45:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/pull/4#issuecomment-6003"
                    ),
                    "pull_request_url": "https://github.com/owner/repo/pull/4",
                },
            ],
        }

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_creates_json_files_with_correct_structure(
        self, mock_boundary_class, temp_data_dir, sample_github_data
    ):
        """Test that save operation creates properly structured JSON files."""
        # Setup mock boundary to return our sample data
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = sample_github_data["labels"]
        mock_boundary.get_repository_issues.return_value = sample_github_data["issues"]
        mock_boundary.get_all_issue_comments.return_value = sample_github_data[
            "comments"
        ]
        _add_pr_method_mocks(mock_boundary, sample_github_data)
        _add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_services(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify JSON files were created
        data_path = Path(temp_data_dir)
        assert (data_path / "labels.json").exists()
        assert (data_path / "issues.json").exists()
        assert (data_path / "comments.json").exists()
        assert (data_path / "pull_requests.json").exists()
        assert (data_path / "pr_comments.json").exists()

        # Verify labels.json content and structure
        with open(data_path / "labels.json") as f:
            labels_data = json.load(f)
        assert len(labels_data) == 2
        assert labels_data[0]["name"] == "bug"
        assert labels_data[0]["color"] == "d73a4a"
        assert labels_data[1]["name"] == "enhancement"
        assert labels_data[1]["description"] == "New feature or request"

        # Verify issues.json content and structure
        with open(data_path / "issues.json") as f:
            issues_data = json.load(f)
        assert len(issues_data) == 2

        # Check first issue (open with body)
        issue1 = issues_data[0]
        assert issue1["title"] == "Fix authentication bug"
        assert issue1["state"] == "open"
        assert issue1["body"] == "Users cannot login with valid credentials"
        assert issue1["user"]["login"] == "alice"
        assert len(issue1["labels"]) == 1
        assert issue1["labels"][0]["name"] == "bug"
        assert issue1["closed_at"] is None

        # Check second issue (closed with assignee, no body)
        issue2 = issues_data[1]
        assert issue2["title"] == "Add user dashboard"
        assert issue2["state"] == "closed"
        assert issue2["body"] is None
        assert issue2["user"]["login"] == "bob"
        assert len(issue2["assignees"]) == 1
        assert issue2["assignees"][0]["login"] == "alice"
        assert issue2["closed_at"] is not None

        # Verify comments.json content and structure
        with open(data_path / "comments.json") as f:
            comments_data = json.load(f)
        assert len(comments_data) == 2
        assert comments_data[0]["body"] == "I can reproduce this issue"
        assert comments_data[0]["user"]["login"] == "charlie"
        assert comments_data[1]["body"] == "Fixed in PR #3"
        assert comments_data[1]["user"]["login"] == "alice"

        # Verify pull_requests.json content and structure
        with open(data_path / "pull_requests.json") as f:
            prs_data = json.load(f)
        assert len(prs_data) == 2

        # Check first PR (merged)
        pr1 = prs_data[0]
        assert pr1["title"] == "Implement API rate limiting"
        assert pr1["state"] == "MERGED"
        assert pr1["base_ref"] == "main"
        assert pr1["head_ref"] == "feature/rate-limiting"
        assert pr1["user"]["login"] == "alice"
        assert pr1["merged_at"] is not None
        assert len(pr1["assignees"]) == 1
        assert pr1["assignees"][0]["login"] == "bob"

        # Check second PR (open)
        pr2 = prs_data[1]
        assert pr2["title"] == "Fix security vulnerability"
        assert pr2["state"] == "OPEN"
        assert pr2["base_ref"] == "main"
        assert pr2["head_ref"] == "fix/xss-vulnerability"
        assert pr2["user"]["login"] == "charlie"
        assert pr2["merged_at"] is None
        assert len(pr2["assignees"]) == 0

        # Verify pr_comments.json content and structure
        with open(data_path / "pr_comments.json") as f:
            pr_comments_data = json.load(f)
        assert len(pr_comments_data) == 3
        assert (
            pr_comments_data[0]["body"]
            == "Great work on the rate limiting implementation!"
        )
        assert pr_comments_data[0]["user"]["login"] == "bob"
        assert pr_comments_data[1]["body"] == "Need to add more tests for edge cases"
        assert pr_comments_data[1]["user"]["login"] == "alice"
        assert (
            pr_comments_data[2]["body"]
            == "Updated the implementation to handle edge cases"
        )
        assert pr_comments_data[2]["user"]["login"] == "charlie"

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_recreates_data_from_json_files(
        self, mock_boundary_class, temp_data_dir, sample_github_data
    ):
        """Test that restore operation correctly recreates repository data."""
        # Create JSON files (simulating previous save operation)
        data_path = Path(temp_data_dir)

        with open(data_path / "labels.json", "w") as f:
            json.dump(sample_github_data["labels"], f)
        with open(data_path / "issues.json", "w") as f:
            json.dump(sample_github_data["issues"], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump(sample_github_data["comments"], f)
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump(sample_github_data["pull_requests"], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump(sample_github_data["pr_comments"], f)

        # Setup mock boundary for creation operations
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock get_repository_labels for conflict detection (default: empty repository)
        mock_boundary.get_repository_labels.return_value = []

        # Mock return values for create operations
        mock_boundary.create_label.side_effect = [
            {
                "name": "bug",
                "id": 5001,
                "color": "d73a4a",
                "description": "Something isn't working",
                "url": "https://api.github.com/repos/owner/target_repo/labels/bug",
            },
            {
                "name": "enhancement",
                "id": 5002,
                "color": "a2eeef",
                "description": "New feature or request",
                "url": "https://api.github.com/repos/owner/target_repo/labels/enhancement",  # noqa: E501
            },
        ]
        mock_boundary.create_issue.side_effect = [
            {
                "number": 10,
                "title": "Fix authentication bug",
                "id": 6001,
                "body": "Test issue body",
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
                "created_at": "2023-01-12T16:45:00Z",
                "updated_at": "2023-01-12T16:45:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/target_repo/issues/10",
                "comments": 0,
            },
            {
                "number": 11,
                "title": "Add user dashboard",
                "id": 6002,
                "body": "Test issue body",
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
                "created_at": "2023-01-15T09:30:00Z",
                "updated_at": "2023-01-15T09:30:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/target_repo/issues/11",
                "comments": 0,
            },
        ]
        mock_boundary.create_issue_comment.side_effect = [
            {
                "id": 7001,
                "body": "I can reproduce this issue",
                "user": {
                    "login": "charlie",
                    "id": 3003,
                    "avatar_url": "https://github.com/images/error/charlie_happy.gif",
                    "url": "https://api.github.com/users/charlie",
                    "html_url": "https://github.com/charlie",
                },
                "created_at": "2023-01-12T17:00:00Z",
                "updated_at": "2023-01-12T17:00:00Z",
                "html_url": (
                    "https://github.com/owner/target_repo/issues/10#issuecomment-7001"
                ),
                "issue_url": "https://api.github.com/repos/owner/target_repo/issues/10",
            },
            {
                "id": 7002,
                "body": "Fixed in PR #3",
                "user": {
                    "login": "alice",
                    "id": 2002,
                    "avatar_url": "https://github.com/images/error/alice_happy.gif",
                    "url": "https://api.github.com/users/alice",
                    "html_url": "https://github.com/alice",
                },
                "created_at": "2023-01-15T10:00:00Z",
                "updated_at": "2023-01-15T10:00:00Z",
                "html_url": (
                    "https://github.com/owner/target_repo/issues/11#issuecomment-7002"
                ),
                "issue_url": "https://api.github.com/repos/owner/target_repo/issues/11",
            },
        ]
        mock_boundary.create_pull_request.side_effect = [
            {
                "id": 8001,
                "number": 20,
                "title": "Implement API rate limiting",
                "body": "This PR adds rate limiting to prevent API abuse",
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
                "created_at": "2023-01-20T10:00:00Z",
                "updated_at": "2023-01-20T10:00:00Z",
                "closed_at": None,
                "merged_at": None,
                "merge_commit_sha": None,
                "base_ref": "main",
                "head_ref": "feature/rate-limiting",
                "html_url": "https://github.com/owner/target_repo/pull/20",
                "comments": 0,
            },
            {
                "id": 8002,
                "number": 21,
                "title": "Fix security vulnerability",
                "body": "Address XSS vulnerability in user input",
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
                "created_at": "2023-01-20T11:00:00Z",
                "updated_at": "2023-01-20T11:00:00Z",
                "closed_at": None,
                "merged_at": None,
                "merge_commit_sha": None,
                "base_ref": "main",
                "head_ref": "fix/xss-vulnerability",
                "html_url": "https://github.com/owner/target_repo/pull/21",
                "comments": 0,
            },
        ]
        mock_boundary.create_pull_request_comment.side_effect = [
            {
                "id": 9001,
                "body": "Great work on the rate limiting implementation!",
                "user": {
                    "login": "testuser",
                    "id": 1,
                    "avatar_url": "https://github.com/images/error/testuser_happy.gif",
                    "url": "https://api.github.com/users/testuser",
                    "html_url": "https://github.com/testuser",
                },
                "created_at": "2023-01-20T12:00:00Z",
                "updated_at": "2023-01-20T12:00:00Z",
                "html_url": (
                    "https://github.com/owner/target_repo/pull/20#issuecomment-9001"
                ),
                "pull_request_url": "https://github.com/owner/target_repo/pull/20",
            },
            {
                "id": 9002,
                "body": "Need to add more tests for edge cases",
                "user": {
                    "login": "testuser",
                    "id": 1,
                    "avatar_url": "https://github.com/images/error/testuser_happy.gif",
                    "url": "https://api.github.com/users/testuser",
                    "html_url": "https://github.com/testuser",
                },
                "created_at": "2023-01-20T12:30:00Z",
                "updated_at": "2023-01-20T12:30:00Z",
                "html_url": (
                    "https://github.com/owner/target_repo/pull/21#issuecomment-9002"
                ),
                "pull_request_url": "https://github.com/owner/target_repo/pull/21",
            },
            {
                "id": 9003,
                "body": "Updated the implementation to handle edge cases",
                "user": {
                    "login": "testuser",
                    "id": 1,
                    "avatar_url": "https://github.com/images/error/testuser_happy.gif",
                    "url": "https://api.github.com/users/testuser",
                    "html_url": "https://github.com/testuser",
                },
                "created_at": "2023-01-20T13:00:00Z",
                "updated_at": "2023-01-20T13:00:00Z",
                "html_url": (
                    "https://github.com/owner/target_repo/pull/21#issuecomment-9003"
                ),
                "pull_request_url": "https://github.com/owner/target_repo/pull/21",
            },
        ]

        # Execute restore operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/target_repo",
            temp_data_dir,
            include_original_metadata=False,
            include_prs=True,
        )

        # Verify boundary methods were called correctly
        assert mock_boundary.create_label.call_count == 2
        assert mock_boundary.create_issue.call_count == 2
        assert mock_boundary.create_issue_comment.call_count == 2
        assert mock_boundary.create_pull_request.call_count == 2
        assert mock_boundary.create_pull_request_comment.call_count == 3

        # Verify label creation calls
        label_calls = mock_boundary.create_label.call_args_list

        # First label call - check positional arguments
        first_label_call = label_calls[0][0]  # positional arguments
        assert first_label_call[1] == "bug"  # name
        assert first_label_call[2] == "d73a4a"  # color
        assert first_label_call[3] == "Something isn't working"  # description

        # Second label call
        second_label_call = label_calls[1][0]  # positional arguments
        assert second_label_call[1] == "enhancement"  # name
        assert second_label_call[2] == "a2eeef"  # color
        assert second_label_call[3] == "New feature or request"  # description

        # Verify issue creation calls
        issue_calls = mock_boundary.create_issue.call_args_list

        # First issue call - check positional arguments
        first_issue_call = issue_calls[0][0]  # positional arguments
        assert first_issue_call[1] == "Fix authentication bug"  # title
        assert (
            first_issue_call[2] == "Users cannot login with valid credentials"
        )  # body
        assert first_issue_call[3] == ["bug"]  # labels

        # Second issue call (with None body converted to empty string)
        second_issue_call = issue_calls[1][0]  # positional arguments
        assert second_issue_call[1] == "Add user dashboard"  # title
        assert second_issue_call[2] == ""  # None converted to empty string
        assert second_issue_call[3] == ["enhancement"]  # labels

        # Verify comment creation calls
        comment_calls = mock_boundary.create_issue_comment.call_args_list

        # First comment call (mapped to issue #10)
        first_comment_call = comment_calls[0][0]  # positional arguments
        assert (
            first_comment_call[1] == 10
        )  # issue_number - Mapped from original issue #1
        assert first_comment_call[2] == "I can reproduce this issue"  # body

        # Second comment call (mapped to issue #11)
        second_comment_call = comment_calls[1][0]  # positional arguments
        assert second_comment_call[1] == 11  # issue_number - Mapped from issue #2
        assert second_comment_call[2] == "Fixed in PR #3"  # body

        # Verify pull request creation calls
        pr_calls = mock_boundary.create_pull_request.call_args_list

        # First PR call - check positional arguments
        first_pr_call = pr_calls[0][0]  # positional arguments
        assert first_pr_call[1] == "Implement API rate limiting"  # title
        assert (
            first_pr_call[2] == "This PR adds rate limiting to prevent API abuse"
        )  # body
        assert first_pr_call[3] == "feature/rate-limiting"  # head
        assert first_pr_call[4] == "main"  # base

        # Second PR call
        second_pr_call = pr_calls[1][0]  # positional arguments
        assert second_pr_call[1] == "Fix security vulnerability"  # title
        assert second_pr_call[2] == "Address XSS vulnerability in user input"  # body
        assert second_pr_call[3] == "fix/xss-vulnerability"  # head
        assert second_pr_call[4] == "main"  # base

        # Verify PR comment creation calls
        pr_comment_calls = mock_boundary.create_pull_request_comment.call_args_list

        # First PR comment call (mapped to PR #20)
        first_pr_comment_call = pr_comment_calls[0][0]  # positional arguments
        assert first_pr_comment_call[1] == 20  # pr_number - Mapped from original PR #3
        assert (
            first_pr_comment_call[2]
            == "Great work on the rate limiting implementation!"
        )  # body

        # Second PR comment call (mapped to PR #21)
        second_pr_comment_call = pr_comment_calls[1][0]  # positional arguments
        assert second_pr_comment_call[1] == 21  # pr_number - Mapped from original PR #4
        assert (
            second_pr_comment_call[2] == "Need to add more tests for edge cases"
        )  # body

        # Third PR comment call (mapped to PR #21)
        third_pr_comment_call = pr_comment_calls[2][0]  # positional arguments
        assert third_pr_comment_call[1] == 21  # pr_number - Mapped from original PR #4
        assert (
            third_pr_comment_call[2]
            == "Updated the implementation to handle edge cases"
        )  # body

    @patch("src.github.service.GitHubApiBoundary")
    def test_complete_save_restore_cycle_preserves_data_integrity(
        self, mock_boundary_class, temp_data_dir, sample_github_data
    ):
        """Test that complete save → restore cycle preserves all data correctly."""

        # Phase 1: Save operation
        save_boundary = Mock()
        mock_boundary_class.return_value = save_boundary
        save_boundary.get_repository_labels.return_value = sample_github_data["labels"]
        save_boundary.get_repository_issues.return_value = sample_github_data["issues"]
        save_boundary.get_all_issue_comments.return_value = sample_github_data[
            "comments"
        ]
        _add_pr_method_mocks(save_boundary, sample_github_data)
        _add_sub_issues_method_mocks(save_boundary)

        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_services(
            github_service, storage_service, "owner/source_repo", temp_data_dir
        )

        # Phase 2: Restore operation with fresh mock
        restore_boundary = Mock()
        mock_boundary_class.return_value = restore_boundary

        # Mock get_repository_labels for conflict detection (default: empty repository)
        restore_boundary.get_repository_labels.return_value = []

        restore_boundary.create_label.return_value = {
            "id": 999,
            "name": "test",
            "color": "ffffff",
            "description": "test",
            "url": "https://api.github.com/repos/owner/target_repo/labels/test",
        }
        restore_boundary.create_issue.return_value = {
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
            "html_url": "https://github.com/owner/target_repo/issues/999",
            "comments": 0,
        }
        restore_boundary.create_issue_comment.return_value = {
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
            "html_url": (
                "https://github.com/owner/target_repo/issues/999#issuecomment-888"
            ),
            "issue_url": "https://api.github.com/repos/owner/target_repo/issues/999",
        }
        restore_boundary.create_pull_request.return_value = {
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
            "html_url": "https://github.com/owner/target_repo/pull/777",
            "comments": 0,
        }
        restore_boundary.create_pull_request_comment.return_value = {
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
            "html_url": (
                "https://github.com/owner/target_repo/pull/777#issuecomment-666"
            ),
            "pull_request_url": "https://github.com/owner/target_repo/pull/777",
        }

        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/target_repo",
            temp_data_dir,
            include_original_metadata=False,
            include_prs=True,
        )

        # Verify data integrity by checking that saved data matches restored data

        # Check that same number of items were saved and restored
        # Note: Labels API is called twice - once for validation, once for collection
        assert save_boundary.get_repository_labels.call_count == 2
        assert restore_boundary.create_label.call_count == 2

        assert save_boundary.get_repository_issues.call_count == 1
        assert restore_boundary.create_issue.call_count == 2

        assert save_boundary.get_all_issue_comments.call_count == 1
        assert restore_boundary.create_issue_comment.call_count == 2

        # Verify PR operations
        assert save_boundary.get_repository_pull_requests.call_count == 1
        assert restore_boundary.create_pull_request.call_count == 2

        assert save_boundary.get_all_pull_request_comments.call_count == 1
        assert restore_boundary.create_pull_request_comment.call_count == 3

        # Verify that all original label data was preserved in restore calls
        restore_label_calls = restore_boundary.create_label.call_args_list
        original_labels = sample_github_data["labels"]

        for original, call in zip(original_labels, restore_label_calls):
            restored_args = call[
                0
            ]  # positional arguments: (repo_name, name, color, description)
            assert restored_args[1] == original["name"]  # name is second positional arg
            assert (
                restored_args[2] == original["color"]
            )  # color is third positional arg
            assert (
                restored_args[3] == original["description"]
            )  # description is fourth positional arg

        # Verify that all original issue data was preserved
        restore_issue_calls = restore_boundary.create_issue.call_args_list
        original_issues = sample_github_data["issues"]

        for original, call in zip(original_issues, restore_issue_calls):
            restored_args = call[
                0
            ]  # positional arguments: (repo_name, title, body, labels)
            assert (
                restored_args[1] == original["title"]
            )  # title is second positional arg
            # Handle None body conversion
            expected_body = original["body"] or ""
            assert restored_args[2] == expected_body  # body is third positional arg
            # Check that labels were extracted correctly
            expected_labels = [label["name"] for label in original["labels"]]
            assert (
                restored_args[3] == expected_labels
            )  # labels is fourth positional arg

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_handles_empty_repository(self, mock_boundary_class, temp_data_dir):
        """Test save operation with repository that has no data."""
        # Setup mock for empty repository
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        _add_pr_method_mocks(mock_boundary)
        _add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_services(
            github_service, storage_service, "owner/empty_repo", temp_data_dir
        )

        # Verify JSON files are created even with empty data
        data_path = Path(temp_data_dir)
        assert (data_path / "labels.json").exists()
        assert (data_path / "issues.json").exists()
        assert (data_path / "comments.json").exists()

        # Verify files contain empty arrays
        with open(data_path / "labels.json") as f:
            assert json.load(f) == []
        with open(data_path / "issues.json") as f:
            assert json.load(f) == []
        with open(data_path / "comments.json") as f:
            assert json.load(f) == []
        with open(data_path / "pull_requests.json") as f:
            assert json.load(f) == []
        with open(data_path / "pr_comments.json") as f:
            assert json.load(f) == []

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_handles_empty_json_files(self, mock_boundary_class, temp_data_dir):
        """Test restore operation with empty JSON files."""
        # Create empty JSON files
        data_path = Path(temp_data_dir)
        for filename in [
            "labels.json",
            "issues.json",
            "comments.json",
            "pull_requests.json",
            "pr_comments.json",
        ]:
            with open(data_path / filename, "w") as f:
                json.dump([], f)

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock get_repository_labels for conflict detection (default: empty repository)
        mock_boundary.get_repository_labels.return_value = []

        # Execute restore operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_prs=True,
        )

        # Verify no creation methods were called for empty data
        assert mock_boundary.create_label.call_count == 0
        assert mock_boundary.create_issue.call_count == 0
        assert mock_boundary.create_pull_request.call_count == 0
        assert mock_boundary.create_pull_request_comment.call_count == 0

    def test_restore_fails_when_json_files_missing(self, temp_data_dir):
        """Test restore fails gracefully when required files are missing."""
        with pytest.raises(FileNotFoundError) as exc_info:
            github_service = create_github_service("fake_token")
            storage_service = create_storage_service("json")
            restore_repository_data_with_strategy_pattern(
                github_service,
                storage_service,
                "owner/repo",
                temp_data_dir,
                include_prs=True,
            )

        assert "labels.json" in str(exc_info.value)

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_creates_output_directory_if_missing(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test that save operation creates output directory structure."""
        # Setup mock
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        _add_pr_method_mocks(mock_boundary)
        _add_sub_issues_method_mocks(mock_boundary)

        # Use nested directory that doesn't exist
        nested_path = Path(temp_data_dir) / "backup" / "github-data"

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_services(
            github_service, storage_service, "owner/repo", str(nested_path)
        )

        # Verify directory was created
        assert nested_path.exists()
        assert nested_path.is_dir()

        # Verify files were created in the new directory
        assert (nested_path / "labels.json").exists()
        assert (nested_path / "issues.json").exists()
        assert (nested_path / "comments.json").exists()
        assert (nested_path / "pull_requests.json").exists()
        assert (nested_path / "pr_comments.json").exists()

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
            include_prs=True,
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


class TestErrorHandlingIntegration:
    """Integration tests for error scenarios and edge cases."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_handles_github_api_failures_gracefully(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test that restore continues despite GitHub API failures."""
        # Create test data files
        data_path = Path(temp_data_dir)

        test_labels = [
            {
                "name": "bug",
                "color": "ff0000",
                "description": "Bug label",
                "url": "http://example.com",
                "id": 1,
            },
            {
                "name": "feature",
                "color": "00ff00",
                "description": "Feature label",
                "url": "http://example.com",
                "id": 2,
            },
        ]

        with open(data_path / "labels.json", "w") as f:
            json.dump(test_labels, f)
        with open(data_path / "issues.json", "w") as f:
            json.dump([], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock to simulate GitHub API failures
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock get_repository_labels for conflict detection (default: empty repository)
        mock_boundary.get_repository_labels.return_value = []

        # First label succeeds, second fails
        mock_boundary.create_label.side_effect = [
            {
                "id": 100,
                "name": "bug",
                "color": "ff0000",
                "description": "Bug label",
                "url": "http://example.com",
            },  # Success
            Exception("API rate limit exceeded"),  # Failure
        ]

        # Execute restore operation - should fail on second error
        with pytest.raises(Exception, match="Failed to create label 'feature'"):
            github_service = create_github_service("fake_token")
            storage_service = create_storage_service("json")
            restore_repository_data_with_strategy_pattern(
                github_service,
                storage_service,
                "owner/repo",
                temp_data_dir,
                include_prs=True,
            )

        # Verify first label succeeded, second failed and stopped execution
        assert mock_boundary.create_label.call_count == 2

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_handles_malformed_json_files(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test restore operation with malformed JSON files."""
        # Create malformed JSON file
        data_path = Path(temp_data_dir)
        with open(data_path / "labels.json", "w") as f:
            f.write("{ invalid json syntax }")
        with open(data_path / "issues.json", "w") as f:
            json.dump([], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary for repository access validation
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock successful repository access check
        mock_boundary.get_repository.return_value = {"name": "repo"}

        # Restore should fail with JSON decode error
        with pytest.raises(json.JSONDecodeError):
            github_service = create_github_service("fake_token")
            storage_service = create_storage_service("json")
            restore_repository_data_with_strategy_pattern(
                github_service,
                storage_service,
                "owner/repo",
                temp_data_dir,
                include_prs=True,
            )

    @patch("src.github.service.GitHubApiBoundary")
    def test_data_type_conversion_and_validation(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test that data types are properly converted and validated."""
        # Test data with various data type scenarios
        complex_github_data = {
            "labels": [
                {
                    "name": "priority/high",
                    "color": "ff0000",
                    "description": None,  # Test None handling
                    "url": (
                        "https://api.github.com/repos/owner/repo/labels/priority%2Fhigh"
                    ),
                    "id": 1234567890,  # Large integer
                }
            ],
            "issues": [
                {
                    "id": 9876543210,  # Large integer
                    "number": 42,
                    "title": "Issue with unicode: 测试 🚀",  # Unicode handling
                    "body": "",  # Empty string
                    "state": "closed",
                    "user": {
                        "login": "test.user-123",  # Special characters in username
                        "id": 111,
                        "avatar_url": "https://github.com/avatar.png",
                        "html_url": "https://github.com/test.user-123",
                    },
                    "assignees": [],
                    "labels": [],
                    "created_at": "2023-12-25T09:30:45Z",  # ISO datetime
                    "updated_at": "2023-12-25T09:30:45Z",
                    "closed_at": "2023-12-25T10:15:30Z",
                    "html_url": "https://github.com/owner/repo/issues/42",
                    "comments": 0,
                }
            ],
            "comments": [],
        }

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = complex_github_data["labels"]
        mock_boundary.get_repository_issues.return_value = complex_github_data["issues"]
        mock_boundary.get_all_issue_comments.return_value = complex_github_data[
            "comments"
        ]
        _add_pr_method_mocks(mock_boundary)
        _add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_services(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify data was saved correctly
        data_path = Path(temp_data_dir)

        # Check labels with None description
        with open(data_path / "labels.json") as f:
            labels_data = json.load(f)
        assert labels_data[0]["description"] is None
        assert labels_data[0]["name"] == "priority/high"
        assert isinstance(labels_data[0]["id"], int)

        # Check issues with unicode and datetime
        with open(data_path / "issues.json") as f:
            issues_data = json.load(f)
        assert "测试 🚀" in issues_data[0]["title"]
        assert issues_data[0]["body"] == ""
        assert isinstance(issues_data[0]["id"], int)
        assert isinstance(
            issues_data[0]["created_at"], str
        )  # Datetime serialized as string

    @patch("src.github.service.GitHubApiBoundary")
    def test_closed_issue_restoration_with_metadata(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test closed issues are restored with their state and metadata."""
        from operations.restore.restore import (
            restore_repository_data_with_strategy_pattern,
        )
        from src.entities import Issue, GitHubUser
        from datetime import datetime
        import json

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
            include_prs=True,
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
        from operations.restore.restore import (
            restore_repository_data_with_strategy_pattern,
        )
        from src.entities import Issue, GitHubUser
        from datetime import datetime
        import json

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
            include_prs=True,
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
