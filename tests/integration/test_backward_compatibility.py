"""Comprehensive backward compatibility tests for selective issue/PR numbers feature.

This test suite ensures that existing boolean behavior (Phase 1) is preserved
exactly as before when using the new selective features.
"""

import json
import logging
from unittest.mock import Mock, patch

import pytest

from src.config.settings import ApplicationConfig
from src.operations.save.save import save_repository_data_with_config
from src.operations.restore.restore import restore_repository_data_with_config
from src.storage import create_storage_service
from tests.shared import add_pr_method_mocks

pytestmark = [
    pytest.mark.integration,
    pytest.mark.medium,
    pytest.mark.backward_compatibility,
]


class TestBackwardCompatibility:
    """Ensure existing workflows continue to work exactly as before."""

    @pytest.fixture
    def sample_github_data(self):
        """Sample GitHub API data for backward compatibility testing."""
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
                    "url": "https://api.github.com/repos/owner/repo/issues/1",
                    "html_url": "https://github.com/owner/repo/issues/1",
                    "comments": 0,
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
                    "url": "https://api.github.com/repos/owner/repo/issues/2",
                    "html_url": "https://github.com/owner/repo/issues/2",
                    "comments": 0,
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
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "assignees": [],
                    "created_at": "2023-01-03T10:00:00Z",
                    "updated_at": "2023-01-03T12:00:00Z",
                    "closed_at": "2023-01-03T12:00:00Z",
                    "url": "https://api.github.com/repos/owner/repo/issues/3",
                    "html_url": "https://github.com/owner/repo/issues/3",
                    "comments": 0,
                    "labels": [],
                },
            ],
            "pull_requests": [
                {
                    "id": 3001,
                    "number": 10,
                    "title": "Fix login endpoint",
                    "body": "Fixes authentication issue",
                    "state": "open",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "assignees": [],
                    "created_at": "2023-01-06T10:00:00Z",
                    "updated_at": "2023-01-06T10:00:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "url": "https://api.github.com/repos/owner/repo/pulls/10",
                    "html_url": "https://github.com/owner/repo/pulls/10",
                    "comments": 0,
                    "head": {"ref": "fix-login"},
                    "base": {"ref": "main"},
                    "labels": [],
                },
                {
                    "id": 3002,
                    "number": 11,
                    "title": "Add dashboard feature",
                    "body": "Implements user dashboard",
                    "state": "open",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "assignees": [],
                    "created_at": "2023-01-07T10:00:00Z",
                    "updated_at": "2023-01-07T10:00:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "url": "https://api.github.com/repos/owner/repo/pulls/11",
                    "html_url": "https://github.com/owner/repo/pulls/11",
                    "comments": 0,
                    "head": {"ref": "add-dashboard"},
                    "base": {"ref": "main"},
                    "labels": [],
                },
            ],
            "comments": [
                {
                    "id": 4001,
                    "body": "This is a critical bug",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "created_at": "2023-01-01T11:00:00Z",
                    "updated_at": "2023-01-01T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/issues/comments/4001"
                    ),
                    "html_url": (
                        "https://github.com/owner/repo/issues/1#issuecomment-4001"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                },
                {
                    "id": 4002,
                    "body": "I can reproduce this issue",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/issues/comments/4002"
                    ),
                    "html_url": (
                        "https://github.com/owner/repo/issues/1#issuecomment-4002"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                },
                {
                    "id": 4003,
                    "body": "Great idea for the dashboard",
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "created_at": "2023-01-02T11:00:00Z",
                    "updated_at": "2023-01-02T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/issues/comments/4003"
                    ),
                    "html_url": (
                        "https://github.com/owner/repo/issues/2#issuecomment-4003"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/2",
                },
            ],
            "pr_comments": [
                {
                    "id": 5001,
                    "body": "Code looks good",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "created_at": "2023-01-06T11:00:00Z",
                    "updated_at": "2023-01-06T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/pulls/comments/5001"
                    ),
                    "html_url": (
                        "https://github.com/owner/repo/pulls/10#issuecomment-5001"
                    ),
                    "pull_request_url": (
                        "https://api.github.com/repos/owner/repo/pulls/10"
                    ),
                    "pull_request_number": 10,
                },
                {
                    "id": 5002,
                    "body": "Nice dashboard implementation",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "created_at": "2023-01-07T11:00:00Z",
                    "updated_at": "2023-01-07T11:00:00Z",
                    "url": (
                        "https://api.github.com/repos/owner/repo/pulls/comments/5002"
                    ),
                    "html_url": (
                        "https://github.com/owner/repo/pulls/11#issuecomment-5002"
                    ),
                    "pull_request_url": (
                        "https://api.github.com/repos/owner/repo/pulls/11"
                    ),
                    "pull_request_number": 11,
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
    def storage_service(self):
        """Create real storage service for integration testing."""
        return create_storage_service()

    def test_boolean_true_preserves_original_behavior(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test include_issues=True works exactly as Phase 1."""
        # Configure exactly as Phase 1 would: boolean True for issues
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=True,  # Boolean True (Phase 1 behavior)
            include_issue_comments=True,
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_pr_reviews=False,
            include_pr_review_comments=False,
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

        # Verify ALL issues are saved (Phase 1 behavior)
        issues_file = tmp_path / "issues.json"
        assert issues_file.exists()
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 3  # All issues saved
        issue_numbers = {issue["number"] for issue in saved_issues}
        assert issue_numbers == {1, 2, 3}

        # Verify ALL issue comments are saved (Phase 1 behavior)
        comments_file = tmp_path / "comments.json"
        assert comments_file.exists()
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        assert len(saved_comments) == 3  # All comments saved

    def test_boolean_false_preserves_original_behavior(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test include_issues=False works exactly as Phase 1."""
        # Configure exactly as Phase 1 would: boolean False for issues
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=False,  # Boolean False (Phase 1 behavior)
            include_issue_comments=True,  # Should be ignored with warning
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Expect warning about issue comments being ignored
        with patch("src.config.settings.logging.warning") as mock_warning:
            config.validate()
            mock_warning.assert_called_once()
            assert "INCLUDE_ISSUE_COMMENTS=true requires INCLUDE_ISSUES=true" in str(
                mock_warning.call_args
            )

        # Execute save operation
        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify NO issues are saved (Phase 1 behavior)
        issues_file = tmp_path / "issues.json"
        assert not issues_file.exists()

        # Verify NO comments are saved (Phase 1 behavior with warning)
        comments_file = tmp_path / "comments.json"
        assert not comments_file.exists()

    def test_pr_boolean_behavior_unchanged(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test PR boolean operations unchanged."""
        # Test True case
        config_true = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path / "true"),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=False,
            include_issue_comments=False,
            include_pull_requests=True,  # Boolean True (Phase 1 behavior)
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            config_true,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path / "true"),
        )

        # Verify ALL PRs are saved
        prs_file = tmp_path / "true" / "pull_requests.json"
        assert prs_file.exists()
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)

        assert len(saved_prs) == 2  # All PRs saved
        pr_numbers = {pr["number"] for pr in saved_prs}
        assert pr_numbers == {10, 11}

        # Verify ALL PR comments are saved
        pr_comments_file = tmp_path / "true" / "pr_comments.json"
        assert pr_comments_file.exists()
        with open(pr_comments_file, "r") as f:
            saved_pr_comments = json.load(f)

        assert len(saved_pr_comments) == 2  # All PR comments saved

        # Test False case
        config_false = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path / "false"),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=False,
            include_issue_comments=False,
            include_pull_requests=False,  # Boolean False (Phase 1 behavior)
            include_pull_request_comments=True,  # Should be ignored with warning
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Expect warning about PR comments being ignored
        with patch("src.config.settings.logging.warning") as mock_warning:
            config_false.validate()
            mock_warning.assert_called_once()
            assert (
                "INCLUDE_PULL_REQUEST_COMMENTS=true requires INCLUDE_PULL_REQUESTS=true"
                in str(mock_warning.call_args)
            )

        save_repository_data_with_config(
            config_false,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path / "false"),
        )

        # Verify NO PRs are saved
        prs_file = tmp_path / "false" / "pull_requests.json"
        assert not prs_file.exists()

        # Verify NO PR comments are saved
        pr_comments_file = tmp_path / "false" / "pr_comments.json"
        assert not pr_comments_file.exists()

    def test_comment_coupling_backward_compatible(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Verify comment coupling doesn't break existing behavior."""
        # Test that boolean True still includes ALL comments as before
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=True,  # Boolean True
            include_issue_comments=True,  # Boolean True
            include_pull_requests=True,  # Boolean True
            include_pull_request_comments=True,  # Boolean True
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify all issues saved
        issues_file = tmp_path / "issues.json"
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)
        assert len(saved_issues) == 3

        # Verify all PRs saved
        prs_file = tmp_path / "pull_requests.json"
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)
        assert len(saved_prs) == 2

        # Verify all issue comments saved (Phase 1 behavior preserved)
        comments_file = tmp_path / "comments.json"
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)
        assert len(saved_comments) == 3  # All issue comments

        # Verify all PR comments saved (Phase 1 behavior preserved)
        pr_comments_file = tmp_path / "pr_comments.json"
        with open(pr_comments_file, "r") as f:
            saved_pr_comments = json.load(f)
        assert len(saved_pr_comments) == 2  # All PR comments

    def test_mixed_boolean_selective_scenarios(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test mixing boolean and selective configurations."""
        # Test boolean True for issues, selective for PRs
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=True,  # Boolean True (all issues)
            include_issue_comments=True,
            include_pull_requests={10},  # Selective (only PR 10)
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify ALL issues saved (boolean behavior preserved)
        issues_file = tmp_path / "issues.json"
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)
        assert len(saved_issues) == 3
        issue_numbers = {issue["number"] for issue in saved_issues}
        assert issue_numbers == {1, 2, 3}

        # Verify only PR 10 saved (selective behavior)
        prs_file = tmp_path / "pull_requests.json"
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)
        assert len(saved_prs) == 1
        assert saved_prs[0]["number"] == 10

        # Verify ALL issue comments saved (boolean behavior preserved)
        comments_file = tmp_path / "comments.json"
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)
        assert len(saved_comments) == 3

        # Verify only PR 10 comments saved (selective coupling)
        pr_comments_file = tmp_path / "pr_comments.json"
        with open(pr_comments_file, "r") as f:
            saved_pr_comments = json.load(f)
        assert len(saved_pr_comments) == 1
        assert saved_pr_comments[0]["pull_request_number"] == 10

    def test_restore_boolean_behavior_preserved(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test that restore operations with boolean values work as before."""
        # First save all data using boolean True
        save_config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=True,  # Boolean True
            include_issue_comments=True,
            include_pull_requests=True,  # Boolean True
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
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

        # Now restore using boolean True (Phase 1 behavior)
        restore_config = ApplicationConfig(
            operation="restore",
            github_token="test_token",
            github_repo="owner/new-repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=True,  # Boolean True (restore all)
            include_issue_comments=True,
            include_pull_requests=True,  # Boolean True (restore all)
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Mock GitHub API for restore operation
        mock_github_service.create_issue.side_effect = [
            {"number": 101, "title": "Fix authentication bug"},
            {"number": 102, "title": "Add user dashboard"},
            {"number": 103, "title": "Performance optimization"},
        ]
        mock_github_service.create_pull_request.side_effect = [
            {"number": 110, "title": "Fix login endpoint"},
            {"number": 111, "title": "Add dashboard feature"},
        ]
        mock_github_service.create_issue_comment.return_value = {"id": 9001}
        mock_github_service.create_pull_request_comment.return_value = {"id": 9002}

        # Execute restore operation
        restore_repository_data_with_config(
            restore_config,
            mock_github_service,
            storage_service,
            "owner/new-repo",
            str(tmp_path),
        )

        # Verify ALL issues were restored (Phase 1 behavior)
        assert mock_github_service.create_issue.call_count == 3

        # Verify ALL PRs were restored (Phase 1 behavior)
        assert mock_github_service.create_pull_request.call_count == 2

        # Verify ALL issue comments were restored (Phase 1 behavior)
        assert mock_github_service.create_issue_comment.call_count == 3

        # Verify ALL PR comments were restored (Phase 1 behavior)
        assert mock_github_service.create_pull_request_comment.call_count == 2

    def test_environment_variable_parsing_backward_compatible(self):
        """Test that environment variable parsing preserves Phase 1 behavior."""
        # Test boolean environment variables work as before
        test_cases = [
            ("true", True),
            ("false", False),
            ("yes", True),
            ("no", False),
            ("on", True),
            ("off", False),
            ("TRUE", True),
            ("FALSE", False),
        ]

        for env_value, expected_result in test_cases:
            with patch.dict("os.environ", {"INCLUDE_ISSUES": env_value}, clear=False):
                config = ApplicationConfig(
                    operation="save",
                    github_token="test_token",
                    github_repo="owner/repo",
                    data_path="/data",
                    label_conflict_strategy="skip",
                    include_git_repo=False,
                    include_issues=ApplicationConfig._parse_number_or_bool_env(
                        "INCLUDE_ISSUES", False
                    ),
                    include_issue_comments=True,
                    include_pull_requests=True,
                    include_pull_request_comments=True,
                    include_pr_reviews=False,
                    include_pr_review_comments=False,
                    include_sub_issues=False,
                    git_auth_method="token",
                )

                assert config.include_issues == expected_result, (
                    f"Expected {env_value} to parse as {expected_result}, "
                    f"got {config.include_issues}"
                )

    def test_legacy_environment_variables_error_guidance(self):
        """Test that legacy "0"/"1" values provide helpful error messages."""
        # Test that legacy "0"/"1" formats provide helpful errors
        legacy_values = ["0", "1"]

        # Base environment variables required for ApplicationConfig
        base_env = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPO": "owner/repo",
            "DATA_PATH": "/data",
        }

        for legacy_value in legacy_values:
            test_env = {**base_env, "INCLUDE_ISSUE_COMMENTS": legacy_value}
            with patch.dict("os.environ", test_env, clear=True):
                with pytest.raises(ValueError) as exc_info:
                    ApplicationConfig.from_environment()

                error_message = str(exc_info.value)
                assert "legacy format" in error_message
                assert "enhanced boolean formats" in error_message
                assert "true/false, yes/no, or on/off" in error_message

    def test_validation_warnings_preserved(self, caplog):
        """Test that validation warnings for comment dependencies are preserved."""
        # Test issue comments warning
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path="/data",
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=False,  # Boolean False
            include_issue_comments=True,  # Should trigger warning
            include_pull_requests=False,
            include_pull_request_comments=False,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        with caplog.at_level(logging.WARNING):
            config.validate()

        assert any(
            "INCLUDE_ISSUE_COMMENTS=true requires INCLUDE_ISSUES=true" in record.message
            for record in caplog.records
        )
        assert config.include_issue_comments is False  # Should be corrected

        # Test PR comments warning
        caplog.clear()
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path="/data",
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=False,
            include_issue_comments=False,
            include_pull_requests=False,  # Boolean False
            include_pull_request_comments=True,  # Should trigger warning
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        with caplog.at_level(logging.WARNING):
            config.validate()

        assert any(
            "INCLUDE_PULL_REQUEST_COMMENTS=true requires INCLUDE_PULL_REQUESTS=true"
            in record.message
            for record in caplog.records
        )
        assert config.include_pull_request_comments is False  # Should be corrected
