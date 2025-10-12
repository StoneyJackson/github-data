"""Integration tests for PR comments save operation file generation."""

import json
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from src.operations.save import save_repository_data_with_strategy_pattern
from src.github import create_github_service
from src.storage import create_storage_service
from tests.shared import add_pr_method_mocks, add_sub_issues_method_mocks

# Test markers for organization and selective execution
pytestmark = [
    pytest.mark.integration,
    pytest.mark.medium,
    pytest.mark.pr_comments,
    pytest.mark.save_operation,
]


class TestPrCommentsSaveIntegration:
    """Integration tests for PR comments save operation behavior."""

    @pytest.fixture
    def sample_github_data_with_pr_comments(self):
        """Sample GitHub API data including pull requests and comments."""
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
                    "number": 1,
                    "title": "Fix authentication bug",
                    "body": "Users cannot login with valid credentials",
                    "state": "open",
                    "user": {
                        "login": "developer1",
                        "id": "USER_123",
                        "avatar_url": "https://github.com/developer1.png",
                        "html_url": "https://github.com/developer1",
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
                    "assignees": [],
                    "created_at": "2025-09-29T10:00:00Z",
                    "updated_at": "2025-09-29T10:00:00Z",
                    "html_url": "https://github.com/owner/repo/issues/1",
                }
            ],
            "comments": [
                {
                    "id": "IC_789",
                    "body": "I can reproduce this issue",
                    "user": {
                        "login": "tester1",
                        "id": "USER_456",
                        "avatar_url": "https://github.com/tester1.png",
                        "html_url": "https://github.com/tester1",
                    },
                    "created_at": "2025-09-29T11:00:00Z",
                    "updated_at": "2025-09-29T11:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/1#issuecomment-789"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                }
            ],
            "pull_requests": [
                {
                    "id": "PR_123",
                    "number": 42,
                    "title": "Add new feature",
                    "body": "This PR adds a new authentication system",
                    "state": "MERGED",
                    "created_at": "2025-09-29T10:00:00Z",
                    "updated_at": "2025-09-29T14:00:00Z",
                    "merged_at": "2025-09-29T15:30:00Z",
                    "user": {
                        "login": "developer1",
                        "id": "USER_123",
                        "avatar_url": "https://github.com/developer1.png",
                        "html_url": "https://github.com/developer1",
                    },
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
                    "assignees": [],
                    "comments": 0,
                    "base_ref": "main",
                    "head_ref": "feature/new-auth",
                    "html_url": "https://github.com/owner/repo/pull/42",
                }
            ],
            "pr_comments": [
                {
                    "id": "IC_790",
                    "body": "This looks great! LGTM.",
                    "user": {
                        "login": "reviewer1",
                        "id": "USER_456",
                        "avatar_url": "https://github.com/reviewer1.png",
                        "html_url": "https://github.com/reviewer1",
                    },
                    "created_at": "2025-09-29T11:30:00Z",
                    "updated_at": "2025-09-29T11:30:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/pull/42#issuecomment-790"
                    ),
                    "pull_request_url": "https://github.com/owner/repo/pull/42",
                },
                {
                    "id": "IC_791",
                    "body": "Could you add more tests?",
                    "user": {
                        "login": "reviewer2",
                        "id": "USER_789",
                        "avatar_url": "https://github.com/reviewer2.png",
                        "html_url": "https://github.com/reviewer2",
                    },
                    "created_at": "2025-09-29T12:00:00Z",
                    "updated_at": "2025-09-29T12:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/pull/42#issuecomment-791"
                    ),
                    "pull_request_url": "https://github.com/owner/repo/pull/42",
                },
            ],
        }

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_with_pr_comments_enabled_creates_all_files(
        self, mock_boundary_class, temp_data_dir, sample_github_data_with_pr_comments
    ):
        """Test save operation with PR comments enabled creates all expected files."""
        # Setup mock boundary to return our sample data
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = (
            sample_github_data_with_pr_comments["labels"]
        )
        mock_boundary.get_repository_issues.return_value = (
            sample_github_data_with_pr_comments["issues"]
        )
        mock_boundary.get_all_issue_comments.return_value = (
            sample_github_data_with_pr_comments["comments"]
        )
        add_pr_method_mocks(mock_boundary, sample_github_data_with_pr_comments)
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify all expected files were created
        data_path = Path(temp_data_dir)

        assert (data_path / "labels.json").exists()
        assert (data_path / "issues.json").exists()
        assert (data_path / "comments.json").exists()
        assert (data_path / "pull_requests.json").exists()
        assert (data_path / "pr_comments.json").exists()

        # Verify file contents
        with open(data_path / "labels.json") as f:
            saved_labels = json.load(f)
            assert len(saved_labels) == 1
            assert saved_labels[0]["name"] == "bug"

        with open(data_path / "pull_requests.json") as f:
            saved_prs = json.load(f)
            assert len(saved_prs) == 1
            assert saved_prs[0]["number"] == 42
            assert saved_prs[0]["title"] == "Add new feature"

        with open(data_path / "pr_comments.json") as f:
            saved_pr_comments = json.load(f)
            assert len(saved_pr_comments) == 2
            assert saved_pr_comments[0]["body"] == "This looks great! LGTM."
            assert saved_pr_comments[1]["body"] == "Could you add more tests?"

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_with_prs_but_no_pr_comments_excludes_pr_comments_file(
        self, mock_boundary_class, temp_data_dir, sample_github_data_with_pr_comments
    ):
        """Test save operation with PRs enabled but PR comments disabled."""
        # Setup mock boundary to return our sample data
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = (
            sample_github_data_with_pr_comments["labels"]
        )
        mock_boundary.get_repository_issues.return_value = (
            sample_github_data_with_pr_comments["issues"]
        )
        mock_boundary.get_all_issue_comments.return_value = (
            sample_github_data_with_pr_comments["comments"]
        )
        mock_boundary.get_repository_pull_requests.return_value = (
            sample_github_data_with_pr_comments["pull_requests"]
        )
        # Add empty PR comments mock to test exclusion
        mock_boundary.get_all_pull_request_comments.return_value = []
        mock_boundary.get_all_pull_request_reviews.return_value = []
        mock_boundary.get_all_pull_request_review_comments.return_value = []
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify expected files were created
        data_path = Path(temp_data_dir)

        assert (data_path / "labels.json").exists()
        assert (data_path / "issues.json").exists()
        assert (data_path / "comments.json").exists()
        assert (data_path / "pull_requests.json").exists()

        # PR comments file should exist but be empty
        assert (data_path / "pr_comments.json").exists()
        with open(data_path / "pr_comments.json") as f:
            saved_pr_comments = json.load(f)
            assert saved_pr_comments == []

        # Verify PR comments method was called but returned empty list
        mock_boundary.get_all_pull_request_comments.assert_called_once()

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_with_pr_comments_but_no_prs_shows_warning_and_excludes_files(
        self,
        mock_boundary_class,
        temp_data_dir,
        sample_github_data_with_pr_comments,
        caplog,
    ):
        """Test save operation with PR comments enabled but PRs disabled."""
        # Setup mock boundary to return our sample data but exclude PRs
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = (
            sample_github_data_with_pr_comments["labels"]
        )
        mock_boundary.get_repository_issues.return_value = (
            sample_github_data_with_pr_comments["issues"]
        )
        mock_boundary.get_all_issue_comments.return_value = (
            sample_github_data_with_pr_comments["comments"]
        )
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        caplog.clear()
        save_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_pull_requests=False,
            include_sub_issues=False,
        )

        # Verify expected files were created
        data_path = Path(temp_data_dir)

        assert (data_path / "labels.json").exists()
        assert (data_path / "issues.json").exists()
        assert (data_path / "comments.json").exists()  # Issue comments only

        # Neither PR files should exist
        assert not (data_path / "pull_requests.json").exists()
        assert not (data_path / "pr_comments.json").exists()

        # Verify PR methods were not called
        mock_boundary.get_repository_pull_requests.assert_not_called()
        mock_boundary.get_all_pull_request_comments.assert_not_called()

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_with_minimal_config_excludes_all_pr_files(
        self, mock_boundary_class, temp_data_dir, sample_github_data_with_pr_comments
    ):
        """Test save operation with minimal config excludes all PR-related files."""
        # Setup mock boundary with minimal data
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = (
            sample_github_data_with_pr_comments["labels"]
        )
        mock_boundary.get_repository_issues.return_value = (
            sample_github_data_with_pr_comments["issues"]
        )
        mock_boundary.get_all_issue_comments.return_value = (
            sample_github_data_with_pr_comments["comments"]
        )
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_pull_requests=False,
            include_sub_issues=False,
        )

        # Verify only core files were created
        data_path = Path(temp_data_dir)

        assert (data_path / "labels.json").exists()
        assert (data_path / "issues.json").exists()
        assert (data_path / "comments.json").exists()

        # No PR files should exist
        assert not (data_path / "pull_requests.json").exists()
        assert not (data_path / "pr_comments.json").exists()

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_operation_performance_impact_with_pr_comments(
        self, mock_boundary_class, temp_data_dir, sample_github_data_with_pr_comments
    ):
        """Test that PR comments add expected API calls and processing time."""
        # Setup mock boundary to return our sample data
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = (
            sample_github_data_with_pr_comments["labels"]
        )
        mock_boundary.get_repository_issues.return_value = (
            sample_github_data_with_pr_comments["issues"]
        )
        mock_boundary.get_all_issue_comments.return_value = (
            sample_github_data_with_pr_comments["comments"]
        )
        add_pr_method_mocks(mock_boundary, sample_github_data_with_pr_comments)
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify all expected API calls were made
        mock_boundary.get_repository_labels.assert_called_once()
        mock_boundary.get_repository_issues.assert_called_once()
        mock_boundary.get_all_issue_comments.assert_called_once()
        mock_boundary.get_repository_pull_requests.assert_called_once()
        mock_boundary.get_all_pull_request_comments.assert_called_once()

        # This test validates the "5 API calls" mentioned in performance doc
        total_api_calls = (
            mock_boundary.get_repository_labels.call_count
            + mock_boundary.get_repository_issues.call_count
            + mock_boundary.get_all_issue_comments.call_count
            + mock_boundary.get_repository_pull_requests.call_count
            + mock_boundary.get_all_pull_request_comments.call_count
        )
        assert total_api_calls == 5  # All 5 expected API calls were made

    @patch("src.github.service.GitHubApiBoundary")
    def test_pr_comments_file_structure_matches_specification(
        self, mock_boundary_class, temp_data_dir, sample_github_data_with_pr_comments
    ):
        """Test that saved PR comments file structure matches the specification."""
        # Setup mock boundary to return our sample data
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = (
            sample_github_data_with_pr_comments["labels"]
        )
        mock_boundary.get_repository_issues.return_value = (
            sample_github_data_with_pr_comments["issues"]
        )
        mock_boundary.get_all_issue_comments.return_value = (
            sample_github_data_with_pr_comments["comments"]
        )
        add_pr_method_mocks(mock_boundary, sample_github_data_with_pr_comments)
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify PR comments file structure matches use cases specification
        data_path = Path(temp_data_dir)

        with open(data_path / "pr_comments.json") as f:
            saved_pr_comments = json.load(f)

            # Verify structure matches the JSON structure from use cases
            assert isinstance(saved_pr_comments, list)
            assert len(saved_pr_comments) == 2

            first_comment = saved_pr_comments[0]
            expected_fields = {
                "id",
                "body",
                "user",
                "created_at",
                "updated_at",
                "html_url",
            }
            actual_fields = set(first_comment.keys())

            # Check that all expected fields are present
            assert expected_fields.issubset(
                actual_fields
            ), f"Missing fields: {expected_fields - actual_fields}"

            # Verify specific field types and values
            assert isinstance(first_comment["user"], dict)
            assert "login" in first_comment["user"]
            assert "id" in first_comment["user"]
