"""Integration tests for selective issue/PR save/restore workflows."""

import json
from unittest.mock import Mock

import pytest

from src.config.settings import ApplicationConfig
from src.operations.save.save import save_repository_data_with_config
from src.operations.restore.restore import restore_repository_data_with_config
from src.storage import create_storage_service
from tests.shared import (
    add_pr_method_mocks,
)

pytestmark = [pytest.mark.integration, pytest.mark.medium]


class TestSelectiveSaveRestore:
    """Integration tests for selective issue/PR save/restore workflows."""

    @pytest.fixture
    def sample_github_data(self):
        """Sample GitHub API data for selective testing."""
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
                    "state_reason": None,
                    "created_at": "2023-01-01T10:00:00Z",
                    "updated_at": "2023-01-01T10:00:00Z",
                    "closed_at": None,
                    "url": "https://api.github.com/repos/owner/repo/issues/1",
                    "html_url": "https://github.com/owner/repo/issues/1",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "labels": [
                        {
                            "name": "bug",
                            "color": "d73a4a",
                            "description": "Something isn't working",
                            "url": "https://api.github.com/repos/owner/repo/labels/bug",
                            "id": 1001,
                        }
                    ],
                },
                {
                    "id": 2002,
                    "number": 2,
                    "title": "Add user dashboard",
                    "body": "Create a dashboard for user management",
                    "state": "open",
                    "state_reason": None,
                    "created_at": "2023-01-02T10:00:00Z",
                    "updated_at": "2023-01-02T10:00:00Z",
                    "closed_at": None,
                    "url": "https://api.github.com/repos/owner/repo/issues/2",
                    "html_url": "https://github.com/owner/repo/issues/2",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "labels": [
                        {
                            "name": "enhancement",
                            "color": "a2eeef",
                            "description": "New feature or request",
                            "url": (
                                "https://api.github.com/repos/owner/repo/labels/"
                                "enhancement"
                            ),
                            "id": 1002,
                        }
                    ],
                },
                {
                    "id": 2003,
                    "number": 3,
                    "title": "Performance optimization",
                    "body": "Optimize database queries",
                    "state": "closed",
                    "state_reason": "completed",
                    "created_at": "2023-01-03T10:00:00Z",
                    "updated_at": "2023-01-03T12:00:00Z",
                    "closed_at": "2023-01-03T12:00:00Z",
                    "url": "https://api.github.com/repos/owner/repo/issues/3",
                    "html_url": "https://github.com/owner/repo/issues/3",
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "labels": [],
                },
                {
                    "id": 2004,
                    "number": 4,
                    "title": "Update documentation",
                    "body": "Update API documentation",
                    "state": "open",
                    "state_reason": None,
                    "created_at": "2023-01-04T10:00:00Z",
                    "updated_at": "2023-01-04T10:00:00Z",
                    "closed_at": None,
                    "url": "https://api.github.com/repos/owner/repo/issues/4",
                    "html_url": "https://github.com/owner/repo/issues/4",
                    "user": {
                        "login": "dave",
                        "id": 3004,
                        "avatar_url": "https://github.com/dave.png",
                        "html_url": "https://github.com/dave",
                    },
                    "labels": [],
                },
                {
                    "id": 2005,
                    "number": 5,
                    "title": "Security review",
                    "body": "Conduct security audit",
                    "state": "open",
                    "state_reason": None,
                    "created_at": "2023-01-05T10:00:00Z",
                    "updated_at": "2023-01-05T10:00:00Z",
                    "closed_at": None,
                    "url": "https://api.github.com/repos/owner/repo/issues/5",
                    "html_url": "https://github.com/owner/repo/issues/5",
                    "user": {
                        "login": "eve",
                        "id": 3005,
                        "avatar_url": "https://github.com/eve.png",
                        "html_url": "https://github.com/eve",
                    },
                    "labels": [
                        {
                            "name": "bug",
                            "color": "d73a4a",
                            "description": "Something isn't working",
                            "url": "https://api.github.com/repos/owner/repo/labels/bug",
                            "id": 1001,
                        }
                    ],
                },
            ],
            "pull_requests": [
                {
                    "id": 3001,
                    "number": 10,
                    "title": "Fix login endpoint",
                    "body": "Fixes authentication issue",
                    "state": "open",
                    "created_at": "2023-01-06T10:00:00Z",
                    "updated_at": "2023-01-06T10:00:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "url": "https://api.github.com/repos/owner/repo/pulls/10",
                    "html_url": "https://github.com/owner/repo/pull/10",
                    "head": {"ref": "fix-login"},
                    "base": {"ref": "main"},
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "labels": [],
                },
                {
                    "id": 3002,
                    "number": 11,
                    "title": "Add dashboard feature",
                    "body": "Implements user dashboard",
                    "state": "open",
                    "created_at": "2023-01-07T10:00:00Z",
                    "updated_at": "2023-01-07T10:00:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "url": "https://api.github.com/repos/owner/repo/pulls/11",
                    "html_url": "https://github.com/owner/repo/pull/11",
                    "head": {"ref": "add-dashboard"},
                    "base": {"ref": "main"},
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "labels": [],
                },
                {
                    "id": 3003,
                    "number": 12,
                    "title": "Performance improvements",
                    "body": "Database query optimization",
                    "state": "merged",
                    "created_at": "2023-01-08T10:00:00Z",
                    "updated_at": "2023-01-08T12:00:00Z",
                    "closed_at": "2023-01-08T12:00:00Z",
                    "merged_at": "2023-01-08T12:00:00Z",
                    "url": "https://api.github.com/repos/owner/repo/pulls/12",
                    "html_url": "https://github.com/owner/repo/pull/12",
                    "head": {"ref": "perf-improvements"},
                    "base": {"ref": "main"},
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "labels": [],
                },
            ],
            "comments": [
                {
                    "id": 4001,
                    "body": "This is a critical bug",
                    "created_at": "2023-01-01T11:00:00Z",
                    "updated_at": "2023-01-01T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/issues/comments/4001"
                    ),
                    "html_url": "https://github.com/owner/repo/issues/1#issuecomment-4001",
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                },
                {
                    "id": 4002,
                    "body": "I can reproduce this issue",
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/issues/comments/4002"
                    ),
                    "html_url": "https://github.com/owner/repo/issues/1#issuecomment-4002",
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                },
                {
                    "id": 4003,
                    "body": "Great idea for the dashboard",
                    "created_at": "2023-01-02T11:00:00Z",
                    "updated_at": "2023-01-02T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/issues/comments/4003"
                    ),
                    "html_url": "https://github.com/owner/repo/issues/2#issuecomment-4003",
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/2",
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                },
                {
                    "id": 4004,
                    "body": "Performance looks good now",
                    "created_at": "2023-01-03T11:00:00Z",
                    "updated_at": "2023-01-03T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/issues/comments/4004"
                    ),
                    "html_url": "https://github.com/owner/repo/issues/3#issuecomment-4004",
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/3",
                    "user": {
                        "login": "dave",
                        "id": 3004,
                        "avatar_url": "https://github.com/dave.png",
                        "html_url": "https://github.com/dave",
                    },
                },
                {
                    "id": 4005,
                    "body": "Documentation needs update",
                    "created_at": "2023-01-04T11:00:00Z",
                    "updated_at": "2023-01-04T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/issues/comments/4005"
                    ),
                    "html_url": "https://github.com/owner/repo/issues/4#issuecomment-4005",
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/4",
                    "user": {
                        "login": "eve",
                        "id": 3005,
                        "avatar_url": "https://github.com/eve.png",
                        "html_url": "https://github.com/eve",
                    },
                },
                {
                    "id": 4006,
                    "body": "Security is important",
                    "created_at": "2023-01-05T11:00:00Z",
                    "updated_at": "2023-01-05T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/issues/comments/4006"
                    ),
                    "html_url": "https://github.com/owner/repo/issues/5#issuecomment-4006",
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/5",
                    "user": {
                        "login": "frank",
                        "id": 3006,
                        "avatar_url": "https://github.com/frank.png",
                        "html_url": "https://github.com/frank",
                    },
                },
            ],
            "pr_comments": [
                {
                    "id": 5001,
                    "body": "Code looks good",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "created_at": "2023-01-06T11:00:00Z",
                    "updated_at": "2023-01-06T11:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/pull/10#issuecomment-5001"
                    ),
                    "pull_request_url": (
                        "https://api.github.com/repos/owner/repo/pulls/10"
                    ),
                },
                {
                    "id": 5002,
                    "body": "Nice dashboard implementation",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "created_at": "2023-01-07T11:00:00Z",
                    "updated_at": "2023-01-07T11:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/pull/11#issuecomment-5002"
                    ),
                    "pull_request_url": (
                        "https://api.github.com/repos/owner/repo/pulls/11"
                    ),
                },
                {
                    "id": 5003,
                    "body": "Performance improvements look solid",
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "created_at": "2023-01-08T11:00:00Z",
                    "updated_at": "2023-01-08T11:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/pull/12#issuecomment-5003"
                    ),
                    "pull_request_url": (
                        "https://api.github.com/repos/owner/repo/pulls/12"
                    ),
                },
            ],
        }

    @pytest.fixture
    def mock_github_service(self, sample_github_data):
        """Mock GitHub service with sample data."""
        github_service = Mock()
        github_service.get_repository_labels.return_value = sample_github_data["labels"]
        github_service.get_repository_issues.return_value = sample_github_data["issues"]
        github_service.get_repository_pull_requests.return_value = sample_github_data[
            "pull_requests"
        ]
        github_service.get_all_issue_comments.return_value = sample_github_data[
            "comments"
        ]
        github_service.get_all_pull_request_comments.return_value = sample_github_data[
            "pr_comments"
        ]

        # Add PR-specific methods
        add_pr_method_mocks(github_service, sample_github_data)

        return github_service

    @pytest.fixture
    def storage_service(self, tmp_path):
        """Create real storage service for integration testing."""
        return create_storage_service()

    def test_save_single_issue_with_comments(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test saving a single issue and its comments."""
        # Configure to save only issue #5 with comments
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={5},  # Only issue #5
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Execute save operation
        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify only issue #5 was saved
        issues_file = tmp_path / "issues.json"
        assert issues_file.exists()
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 1
        assert saved_issues[0]["number"] == 5
        assert saved_issues[0]["title"] == "Security review"

        # Verify only comments for issue #5 were saved
        comments_file = tmp_path / "comments.json"
        assert comments_file.exists()
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        assert len(saved_comments) == 1
        assert (
            saved_comments[0]["issue_url"]
            == "https://api.github.com/repos/owner/repo/issues/5"
        )
        assert saved_comments[0]["body"] == "Security is important"

    def test_save_issue_range_without_comments(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test saving issue range without comments."""
        # Configure to save issues #1-3 without comments
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={1, 2, 3},  # Issues #1, #2, #3
            include_issue_comments=False,
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Execute save operation
        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify issues #1-3 were saved
        issues_file = tmp_path / "issues.json"
        assert issues_file.exists()
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 3
        issue_numbers = {issue["number"] for issue in saved_issues}
        assert issue_numbers == {1, 2, 3}

        # Verify no comments were saved
        comments_file = tmp_path / "comments.json"
        assert not comments_file.exists()

    def test_save_mixed_specification(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test combined issue and PR selection."""
        # Configure to save issues #1-3 and PRs #10-12
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={1, 2, 3},  # Issues #1, #2, #3
            include_issue_comments=True,
            include_pull_requests={10, 11, 12},  # PRs #10, #11, #12
            include_pull_request_comments=True,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Execute save operation
        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify correct issues were saved
        issues_file = tmp_path / "issues.json"
        assert issues_file.exists()
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 3
        issue_numbers = {issue["number"] for issue in saved_issues}
        assert issue_numbers == {1, 2, 3}

        # Verify correct PRs were saved
        prs_file = tmp_path / "pull_requests.json"
        assert prs_file.exists()
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)

        assert len(saved_prs) == 3
        pr_numbers = {pr["number"] for pr in saved_prs}
        assert pr_numbers == {10, 11, 12}

        # Verify proper comment coupling
        comments_file = tmp_path / "comments.json"
        assert comments_file.exists()
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        # Should have comments for issues #1, #2, #3 (2 + 1 + 1 = 4 comments)
        assert len(saved_comments) == 4
        comment_issue_urls = {comment["issue_url"] for comment in saved_comments}
        expected_urls = {
            "https://api.github.com/repos/owner/repo/issues/1",
            "https://api.github.com/repos/owner/repo/issues/2",
            "https://api.github.com/repos/owner/repo/issues/3",
        }
        assert comment_issue_urls == expected_urls

        # Verify PR comments coupling
        pr_comments_file = tmp_path / "pr_comments.json"
        assert pr_comments_file.exists()
        with open(pr_comments_file, "r") as f:
            saved_pr_comments = json.load(f)

        # Should have comments for PRs #10, #11, #12
        assert len(saved_pr_comments) == 3
        pr_comment_urls = {comment["pull_request_url"] for comment in saved_pr_comments}
        expected_pr_urls = {
            "https://api.github.com/repos/owner/repo/pulls/10",
            "https://api.github.com/repos/owner/repo/pulls/11",
            "https://api.github.com/repos/owner/repo/pulls/12",
        }
        assert pr_comment_urls == expected_pr_urls

    def test_restore_selective_issues_from_full_backup(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test restoring specific issues from complete backup."""
        # First save all issues and comments
        save_config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=True,  # All issues
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            save_config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Now restore only issues #2, #4, #5
        restore_config = ApplicationConfig(
            operation="restore",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={2, 4, 5},  # Only these issues
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Mock GitHub API for restore operation
        mock_github_service.create_issue.side_effect = [
            {"number": 102, "title": "Add user dashboard"},
            {"number": 104, "title": "Update documentation"},
            {"number": 105, "title": "Security review"},
        ]
        mock_github_service.create_issue_comment.return_value = {"id": 9001}

        # Execute restore operation
        restore_repository_data_with_config(
            restore_config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify only specified issues were restored
        assert mock_github_service.create_issue.call_count == 3

        # Get the call arguments to verify the correct issues were restored
        issue_calls = mock_github_service.create_issue.call_args_list
        restored_titles = [
            call[0][1] for call in issue_calls
        ]  # Extract title from args
        expected_titles = [
            "Add user dashboard",
            "Update documentation",
            "Security review",
        ]
        assert set(restored_titles) == set(expected_titles)

        # Verify only comments for restored issues were restored
        assert mock_github_service.create_issue_comment.call_count == 3

    def test_restore_missing_issue_numbers(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test restore behavior when specified numbers don't exist."""
        # First save only issues #1-3
        save_config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={1, 2, 3},  # Only issues #1-3
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            save_config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Now try to restore issues #2, #7, #9 (7 and 9 don't exist in backup)
        restore_config = ApplicationConfig(
            operation="restore",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={2, 7, 9},  # 7 and 9 don't exist
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Mock GitHub API for restore operation
        mock_github_service.create_issue.return_value = {
            "number": 102,
            "title": "Add user dashboard",
        }
        mock_github_service.create_issue_comment.return_value = {"id": 9001}

        # Execute restore operation
        restore_repository_data_with_config(
            restore_config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify only issue #2 was restored (since #7 and #9 don't exist)
        assert mock_github_service.create_issue.call_count == 1

        # Verify only comment for issue #2 was restored
        assert mock_github_service.create_issue_comment.call_count == 1

    def test_comment_coupling_selective_save(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test that comments are only saved for selected issues."""
        # Configure to save only issues #2 and #4 with comments
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={2, 4},  # Only issues #2 and #4
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Execute save operation
        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify only comments from issues #2 and #4 are saved
        comments_file = tmp_path / "comments.json"
        assert comments_file.exists()
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        assert len(saved_comments) == 2
        comment_issue_urls = {comment["issue_url"] for comment in saved_comments}
        expected_urls = {
            "https://api.github.com/repos/owner/repo/issues/2",
            "https://api.github.com/repos/owner/repo/issues/4",
        }
        assert comment_issue_urls == expected_urls

    def test_selective_save_performance(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test that selective operations process less data."""
        # Configure to save only issues #1-2
        selective_config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path / "selective"),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={1, 2},  # Only 2 issues
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Execute selective save
        save_repository_data_with_config(
            selective_config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path / "selective"),
        )

        # Configure to save all issues
        full_config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path / "full"),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=True,  # All issues
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Execute full save
        save_repository_data_with_config(
            full_config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path / "full"),
        )

        # Verify selective save processed significantly less data
        selective_issues_file = tmp_path / "selective" / "issues.json"
        full_issues_file = tmp_path / "full" / "issues.json"

        with open(selective_issues_file, "r") as f:
            selective_issues = json.load(f)
        with open(full_issues_file, "r") as f:
            full_issues = json.load(f)

        assert len(selective_issues) == 2
        assert len(full_issues) == 5

        # Verify selective comments are fewer
        selective_comments_file = tmp_path / "selective" / "comments.json"
        full_comments_file = tmp_path / "full" / "comments.json"

        with open(selective_comments_file, "r") as f:
            selective_comments = json.load(f)
        with open(full_comments_file, "r") as f:
            full_comments = json.load(f)

        assert len(selective_comments) == 3
        assert len(full_comments) == 6
