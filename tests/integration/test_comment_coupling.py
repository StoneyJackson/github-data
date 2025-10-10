"""Integration tests for comment coupling in selective operations."""

import json
from unittest.mock import Mock

import pytest

from src.config.settings import ApplicationConfig
from src.operations.save.save import save_repository_data_with_config
from src.operations.restore.restore import restore_repository_data_with_config
from src.storage import create_storage_service
from tests.shared import add_pr_method_mocks

pytestmark = [pytest.mark.integration, pytest.mark.medium]


class TestCommentCoupling:
    """Integration tests for automatic comment coupling to issue/PR selection."""

    @pytest.fixture
    def sample_github_data(self):
        """Sample GitHub API data with multiple issues, PRs, and comments."""
        return {
            "labels": [
                {
                    "name": "bug",
                    "color": "d73a4a",
                    "description": "Something isn't working",
                    "url": "https://api.github.com/repos/owner/repo/labels/bug",
                    "id": 1001,
                }
            ],
            "issues": [
                {
                    "id": 2001,
                    "number": 10,
                    "title": "Issue 10",
                    "body": "First issue",
                    "state": "open",
                    "state_reason": None,
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "assignees": [],
                    "created_at": "2023-01-01T10:00:00Z",
                    "updated_at": "2023-01-01T10:00:00Z",
                    "closed_at": None,
                    "html_url": "https://api.github.com/repos/owner/repo/issues/10",
                    "comments": 0,
                    "labels": [],
                },
                {
                    "id": 2002,
                    "number": 20,
                    "title": "Issue 20",
                    "body": "Second issue",
                    "state": "open",
                    "state_reason": None,
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "assignees": [],
                    "created_at": "2023-01-02T10:00:00Z",
                    "updated_at": "2023-01-02T10:00:00Z",
                    "closed_at": None,
                    "html_url": "https://api.github.com/repos/owner/repo/issues/20",
                    "comments": 0,
                    "labels": [],
                },
                {
                    "id": 2003,
                    "number": 30,
                    "title": "Issue 30",
                    "body": "Third issue",
                    "state": "open",
                    "state_reason": None,
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "assignees": [],
                    "created_at": "2023-01-03T10:00:00Z",
                    "updated_at": "2023-01-03T10:00:00Z",
                    "closed_at": None,
                    "html_url": "https://api.github.com/repos/owner/repo/issues/30",
                    "comments": 0,
                    "labels": [],
                },
            ],
            "pull_requests": [
                {
                    "id": 3001,
                    "number": 100,
                    "title": "PR 100",
                    "body": "First PR",
                    "state": "open",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "assignees": [],
                    "created_at": "2023-01-04T10:00:00Z",
                    "updated_at": "2023-01-04T10:00:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "html_url": "https://github.com/owner/repo/pulls/100",
                    "comments": 0,
                    "head_ref": "feature-100",
                    "base_ref": "main",
                    "labels": [],
                },
                {
                    "id": 3002,
                    "number": 200,
                    "title": "PR 200",
                    "body": "Second PR",
                    "state": "open",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "assignees": [],
                    "created_at": "2023-01-05T10:00:00Z",
                    "updated_at": "2023-01-05T10:00:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "html_url": "https://github.com/owner/repo/pulls/200",
                    "comments": 0,
                    "head_ref": "feature-200",
                    "base_ref": "main",
                    "labels": [],
                },
                {
                    "id": 3003,
                    "number": 300,
                    "title": "PR 300",
                    "body": "Third PR",
                    "state": "open",
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "assignees": [],
                    "created_at": "2023-01-06T10:00:00Z",
                    "updated_at": "2023-01-06T10:00:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "html_url": "https://github.com/owner/repo/pulls/300",
                    "comments": 0,
                    "head_ref": "feature-300",
                    "base_ref": "main",
                    "labels": [],
                },
            ],
            "comments": [
                # Comments for issue 10
                {
                    "id": 4001,
                    "body": "Comment 1 on issue 10",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "created_at": "2023-01-01T11:00:00Z",
                    "updated_at": "2023-01-01T11:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/10#issuecomment-4001"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/10",
                },
                {
                    "id": 4002,
                    "body": "Comment 2 on issue 10",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/10#issuecomment-4002"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/10",
                },
                # Comments for issue 20
                {
                    "id": 4003,
                    "body": "Comment 1 on issue 20",
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "created_at": "2023-01-02T11:00:00Z",
                    "updated_at": "2023-01-02T11:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/20#issuecomment-4003"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/20",
                },
                {
                    "id": 4004,
                    "body": "Comment 2 on issue 20",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "created_at": "2023-01-02T12:00:00Z",
                    "updated_at": "2023-01-02T12:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/20#issuecomment-4004"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/20",
                },
                # Comments for issue 30
                {
                    "id": 4005,
                    "body": "Comment 1 on issue 30",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "created_at": "2023-01-03T11:00:00Z",
                    "updated_at": "2023-01-03T11:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/30#issuecomment-4005"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/30",
                },
                {
                    "id": 4006,
                    "body": "Comment 2 on issue 30",
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "created_at": "2023-01-03T12:00:00Z",
                    "updated_at": "2023-01-03T12:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/30#issuecomment-4006"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/30",
                },
            ],
            "pr_comments": [
                # Comments for PR 100
                {
                    "id": 5001,
                    "body": "Comment 1 on PR 100",
                    "created_at": "2023-01-04T11:00:00Z",
                    "updated_at": "2023-01-04T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/pulls/comments/5001"
                    ),
                    "pull_request_url": (
                        "https://api.github.com/repos/owner/repo/pulls/100"
                    ),
                    "pull_request_number": 100,
                },
                {
                    "id": 5002,
                    "body": "Comment 2 on PR 100",
                    "created_at": "2023-01-04T12:00:00Z",
                    "updated_at": "2023-01-04T12:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/pulls/comments/5002"
                    ),
                    "pull_request_url": (
                        "https://api.github.com/repos/owner/repo/pulls/100"
                    ),
                    "pull_request_number": 100,
                },
                # Comments for PR 200
                {
                    "id": 5003,
                    "body": "Comment 1 on PR 200",
                    "created_at": "2023-01-05T11:00:00Z",
                    "updated_at": "2023-01-05T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/pulls/comments/5003"
                    ),
                    "pull_request_url": (
                        "https://api.github.com/repos/owner/repo/pulls/200"
                    ),
                    "pull_request_number": 200,
                },
                {
                    "id": 5004,
                    "body": "Comment 1 on PR 300",
                    "created_at": "2023-01-06T11:00:00Z",
                    "updated_at": "2023-01-06T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/pulls/comments/5004"
                    ),
                    "pull_request_url": (
                        "https://api.github.com/repos/owner/repo/pulls/300"
                    ),
                    "pull_request_number": 300,
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
        add_pr_method_mocks(github_service)

        return github_service

    @pytest.fixture
    def storage_service(self):
        """Create real storage service for integration testing."""
        return create_storage_service()

    def test_issue_comments_follow_issue_selection(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Verify issue comments are automatically coupled to issue selection."""
        # Configure to save only issue #20 with comments enabled
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={20},  # Only issue #20
            include_issue_comments=True,  # Comments enabled
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

        # Verify only issue #20 was saved
        issues_file = tmp_path / "issues.json"
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 1
        assert saved_issues[0]["number"] == 20

        # Verify only comments for issue #20 were saved (should be 2 comments)
        comments_file = tmp_path / "comments.json"
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        assert len(saved_comments) == 2
        for comment in saved_comments:
            assert (
                comment["issue_url"]
                == "https://api.github.com/repos/owner/repo/issues/20"
            )

        comment_bodies = {comment["body"] for comment in saved_comments}
        expected_bodies = {"Comment 1 on issue 20", "Comment 2 on issue 20"}
        assert comment_bodies == expected_bodies

    def test_issue_comments_disabled_overrides_selection(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Verify INCLUDE_ISSUE_COMMENTS=false disables comments regardless of issue
        selection.
        """
        # Configure to save issue #10 but with comments disabled
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={10},  # Issue #10 selected
            include_issue_comments=False,  # Comments explicitly disabled
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

        # Verify issue #10 was saved
        issues_file = tmp_path / "issues.json"
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 1
        assert saved_issues[0]["number"] == 10

        # Verify no comments were saved despite issue selection
        comments_file = tmp_path / "comments.json"
        assert not comments_file.exists()

    def test_pr_comments_follow_pr_selection(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Verify PR comments are automatically coupled to PR selection."""
        # Configure to save only PR #100 with comments enabled
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=False,
            include_issue_comments=False,
            include_pull_requests={100},  # Only PR #100
            include_pull_request_comments=True,  # Comments enabled
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

        # Verify only PR #100 was saved
        prs_file = tmp_path / "pull_requests.json"
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)

        assert len(saved_prs) == 1
        assert saved_prs[0]["number"] == 100

        # Verify only comments for PR #100 were saved (should be 2 comments)
        pr_comments_file = tmp_path / "pr_comments.json"
        with open(pr_comments_file, "r") as f:
            saved_pr_comments = json.load(f)

        assert len(saved_pr_comments) == 2
        for comment in saved_pr_comments:
            assert (
                comment["pull_request_url"]
                == "https://api.github.com/repos/owner/repo/pulls/100"
            )

        comment_bodies = {comment["body"] for comment in saved_pr_comments}
        expected_bodies = {"Comment 1 on PR 100", "Comment 2 on PR 100"}
        assert comment_bodies == expected_bodies

    def test_pr_comments_disabled_overrides_selection(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Verify INCLUDE_PULL_REQUEST_COMMENTS=false disables comments regardless of
        PR selection.
        """
        # Configure to save PR #200 but with comments disabled
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=False,
            include_issue_comments=False,
            include_pull_requests={200},  # PR #200 selected
            include_pull_request_comments=False,  # Comments explicitly disabled
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

        # Verify PR #200 was saved
        prs_file = tmp_path / "pull_requests.json"
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)

        assert len(saved_prs) == 1
        assert saved_prs[0]["number"] == 200

        # Verify no PR comments were saved despite PR selection
        pr_comments_file = tmp_path / "pr_comments.json"
        assert not pr_comments_file.exists()

    def test_comment_coupling_selective_restore(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test that comments are only restored for restored issues."""
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

        # Now restore only issues #10 and #30
        restore_config = ApplicationConfig(
            operation="restore",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={10, 30},  # Only these issues
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Mock GitHub API for restore operation
        mock_github_service.create_issue.side_effect = [
            {
                "number": 110,
                "title": "Issue 10",
            },  # Maps original issue 10 to new issue 110
            {
                "number": 130,
                "title": "Issue 30",
            },  # Maps original issue 30 to new issue 130
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

        # Verify only issues #10 and #30 were restored
        assert mock_github_service.create_issue.call_count == 2

        # Verify only comments for issues #10 and #30 were restored (4 comments total)
        assert mock_github_service.create_issue_comment.call_count == 4

        # Verify the comments were created for the correct new issue numbers
        comment_calls = mock_github_service.create_issue_comment.call_args_list
        created_issue_numbers = [
            call[0][1] for call in comment_calls
        ]  # Extract issue number from args

        # Should have 2 comments for issue 110 (mapped from 10) and 2 comments for
        # issue 130 (mapped from 30)
        assert created_issue_numbers.count(110) == 2
        assert created_issue_numbers.count(130) == 2

    def test_mixed_comment_coupling(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test comment coupling with both issues and PRs selected."""
        # Configure to save mixed selection: issue #20, PR #200, with both comment
        # types enabled
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={20},  # Only issue #20
            include_issue_comments=True,
            include_pull_requests={200},  # Only PR #200
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

        # Verify issue #20 was saved
        issues_file = tmp_path / "issues.json"
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 1
        assert saved_issues[0]["number"] == 20

        # Verify PR #200 was saved
        prs_file = tmp_path / "pull_requests.json"
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)

        assert len(saved_prs) == 1
        assert saved_prs[0]["number"] == 200

        # Verify only comments for issue #20 were saved
        comments_file = tmp_path / "comments.json"
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        assert len(saved_comments) == 2
        for comment in saved_comments:
            assert (
                comment["issue_url"]
                == "https://api.github.com/repos/owner/repo/issues/20"
            )

        # Verify only comments for PR #200 were saved
        pr_comments_file = tmp_path / "pr_comments.json"
        with open(pr_comments_file, "r") as f:
            saved_pr_comments = json.load(f)

        assert len(saved_pr_comments) == 1
        assert (
            saved_pr_comments[0]["pull_request_url"]
            == "https://api.github.com/repos/owner/repo/pulls/200"
        )

    def test_no_issues_selected_skips_all_comments(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test that no comments are saved when no issues are selected."""
        # Configure to save no issues but with comments enabled
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=False,  # No issues selected
            include_issue_comments=True,  # Comments enabled but should be ignored
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

        # Verify no issues were saved
        issues_file = tmp_path / "issues.json"
        assert not issues_file.exists()

        # Verify no comments were saved despite being enabled
        comments_file = tmp_path / "comments.json"
        assert not comments_file.exists()

    def test_no_prs_selected_skips_all_pr_comments(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test that no PR comments are saved when no PRs are selected."""
        # Configure to save no PRs but with PR comments enabled
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=False,
            include_issue_comments=False,
            include_pull_requests=False,  # No PRs selected
            include_pull_request_comments=True,  # PR comments enabled but should be
            # ignored
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

        # Verify no PRs were saved
        prs_file = tmp_path / "pull_requests.json"
        assert not prs_file.exists()

        # Verify no PR comments were saved despite being enabled
        pr_comments_file = tmp_path / "pr_comments.json"
        assert not pr_comments_file.exists()
