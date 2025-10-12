"""Integration tests for core save/restore workflows."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.operations.save import save_repository_data_with_strategy_pattern
from src.github import create_github_service
from src.storage import create_storage_service
from src.operations.restore.restore import restore_repository_data_with_strategy_pattern

from tests.shared.mocks import add_pr_method_mocks, add_sub_issues_method_mocks

pytestmark = [pytest.mark.integration]


class TestSaveRestoreWorkflows:
    """Integration tests for complete save/restore workflows."""

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
        add_pr_method_mocks(mock_boundary, sample_github_data)
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
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
        with open(data_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

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
                "url": (
                    "https://api.github.com/repos/owner/target_repo/labels/enhancement"
                ),
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
            include_pull_requests=True,
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
        add_pr_method_mocks(save_boundary, sample_github_data)
        add_sub_issues_method_mocks(save_boundary)

        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
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
            include_pull_requests=True,
        )

        # Verify data integrity by checking that saved data matches restored data

        # Check that same number of items were saved and restored
        # Note: Labels API is called once for collection
        assert save_boundary.get_repository_labels.call_count == 1
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
        add_pr_method_mocks(mock_boundary)
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
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
            include_pull_requests=True,
        )

        # Verify no creation methods were called for empty data
        assert mock_boundary.create_label.call_count == 0
        assert mock_boundary.create_issue.call_count == 0
        assert mock_boundary.create_pull_request.call_count == 0
        assert mock_boundary.create_pull_request_comment.call_count == 0
