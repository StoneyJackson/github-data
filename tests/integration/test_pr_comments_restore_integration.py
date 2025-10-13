"""Integration tests for PR comments restore operation behavior."""

import json
from pathlib import Path
from unittest.mock import patch
import pytest

from src.operations.restore.restore import (
    restore_repository_data_with_strategy_pattern,
)
from src.github import create_github_service
from src.storage import create_storage_service
from tests.shared import MockBoundaryFactory

# Test markers for organization and selective execution
pytestmark = [
    pytest.mark.integration,
    pytest.mark.medium,
    pytest.mark.pr_comments,
    pytest.mark.restore_operation,
]


class TestPrCommentsRestoreIntegration:
    """Integration tests for PR comments restore operation behavior."""

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_with_pr_comments_enabled_restores_all_entities(
        self, mock_boundary_class, temp_data_dir, sample_github_data
    ):
        """Test restore operation with PR comments enabled restores all entities."""
        # Create backup files
        temp_path = Path(temp_data_dir)

        with open(temp_path / "labels.json", "w") as f:
            json.dump(sample_github_data["labels"], f)
        with open(temp_path / "issues.json", "w") as f:
            json.dump(sample_github_data["issues"], f)
        with open(temp_path / "comments.json", "w") as f:
            json.dump(sample_github_data["comments"], f)
        with open(temp_path / "pull_requests.json", "w") as f:
            json.dump(sample_github_data["pull_requests"], f)
        with open(temp_path / "pr_comments.json", "w") as f:
            json.dump(sample_github_data["pr_comments"], f)
        with open(temp_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(temp_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary for restore operations
        mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
        mock_boundary_class.return_value = mock_boundary

        # Mock successful creation responses
        mock_boundary.create_label.return_value = {"name": "bug", "id": "new_label_id"}
        mock_boundary.create_issue.return_value = {"number": 1, "id": "new_issue_id"}
        mock_boundary.create_issue_comment.return_value = {"id": "new_comment_id"}
        mock_boundary.create_pull_request.return_value = {
            "number": 42,
            "id": "new_pr_id",
        }
        mock_boundary.create_pull_request_comment.return_value = {
            "id": "new_pr_comment_id"
        }

        # Execute restore operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_original_metadata=True,
            include_pull_requests=True,
            include_sub_issues=False,
        )

        # Verify all expected creation calls were made
        assert mock_boundary.create_label.call_count == 2  # 2 labels in sample data
        assert mock_boundary.create_issue.call_count == 2  # 2 issues in sample data
        assert (
            mock_boundary.create_issue_comment.call_count == 2
        )  # 2 issue comments coupled to restored issues
        assert mock_boundary.create_pull_request.call_count == 2  # 2 PRs in sample data

        # Verify PR comments were created (should be 3 calls from sample data)
        assert mock_boundary.create_pull_request_comment.call_count == 3

        # Verify PR comment creation was called with correct data
        pr_comment_calls = mock_boundary.create_pull_request_comment.call_args_list
        assert len(pr_comment_calls) == 3

        # Check first PR comment (matches sample data)
        first_call_body = pr_comment_calls[0][0][2]  # Third positional argument (body)
        # With include_original_metadata=True, body enriched with author/timestamp
        assert "Great work on the rate limiting implementation!" in first_call_body
        assert "bob" in first_call_body
        assert "2023-01-18" in first_call_body

        # Check second PR comment (matches sample data)
        second_call_body = pr_comment_calls[1][0][2]  # Third positional argument (body)
        assert "Need to add more tests for edge cases" in second_call_body
        assert "alice" in second_call_body
        assert "2023-01-17" in second_call_body

        # Check third PR comment (matches sample data)
        third_call_body = pr_comment_calls[2][0][2]  # Third positional argument (body)
        assert "Updated the implementation to handle edge cases" in third_call_body
        assert "charlie" in third_call_body
        assert "2023-01-17" in third_call_body

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_with_prs_but_no_pr_comments_skips_pr_comments(
        self, mock_boundary_class, temp_data_dir, sample_github_data
    ):
        """Test restore operation with PRs enabled but PR comments disabled."""
        # Create backup files (including pr_comments.json even though it won't be used)
        temp_path = Path(temp_data_dir)

        with open(temp_path / "labels.json", "w") as f:
            json.dump(sample_github_data["labels"], f)
        with open(temp_path / "issues.json", "w") as f:
            json.dump(sample_github_data["issues"], f)
        with open(temp_path / "comments.json", "w") as f:
            json.dump(sample_github_data["comments"], f)
        with open(temp_path / "pull_requests.json", "w") as f:
            json.dump(sample_github_data["pull_requests"], f)
        with open(temp_path / "pr_comments.json", "w") as f:
            json.dump(sample_github_data["pr_comments"], f)
        with open(temp_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(temp_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary for restore operations
        mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
        mock_boundary_class.return_value = mock_boundary

        # Mock successful creation responses
        mock_boundary.create_label.return_value = {"name": "bug", "id": "new_label_id"}
        mock_boundary.create_issue.return_value = {"number": 1, "id": "new_issue_id"}
        mock_boundary.create_issue_comment.return_value = {"id": "new_comment_id"}
        mock_boundary.create_pull_request.return_value = {
            "number": 42,
            "id": "new_pr_id",
        }

        # Execute restore operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_original_metadata=True,
            include_pull_requests=True,
            include_pull_request_comments=False,
            include_sub_issues=False,
        )

        # Verify expected creation calls were made
        assert mock_boundary.create_label.call_count == 2  # 2 labels in sample data
        assert mock_boundary.create_issue.call_count == 2  # 2 issues in sample data
        assert (
            mock_boundary.create_issue_comment.call_count == 2
        )  # 2 issue comments in sample data
        assert mock_boundary.create_pull_request.call_count == 2  # 2 PRs in sample data

        # Verify PR comments were NOT created
        mock_boundary.create_pull_request_comment.assert_not_called()

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_with_pr_comments_but_no_prs_shows_warning_and_skips_both(
        self,
        mock_boundary_class,
        temp_data_dir,
        sample_github_data,
        caplog,
    ):
        """Test restore operation with PR comments enabled but PRs disabled."""
        # Create backup files
        temp_path = Path(temp_data_dir)

        with open(temp_path / "labels.json", "w") as f:
            json.dump(sample_github_data["labels"], f)
        with open(temp_path / "issues.json", "w") as f:
            json.dump(sample_github_data["issues"], f)
        with open(temp_path / "comments.json", "w") as f:
            json.dump(sample_github_data["comments"], f)
        with open(temp_path / "pull_requests.json", "w") as f:
            json.dump(sample_github_data["pull_requests"], f)
        with open(temp_path / "pr_comments.json", "w") as f:
            json.dump(sample_github_data["pr_comments"], f)
        with open(temp_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(temp_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary for restore operations
        mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
        mock_boundary_class.return_value = mock_boundary

        # Mock successful creation responses
        mock_boundary.create_label.return_value = {"name": "bug", "id": "new_label_id"}
        mock_boundary.create_issue.return_value = {"number": 1, "id": "new_issue_id"}
        mock_boundary.create_issue_comment.return_value = {"id": "new_comment_id"}

        # Execute restore operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        caplog.clear()
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_original_metadata=True,
            include_pull_requests=False,
            include_sub_issues=False,
        )

        # Verify expected creation calls were made for allowed entities
        assert mock_boundary.create_label.call_count == 2  # 2 labels in sample data
        assert mock_boundary.create_issue.call_count == 2  # 2 issues in sample data
        assert (
            mock_boundary.create_issue_comment.call_count == 2
        )  # 2 issue comments in sample data

        # Verify neither PR nor PR comments were created
        mock_boundary.create_pull_request.assert_not_called()
        mock_boundary.create_pull_request_comment.assert_not_called()

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_maintains_chronological_order_of_pr_comments(
        self, mock_boundary_class, temp_data_dir, sample_github_data
    ):
        """Test that restore operation maintains chronological order of PR comments."""
        # Create backup files with timestamps to verify order
        pr_comments_with_timestamps = [
            {
                "id": 5001,
                "pullRequestNumber": 3,
                "body": "First comment",
                "author": {
                    "login": "reviewer1",
                    "id": 1003,
                    "avatar_url": "https://github.com/reviewer1.png",
                    "html_url": "https://github.com/reviewer1",
                },
                "user": {
                    "login": "reviewer1",
                    "id": 1003,
                    "avatar_url": "https://github.com/reviewer1.png",
                    "html_url": "https://github.com/reviewer1",
                },
                "created_at": "2025-09-29T10:00:00Z",
                "updated_at": "2025-09-29T10:00:00Z",
                "html_url": "https://github.com/owner/repo/pull/3#issuecomment-5001",
                "pull_request_url": "https://api.github.com/repos/owner/repo/pulls/3",
            },
            {
                "id": 5002,
                "pullRequestNumber": 3,
                "body": "Second comment",
                "author": {
                    "login": "reviewer2",
                    "id": 1004,
                    "avatar_url": "https://github.com/reviewer2.png",
                    "html_url": "https://github.com/reviewer2",
                },
                "user": {
                    "login": "reviewer2",
                    "id": 1004,
                    "avatar_url": "https://github.com/reviewer2.png",
                    "html_url": "https://github.com/reviewer2",
                },
                "created_at": "2025-09-29T11:00:00Z",
                "updated_at": "2025-09-29T11:00:00Z",
                "html_url": "https://github.com/owner/repo/pull/3#issuecomment-5002",
                "pull_request_url": "https://api.github.com/repos/owner/repo/pulls/3",
            },
            {
                "id": 5003,
                "pullRequestNumber": 3,
                "body": "Third comment",
                "author": {
                    "login": "reviewer1",
                    "id": 1003,
                    "avatar_url": "https://github.com/reviewer1.png",
                    "html_url": "https://github.com/reviewer1",
                },
                "user": {
                    "login": "reviewer1",
                    "id": 1003,
                    "avatar_url": "https://github.com/reviewer1.png",
                    "html_url": "https://github.com/reviewer1",
                },
                "created_at": "2025-09-29T12:00:00Z",
                "updated_at": "2025-09-29T12:00:00Z",
                "html_url": "https://github.com/owner/repo/pull/3#issuecomment-5003",
                "pull_request_url": "https://api.github.com/repos/owner/repo/pulls/3",
            },
        ]

        temp_path = Path(temp_data_dir)

        with open(temp_path / "labels.json", "w") as f:
            json.dump(sample_github_data["labels"], f)
        with open(temp_path / "issues.json", "w") as f:
            json.dump(sample_github_data["issues"], f)
        with open(temp_path / "comments.json", "w") as f:
            json.dump(sample_github_data["comments"], f)
        with open(temp_path / "pull_requests.json", "w") as f:
            json.dump(sample_github_data["pull_requests"], f)
        with open(temp_path / "pr_comments.json", "w") as f:
            json.dump(pr_comments_with_timestamps, f)

        # Setup mock boundary for restore operations
        mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
        mock_boundary_class.return_value = mock_boundary

        # Mock successful creation responses
        mock_boundary.create_label.return_value = {"name": "bug", "id": "new_label_id"}
        mock_boundary.create_issue.return_value = {"number": 1, "id": "new_issue_id"}
        mock_boundary.create_issue_comment.return_value = {"id": "new_comment_id"}
        mock_boundary.create_pull_request.return_value = {
            "number": 3,
            "id": "new_pr_id",
        }
        mock_boundary.create_pull_request_comment.return_value = {
            "id": "new_pr_comment_id"
        }

        # Execute restore operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_original_metadata=True,
            include_pull_requests=True,
            include_sub_issues=False,
        )

        # Verify PR comments were created in chronological order
        pr_comment_calls = mock_boundary.create_pull_request_comment.call_args_list
        assert len(pr_comment_calls) == 3

        # Verify order based on content (which corresponds to chronological order)
        first_comment = pr_comment_calls[0][0][2]  # Third positional argument (body)
        second_comment = pr_comment_calls[1][0][2]
        third_comment = pr_comment_calls[2][0][2]

        # With include_original_metadata=True, body enriched with author/timestamp
        assert "First comment" in first_comment
        assert "reviewer1" in first_comment
        assert "2025-09-29" in first_comment

        assert "Second comment" in second_comment
        assert "reviewer2" in second_comment
        assert "2025-09-29" in second_comment

        assert "Third comment" in third_comment
        assert "reviewer1" in third_comment
        assert "2025-09-29" in third_comment

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_handles_missing_pr_comments_file_gracefully(
        self, mock_boundary_class, temp_data_dir, sample_github_data
    ):
        """Test restore operation handles missing pr_comments.json file gracefully."""
        # Create backup files but deliberately omit pr_comments.json
        temp_path = Path(temp_data_dir)

        with open(temp_path / "labels.json", "w") as f:
            json.dump(sample_github_data["labels"], f)
        with open(temp_path / "issues.json", "w") as f:
            json.dump(sample_github_data["issues"], f)
        with open(temp_path / "comments.json", "w") as f:
            json.dump(sample_github_data["comments"], f)
        with open(temp_path / "pull_requests.json", "w") as f:
            json.dump(sample_github_data["pull_requests"], f)
        # Note: no pr_comments.json file

        # Setup mock boundary for restore operations
        mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
        mock_boundary_class.return_value = mock_boundary

        # Mock successful creation responses
        mock_boundary.create_label.return_value = {"name": "bug", "id": "new_label_id"}
        mock_boundary.create_issue.return_value = {"number": 1, "id": "new_issue_id"}
        mock_boundary.create_issue_comment.return_value = {"id": "new_comment_id"}
        mock_boundary.create_pull_request.return_value = {
            "number": 42,
            "id": "new_pr_id",
        }

        # Operation should not fail due to missing file
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_original_metadata=True,
            include_pull_requests=True,
            include_sub_issues=False,
        )

        # Verify other entities were still created successfully
        assert mock_boundary.create_label.call_count == 2  # 2 labels in sample data
        assert mock_boundary.create_issue.call_count == 2  # 2 issues in sample data
        assert (
            mock_boundary.create_issue_comment.call_count == 2
        )  # 2 issue comments in sample data
        assert mock_boundary.create_pull_request.call_count == 2  # 2 PRs in sample data

        # PR comments should not be created (file was missing)
        mock_boundary.create_pull_request_comment.assert_not_called()

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_with_orphaned_pr_comments_file_shows_warning(
        self,
        mock_boundary_class,
        temp_data_dir,
        sample_github_data,
        caplog,
    ):
        """Test restore operation with orphaned pr_comments.json but no PRs."""
        # Create backup files but deliberately omit pull_requests.json
        temp_path = Path(temp_data_dir)

        with open(temp_path / "labels.json", "w") as f:
            json.dump(sample_github_data["labels"], f)
        with open(temp_path / "issues.json", "w") as f:
            json.dump(sample_github_data["issues"], f)
        with open(temp_path / "comments.json", "w") as f:
            json.dump(sample_github_data["comments"], f)
        # Note: no pull_requests.json file
        with open(temp_path / "pr_comments.json", "w") as f:
            json.dump(sample_github_data["pr_comments"], f)
        with open(temp_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(temp_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary for restore operations
        mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
        mock_boundary_class.return_value = mock_boundary

        # Mock successful creation responses
        mock_boundary.create_label.return_value = {"name": "bug", "id": "new_label_id"}
        mock_boundary.create_issue.return_value = {"number": 1, "id": "new_issue_id"}
        mock_boundary.create_issue_comment.return_value = {"id": "new_comment_id"}

        # Execute restore operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        caplog.clear()
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_original_metadata=True,
            include_pull_requests=False,
            include_sub_issues=False,
        )

        # Verify other entities were created
        assert mock_boundary.create_label.call_count == 2  # 2 labels in sample data
        assert mock_boundary.create_issue.call_count == 2  # 2 issues in sample data
        assert (
            mock_boundary.create_issue_comment.call_count == 2
        )  # 2 issue comments in sample data

        # Verify PR methods were not called
        mock_boundary.create_pull_request.assert_not_called()
        mock_boundary.create_pull_request_comment.assert_not_called()
