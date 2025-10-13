"""Integration tests for selective issue/PR save/restore workflows."""

import json
from unittest.mock import Mock

import pytest

from src.operations.save.save import save_repository_data_with_config
from src.operations.restore.restore import restore_repository_data_with_config
from src.storage import create_storage_service
from tests.shared import (
    add_pr_method_mocks,
)
from tests.shared.builders.config_builder import ConfigBuilder

pytestmark = [pytest.mark.integration, pytest.mark.medium]


class TestSelectiveSaveRestore:
    """Integration tests for selective issue/PR save/restore workflows."""

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
        self, mock_github_service, storage_service, tmp_path, sample_github_data
    ):
        """Test saving a single issue and its comments."""
        # Configure to save only issue #1 with comments
        config = (
            ConfigBuilder()
            .with_operation("save")
            .with_token("test_token")
            .with_repo("owner/repo")
            .with_data_path(str(tmp_path))
            .with_label_strategy("skip")
            .with_git_repo(False)
            .with_issues({1})  # Only issue #1
            .with_issue_comments(True)
            .with_pull_requests(False)
            .with_pull_request_comments(False)
            .with_pr_reviews(False)
            .with_pr_review_comments(False)
            .with_sub_issues(False)
            .with_git_auth_method("token")
            .build()
        )

        # Execute save operation
        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify only issue #1 was saved
        issues_file = tmp_path / "issues.json"
        assert issues_file.exists()
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 1
        assert saved_issues[0]["number"] == 1
        assert saved_issues[0]["title"] == "Fix authentication bug"

        # Verify only comments for issue #1 were saved
        comments_file = tmp_path / "comments.json"
        assert comments_file.exists()
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        assert len(saved_comments) == 1
        assert (
            saved_comments[0]["issue_url"]
            == "https://api.github.com/repos/owner/repo/issues/1"
        )
        assert saved_comments[0]["body"] == "I can reproduce this issue"

    def test_save_issue_range_without_comments(
        self, mock_github_service, storage_service, tmp_path, sample_github_data
    ):
        """Test saving issue range without comments."""
        # Configure to save issues #1-2 without comments
        config = (
            ConfigBuilder()
            .with_operation("save")
            .with_token("test_token")
            .with_repo("owner/repo")
            .with_data_path(str(tmp_path))
            .with_label_strategy("skip")
            .with_git_repo(False)
            .with_issues({1, 2})  # Issues #1, #2
            .with_issue_comments(False)
            .with_pull_requests(False)
            .with_pull_request_comments(False)
            .with_pr_reviews(False)
            .with_pr_review_comments(False)
            .with_sub_issues(False)
            .with_git_auth_method("token")
            .build()
        )

        # Execute save operation
        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify issues #1-2 were saved
        issues_file = tmp_path / "issues.json"
        assert issues_file.exists()
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 2
        issue_numbers = {issue["number"] for issue in saved_issues}
        assert issue_numbers == {1, 2}

        # Verify no comments were saved
        comments_file = tmp_path / "comments.json"
        assert not comments_file.exists()

    def test_save_mixed_specification(
        self, mock_github_service, storage_service, tmp_path, sample_github_data
    ):
        """Test combined issue and PR selection."""
        # Configure to save issues #1-2 and PRs #3-4
        config = (
            ConfigBuilder()
            .with_operation("save")
            .with_token("test_token")
            .with_repo("owner/repo")
            .with_data_path(str(tmp_path))
            .with_label_strategy("skip")
            .with_git_repo(False)
            .with_issues({1, 2})  # Issues #1, #2
            .with_issue_comments(True)
            .with_pull_requests({3, 4})  # PRs #3, #4
            .with_pull_request_comments(True)
            .with_pr_reviews(False)
            .with_pr_review_comments(False)
            .with_sub_issues(False)
            .with_git_auth_method("token")
            .build()
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

        assert len(saved_issues) == 2
        issue_numbers = {issue["number"] for issue in saved_issues}
        assert issue_numbers == {1, 2}

        # Verify correct PRs were saved
        prs_file = tmp_path / "pull_requests.json"
        assert prs_file.exists()
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)

        assert len(saved_prs) == 2
        pr_numbers = {pr["number"] for pr in saved_prs}
        assert pr_numbers == {3, 4}

        # Verify proper comment coupling
        comments_file = tmp_path / "comments.json"
        assert comments_file.exists()
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        # Should have comments for issues #1, #2 (1 + 1 = 2 comments)
        assert len(saved_comments) == 2
        comment_issue_urls = {comment["issue_url"] for comment in saved_comments}
        expected_urls = {
            "https://api.github.com/repos/owner/repo/issues/1",
            "https://api.github.com/repos/owner/repo/issues/2",
        }
        assert comment_issue_urls == expected_urls

        # Verify PR comments coupling
        pr_comments_file = tmp_path / "pr_comments.json"
        assert pr_comments_file.exists()
        with open(pr_comments_file, "r") as f:
            saved_pr_comments = json.load(f)

        # Should have comments for PRs #3, #4
        assert len(saved_pr_comments) == 3  # Based on sample data: 1 + 2 comments
        pr_comment_urls = {comment["pull_request_url"] for comment in saved_pr_comments}
        expected_pr_urls = {
            "https://github.com/owner/repo/pull/3",
            "https://github.com/owner/repo/pull/4",
        }
        assert pr_comment_urls == expected_pr_urls

    def test_restore_selective_issues_from_full_backup(
        self, mock_github_service, storage_service, tmp_path, sample_github_data
    ):
        """Test restoring specific issues from complete backup."""
        # First save all issues and comments
        save_config = (
            ConfigBuilder()
            .with_operation("save")
            .with_token("test_token")
            .with_repo("owner/repo")
            .with_data_path(str(tmp_path))
            .with_label_strategy("skip")
            .with_git_repo(False)
            .with_issues(True)  # All issues
            .with_issue_comments(True)
            .with_pull_requests(False)
            .with_pull_request_comments(False)
            .with_pr_reviews(False)
            .with_pr_review_comments(False)
            .with_sub_issues(False)
            .with_git_auth_method("token")
            .build()
        )

        save_repository_data_with_config(
            save_config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Now restore only issue #2
        restore_config = (
            ConfigBuilder()
            .with_operation("restore")
            .with_token("test_token")
            .with_repo("owner/repo")
            .with_data_path(str(tmp_path))
            .with_label_strategy("skip")
            .with_git_repo(False)
            .with_issues({2})  # Only issue #2
            .with_issue_comments(True)
            .with_pull_requests(False)
            .with_pull_request_comments(False)
            .with_pr_reviews(False)
            .with_pr_review_comments(False)
            .with_sub_issues(False)
            .with_git_auth_method("token")
            .build()
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

        # Verify only issue #2 was restored
        assert mock_github_service.create_issue.call_count == 1

        # Get the call arguments to verify the correct issue was restored
        issue_calls = mock_github_service.create_issue.call_args_list
        restored_titles = [
            call[0][1] for call in issue_calls
        ]  # Extract title from args
        expected_titles = [
            "Add user dashboard",
        ]
        assert set(restored_titles) == set(expected_titles)

        # Verify only comments for issue #2 were restored
        assert mock_github_service.create_issue_comment.call_count == 1

    def test_restore_missing_issue_numbers(
        self, mock_github_service, storage_service, tmp_path, sample_github_data
    ):
        """Test restore behavior when specified numbers don't exist."""
        # First save only issues #1-2
        save_config = (
            ConfigBuilder()
            .with_operation("save")
            .with_token("test_token")
            .with_repo("owner/repo")
            .with_data_path(str(tmp_path))
            .with_label_strategy("skip")
            .with_git_repo(False)
            .with_issues({1, 2})  # Only issues #1-2
            .with_issue_comments(True)
            .with_pull_requests(False)
            .with_pull_request_comments(False)
            .with_pr_reviews(False)
            .with_pr_review_comments(False)
            .with_sub_issues(False)
            .with_git_auth_method("token")
            .build()
        )

        save_repository_data_with_config(
            save_config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Now try to restore issues #2, #7, #9 (7 and 9 don't exist in backup)
        restore_config = (
            ConfigBuilder()
            .with_operation("restore")
            .with_token("test_token")
            .with_repo("owner/repo")
            .with_data_path(str(tmp_path))
            .with_label_strategy("skip")
            .with_git_repo(False)
            .with_issues({2, 7, 9})  # 7 and 9 don't exist
            .with_issue_comments(True)
            .with_pull_requests(False)
            .with_pull_request_comments(False)
            .with_pr_reviews(False)
            .with_pr_review_comments(False)
            .with_sub_issues(False)
            .with_git_auth_method("token")
            .build()
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
        self, mock_github_service, storage_service, tmp_path, sample_github_data
    ):
        """Test that comments are only saved for selected issues."""
        # Configure to save only issues #1 and #2 with comments
        config = (
            ConfigBuilder()
            .with_operation("save")
            .with_token("test_token")
            .with_repo("owner/repo")
            .with_data_path(str(tmp_path))
            .with_label_strategy("skip")
            .with_git_repo(False)
            .with_issues({1, 2})  # Only issues #1 and #2
            .with_issue_comments(True)
            .with_pull_requests(False)
            .with_pull_request_comments(False)
            .with_pr_reviews(False)
            .with_pr_review_comments(False)
            .with_sub_issues(False)
            .with_git_auth_method("token")
            .build()
        )

        # Execute save operation
        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify only comments from issues #1 and #2 are saved
        comments_file = tmp_path / "comments.json"
        assert comments_file.exists()
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        assert len(saved_comments) == 2
        comment_issue_urls = {comment["issue_url"] for comment in saved_comments}
        expected_urls = {
            "https://api.github.com/repos/owner/repo/issues/1",
            "https://api.github.com/repos/owner/repo/issues/2",
        }
        assert comment_issue_urls == expected_urls

    def test_selective_save_performance(
        self, mock_github_service, storage_service, tmp_path, sample_github_data
    ):
        """Test that selective operations process less data."""
        # Configure to save only issue #1
        selective_config = (
            ConfigBuilder()
            .with_operation("save")
            .with_token("test_token")
            .with_repo("owner/repo")
            .with_data_path(str(tmp_path / "selective"))
            .with_label_strategy("skip")
            .with_git_repo(False)
            .with_issues({1})  # Only 1 issue
            .with_issue_comments(True)
            .with_pull_requests(False)
            .with_pull_request_comments(False)
            .with_pr_reviews(False)
            .with_pr_review_comments(False)
            .with_sub_issues(False)
            .with_git_auth_method("token")
            .build()
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
        full_config = (
            ConfigBuilder()
            .with_operation("save")
            .with_token("test_token")
            .with_repo("owner/repo")
            .with_data_path(str(tmp_path / "full"))
            .with_label_strategy("skip")
            .with_git_repo(False)
            .with_issues(True)  # All issues
            .with_issue_comments(True)
            .with_pull_requests(False)
            .with_pull_request_comments(False)
            .with_pr_reviews(False)
            .with_pr_review_comments(False)
            .with_sub_issues(False)
            .with_git_auth_method("token")
            .build()
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

        assert len(selective_issues) == 1  # Only issue #1
        assert len(full_issues) == 2      # All issues (#1, #2)

        # Verify selective comments are fewer
        selective_comments_file = tmp_path / "selective" / "comments.json"
        full_comments_file = tmp_path / "full" / "comments.json"

        with open(selective_comments_file, "r") as f:
            selective_comments = json.load(f)
        with open(full_comments_file, "r") as f:
            full_comments = json.load(f)

        assert len(selective_comments) == 1  # Only comment for issue #1
        assert len(full_comments) == 2      # All comments (1 for #1, 1 for #2)
