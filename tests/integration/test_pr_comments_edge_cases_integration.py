"""Integration tests for PR comments error handling and edge cases."""

import json
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from src.operations.save import save_repository_data_with_strategy_pattern
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
    pytest.mark.error_handling,
]


class TestPrCommentsEdgeCasesIntegration:
    """Integration tests for PR comments error handling and edge cases."""


    @patch("src.github.service.GitHubApiBoundary")
    def test_save_operation_handles_empty_pr_comments_list(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test save operation handles empty PR comments response gracefully."""
        # Setup mock boundary with empty PR comments
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock empty responses using correct method names
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        mock_boundary.get_repository_pull_requests.return_value = []
        mock_boundary.get_all_pull_request_comments.return_value = []  # Empty list
        mock_boundary.get_all_pull_request_reviews.return_value = []
        mock_boundary.get_all_pull_request_review_comments.return_value = []
        mock_boundary.get_repository_sub_issues.return_value = []

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify files were created with empty arrays
        temp_path = Path(temp_data_dir)

        assert (temp_path / "pr_comments.json").exists()
        with open(temp_path / "pr_comments.json") as f:
            saved_pr_comments = json.load(f)
            assert saved_pr_comments == []

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_operation_handles_pr_comments_api_failure(
        self, mock_boundary_class, temp_data_dir, caplog
    ):
        """Test save operation handles PR comments API failure gracefully."""
        # Setup mock boundary with API failure for PR comments
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock successful responses for other entities
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        mock_boundary.get_repository_pull_requests.return_value = []

        # Mock API failure for PR comments
        mock_boundary.get_all_pull_request_comments.side_effect = Exception(
            "API rate limit exceeded"
        )
        mock_boundary.get_repository_sub_issues.return_value = []

        # Execute save operation - should handle the error gracefully
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")

        with pytest.raises(Exception, match="API rate limit exceeded"):
            save_repository_data_with_strategy_pattern(
                github_service, storage_service, "owner/repo", temp_data_dir
            )

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_handles_corrupted_pr_comments_file(
        self, mock_boundary_class, temp_data_dir, sample_github_data, caplog
    ):
        """Test restore operation handles corrupted pr_comments.json file."""
        temp_path = Path(temp_data_dir)

        # Create valid backup files
        with open(temp_path / "labels.json", "w") as f:
            json.dump(sample_github_data["labels"], f)
        with open(temp_path / "issues.json", "w") as f:
            json.dump(sample_github_data["issues"], f)
        with open(temp_path / "comments.json", "w") as f:
            json.dump(sample_github_data["comments"], f)
        with open(temp_path / "pull_requests.json", "w") as f:
            json.dump(sample_github_data["pull_requests"], f)

        # Create corrupted pr_comments.json
        with open(temp_path / "pr_comments.json", "w") as f:
            f.write("{ invalid json content }")
        with open(temp_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(temp_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary for restore operations
        mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
        mock_boundary_class.return_value = mock_boundary

        mock_boundary.create_label.return_value = {"name": "bug", "id": "new_label_id"}
        mock_boundary.create_issue.return_value = {"number": 1, "id": "new_issue_id"}
        mock_boundary.create_issue_comment.return_value = {"id": "new_comment_id"}
        mock_boundary.create_pull_request.return_value = {
            "number": 100,
            "id": "new_pr_id",
        }

        # Execute restore operation - should handle corrupted file gracefully
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")

        caplog.clear()
        with pytest.raises((json.JSONDecodeError, Exception)):
            restore_repository_data_with_strategy_pattern(
                github_service,
                storage_service,
                "owner/repo",
                temp_data_dir,
                include_original_metadata=True,
                include_pull_requests=True,
                include_sub_issues=False,
            )

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_handles_pr_comment_creation_failures_gracefully(
        self, mock_boundary_class, temp_data_dir, sample_github_data, caplog
    ):
        """Test restore handles individual PR comment creation failures."""
        temp_path = Path(temp_data_dir)

        # Create valid backup files
        with open(temp_path / "labels.json", "w") as f:
            json.dump(sample_github_data["labels"], f)
        with open(temp_path / "issues.json", "w") as f:
            json.dump(sample_github_data["issues"], f)
        with open(temp_path / "comments.json", "w") as f:
            json.dump(sample_github_data["comments"], f)
        with open(temp_path / "pull_requests.json", "w") as f:
            json.dump(sample_github_data["pull_requests"], f)
        with open(temp_path / "pr_comments.json", "w") as f:
            # Use the PR comments from shared fixture (just 3 comments)
            json.dump(sample_github_data["pr_comments"], f)
        with open(temp_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(temp_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary for restore operations
        mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
        mock_boundary_class.return_value = mock_boundary

        mock_boundary.create_label.return_value = {"name": "bug", "id": "new_label_id"}
        mock_boundary.create_issue.return_value = {"number": 1, "id": "new_issue_id"}
        mock_boundary.create_issue_comment.return_value = {"id": "new_comment_id"}
        mock_boundary.create_pull_request.return_value = {
            "number": 100,
            "id": "new_pr_id",
        }

        # Mock first PR comment creation to succeed, second to fail
        mock_boundary.create_pull_request_comment.side_effect = [
            {"id": "pr_comment_1"},  # First succeeds
            Exception("API error"),  # Second fails
            {"id": "pr_comment_3"},  # Third succeeds (if we get there)
        ]

        # Execute restore operation - should handle partial failure gracefully
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")

        caplog.clear()
        try:
            restore_repository_data_with_strategy_pattern(
                github_service,
                storage_service,
                "owner/repo",
                temp_data_dir,
                include_original_metadata=True,
                include_pull_requests=True,
                include_sub_issues=False,
            )
        except Exception as e:
            # The operation may fail completely or continue with errors logged
            assert "API error" in str(e) or any(
                "API error" in record.message for record in caplog.records
            )

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_with_mismatched_pr_numbers_in_comments(
        self, mock_boundary_class, temp_data_dir, caplog
    ):
        """Test restore handles PR comments referencing non-existent PRs."""
        temp_path = Path(temp_data_dir)

        # Create backup with PRs and comments that reference different PR numbers
        labels = [
            {
                "name": "bug",
                "color": "red",
                "description": "Bug",
                "url": "https://api.github.com/repos/owner/repo/labels/bug",
                "id": 1000,
            }
        ]
        issues = []
        comments = []
        pull_requests = [
            {
                "id": 3001,
                "number": 100,  # PR exists
                "title": "Valid PR",
                "body": "PR body",
                "state": "OPEN",
                "user": {
                    "login": "dev1",
                    "id": 1001,
                    "avatar_url": "https://github.com/dev1.png",
                    "html_url": "https://github.com/dev1",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T10:30:00Z",
                "base_ref": "main",
                "head_ref": "feature/test",
                "html_url": "https://github.com/owner/repo/pull/100",
                "comments": 0,
                "merged": False,
            }
        ]
        pr_comments = [
            {
                "id": 5001,
                "pullRequestNumber": 999,  # PR does not exist in backup
                "body": "Orphaned comment",
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
                "created_at": "2023-01-15T14:00:00Z",
                "updated_at": "2023-01-15T14:00:00Z",
                "html_url": "https://github.com/owner/repo/pull/999#issuecomment-5001",
                "pull_request_url": "https://api.github.com/repos/owner/repo/pulls/999",
            },
            {
                "id": 5002,
                "pullRequestNumber": 100,  # PR exists
                "body": "Valid comment",
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
                "created_at": "2023-01-15T15:00:00Z",
                "updated_at": "2023-01-15T15:00:00Z",
                "html_url": "https://github.com/owner/repo/pull/100#issuecomment-5002",
                "pull_request_url": "https://api.github.com/repos/owner/repo/pulls/100",
            },
        ]

        with open(temp_path / "labels.json", "w") as f:
            json.dump(labels, f)
        with open(temp_path / "issues.json", "w") as f:
            json.dump(issues, f)
        with open(temp_path / "comments.json", "w") as f:
            json.dump(comments, f)
        with open(temp_path / "pull_requests.json", "w") as f:
            json.dump(pull_requests, f)
        with open(temp_path / "pr_comments.json", "w") as f:
            json.dump(pr_comments, f)
        with open(temp_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(temp_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary for restore operations
        mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
        mock_boundary_class.return_value = mock_boundary

        mock_boundary.create_label.return_value = {"name": "bug", "id": "new_label_id"}
        mock_boundary.create_pull_request.return_value = {
            "number": 100,
            "id": "new_pr_id",
        }
        mock_boundary.create_pull_request_comment.return_value = {
            "id": "new_pr_comment_id"
        }

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
            include_pull_requests=True,
            include_pull_request_comments=True,
            include_sub_issues=False,
        )

        # Verify only the valid comment was created (orphaned comments skipped)
        assert mock_boundary.create_pull_request_comment.call_count == 1

        # Verify the warning about the orphaned comment was logged
        assert any(
            "No mapping found for PR #999" in record.message
            for record in caplog.records
        )

    @patch("src.github.service.GitHubApiBoundary")
    def test_large_dataset_performance_implications(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test performance implications with large PR comment datasets."""
        # Generate a larger dataset to simulate performance impact
        large_pr_comments = []
        for i in range(100):  # Simulate 100 PR comments
            large_pr_comments.append(
                {
                    "id": 5000 + i,
                    "pullRequestNumber": i % 10 + 1,  # Distribute across 10 PRs
                    "body": (
                        f"Comment {i} with some substantial content to simulate "
                        f"real PR discussions"
                    ),
                    "author": {
                        "login": f"reviewer{i % 5}",
                        "id": 2000 + (i % 5),
                        "avatar_url": f"https://github.com/reviewer{i % 5}.png",
                        "html_url": f"https://github.com/reviewer{i % 5}",
                    },
                    "user": {
                        "login": f"reviewer{i % 5}",
                        "id": 2000 + (i % 5),
                        "avatar_url": f"https://github.com/reviewer{i % 5}.png",
                        "html_url": f"https://github.com/reviewer{i % 5}",
                    },
                    "created_at": f"2025-09-29T{10 + i % 14:02d}:00:00Z",
                    "updated_at": f"2025-09-29T{10 + i % 14:02d}:00:00Z",
                    "html_url": (
                        f"https://github.com/owner/repo/pull/{i % 10 + 1}"
                        f"#issuecomment-{5000 + i}"
                    ),
                    "pull_request_url": (
                        f"https://api.github.com/repos/owner/repo/pulls/{i % 10 + 1}"
                    ),
                }
            )

        # Setup mock boundary with large dataset
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock responses with large dataset
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        mock_boundary.get_repository_pull_requests.return_value = [
            {
                "id": 1000 + i,
                "number": i,
                "title": f"PR {i}",
                "body": f"PR {i} body",
                "state": "OPEN",
                "user": {
                    "login": "dev1",
                    "id": 1001,
                    "avatar_url": "https://github.com/dev1.png",
                    "html_url": "https://github.com/dev1",
                },
                "labels": [],
                "assignees": [],
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T10:30:00Z",
                "base_ref": "main",
                "head_ref": f"feature/pr-{i}",
                "html_url": f"https://github.com/owner/repo/pull/{i}",
                "comments": 0,
                "merged": False,
            }
            for i in range(1, 11)
        ]
        mock_boundary.get_all_pull_request_comments.return_value = large_pr_comments
        mock_boundary.get_all_pull_request_reviews.return_value = []
        mock_boundary.get_all_pull_request_review_comments.return_value = []
        mock_boundary.get_repository_sub_issues.return_value = []

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")

        # This should complete without performance issues in test environment
        import time

        start_time = time.time()
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )
        end_time = time.time()

        # Basic performance check - operation should complete in reasonable time
        assert (
            end_time - start_time
        ) < 30, "Save operation took too long with large dataset"

        # Verify file was created with correct content
        temp_path = Path(temp_data_dir)
        assert (temp_path / "pr_comments.json").exists()

        with open(temp_path / "pr_comments.json") as f:
            saved_comments = json.load(f)
            assert len(saved_comments) == 100, "All PR comments should be saved"
