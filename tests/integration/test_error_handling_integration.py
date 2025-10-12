"""Integration tests for error scenarios and edge cases."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.github import create_github_service
from src.storage import create_storage_service
from src.operations.save import save_repository_data_with_strategy_pattern
from src.operations.restore.restore import restore_repository_data_with_strategy_pattern

from tests.shared.mocks import add_pr_method_mocks, add_sub_issues_method_mocks
from tests.shared.builders import GitHubDataBuilder

pytestmark = [pytest.mark.integration, pytest.mark.errors]


class TestErrorHandlingIntegration:
    """Integration tests for error scenarios and edge cases."""

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
        with open(data_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_review_comments.json", "w") as f:
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
                include_pull_requests=True,
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
        with open(data_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_review_comments.json", "w") as f:
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
                include_pull_requests=True,
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
        add_pr_method_mocks(mock_boundary)
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
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
                include_pull_requests=True,
            )

        assert "labels.json" in str(exc_info.value)

    @patch("src.github.service.GitHubApiBoundary")
    def test_unicode_content_handling(self, mock_boundary_class, temp_data_dir):
        """Test handling of unicode content in issues and comments."""
        # Create test data with unicode content
        builder = GitHubDataBuilder()
        test_data = builder.with_unicode_content().build()

        # Write test data to files
        data_path = Path(temp_data_dir)
        for key, data in test_data.items():
            with open(data_path / f"{key}.json", "w") as f:
                json.dump(data, f, ensure_ascii=False)

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []

        # Mock successful responses
        mock_boundary.create_issue.return_value = {"number": 10, "id": 999}
        mock_boundary.create_issue_comment.return_value = {"id": 888}

        # Execute restore - should handle unicode gracefully
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_pull_requests=True,
        )

        # Verify unicode content was processed correctly
        issue_calls = mock_boundary.create_issue.call_args_list
        assert len(issue_calls) == 1

        # Check that unicode characters are preserved in the issue title
        issue_call_args = issue_calls[0][0]
        assert "测试 🚀" in issue_call_args[1]  # title is 2nd positional arg
        assert "こんにちは 世界 🌍" in issue_call_args[2]  # body is 3rd positional arg

        # Check unicode in comments
        comment_calls = mock_boundary.create_issue_comment.call_args_list
        assert len(comment_calls) == 1
        comment_call_args = comment_calls[0][0]
        assert "Привет мир! 🎉" in comment_call_args[2]  # body is 3rd positional arg

    @patch("src.github.service.GitHubApiBoundary")
    def test_large_dataset_handling(self, mock_boundary_class, temp_data_dir):
        """Test handling of large datasets without performance issues."""
        # Create test data with many items
        builder = GitHubDataBuilder()
        test_data = (
            builder.with_labels(10)
            .with_issues(50, include_closed=True)
            .with_comments(25, 3)  # 25 issues with 3 comments each = 75 comments
            .with_pull_requests(20)
            .with_pr_comments(15, 2)  # 15 PRs with 2 comments each = 30 PR comments
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

        # Mock successful responses for all operations
        mock_boundary.create_label.return_value = {"id": 999, "name": "test"}
        mock_boundary.create_issue.return_value = {"number": 10, "id": 999}
        mock_boundary.create_issue_comment.return_value = {"id": 888}
        mock_boundary.create_pull_request.return_value = {"number": 20, "id": 777}
        mock_boundary.create_pull_request_comment.return_value = {"id": 666}

        # Execute restore - should handle large dataset efficiently
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_pull_requests=True,
        )

        # Verify all items were processed
        assert mock_boundary.create_label.call_count == 10
        assert mock_boundary.create_issue.call_count == 50
        assert mock_boundary.create_issue_comment.call_count == 75
        assert mock_boundary.create_pull_request.call_count == 20
        assert mock_boundary.create_pull_request_comment.call_count == 30

    @patch("src.github.service.GitHubApiBoundary")
    def test_network_timeout_simulation(self, mock_boundary_class, temp_data_dir):
        """Test handling of network timeouts during API calls."""
        import requests

        # Create minimal test data
        builder = GitHubDataBuilder()
        test_data = builder.with_labels(2).build()

        # Write test data to files
        data_path = Path(temp_data_dir)
        for key, data in test_data.items():
            with open(data_path / f"{key}.json", "w") as f:
                json.dump(data, f)

        # Setup mock boundary to simulate timeout
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []

        # First call succeeds, second times out
        mock_boundary.create_label.side_effect = [
            {"id": 100, "name": "bug"},
            requests.exceptions.Timeout("Request timed out"),
        ]

        # Execute restore operation - should handle timeout gracefully
        with pytest.raises(Exception, match="Failed to create label 'enhancement'"):
            github_service = create_github_service("fake_token")
            storage_service = create_storage_service("json")
            restore_repository_data_with_strategy_pattern(
                github_service,
                storage_service,
                "owner/repo",
                temp_data_dir,
                include_pull_requests=True,
            )

        # Verify first label succeeded before timeout
        assert mock_boundary.create_label.call_count == 2

    @patch("src.github.service.GitHubApiBoundary")
    def test_empty_fields_and_null_values(self, mock_boundary_class, temp_data_dir):
        """Test handling of empty fields and null values in data."""
        # Create test data with various empty/null scenarios
        test_data = {
            "labels": [
                {
                    "name": "empty-description",
                    "color": "ffffff",
                    "description": "",  # Empty string
                    "url": "https://api.github.com/repos/owner/repo/labels/empty",
                    "id": 1001,
                },
                {
                    "name": "null-description",
                    "color": "000000",
                    "description": None,  # Null value
                    "url": "https://api.github.com/repos/owner/repo/labels/null",
                    "id": 1002,
                },
            ],
            "issues": [
                {
                    "id": 2001,
                    "number": 1,
                    "title": "",  # Empty title - edge case
                    "body": None,  # Null body
                    "state": "open",
                    "user": {
                        "login": "testuser",
                        "id": 3001,
                        "avatar_url": "https://github.com/testuser.png",
                        "html_url": "https://github.com/testuser",
                    },
                    "assignees": [],  # Empty array
                    "labels": [],  # Empty array
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "closed_at": None,  # Null for open issue
                    "html_url": "https://github.com/owner/repo/issues/1",
                    "comments": 0,
                }
            ],
            "comments": [],
            "pull_requests": [],
            "pr_comments": [],
        }

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

        # Execute restore - should handle empty/null values gracefully
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_original_metadata=False,
            include_pull_requests=True,
        )

        # Verify calls were made despite empty/null values
        assert mock_boundary.create_label.call_count == 2
        assert mock_boundary.create_issue.call_count == 1

        # Check that empty/null descriptions were handled
        label_calls = mock_boundary.create_label.call_args_list

        # First label - empty description
        first_label_args = label_calls[0][0]
        assert first_label_args[3] == ""  # description is 4th positional arg

        # Second label - null description converted to empty string
        second_label_args = label_calls[1][0]
        assert second_label_args[3] == ""  # None converted to empty string

        # Check that null body was converted to empty string
        issue_calls = mock_boundary.create_issue.call_args_list
        issue_args = issue_calls[0][0]
        assert issue_args[2] == ""  # None body converted to empty string
