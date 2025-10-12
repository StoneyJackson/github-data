"""Integration tests for Sub-Issues functionality."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.operations.save import save_repository_data_with_strategy_pattern
from src.github import create_github_service
from src.storage import create_storage_service
from src.operations.restore.restore import restore_repository_data_with_strategy_pattern

pytestmark = [pytest.mark.integration, pytest.mark.medium, pytest.mark.sub_issues]


class TestSubIssuesIntegration:
    """Integration tests for sub-issues save/restore workflows."""

    @pytest.mark.save_workflow
    @pytest.mark.github_api
    @patch("src.github.service.GitHubApiBoundary")
    def test_sub_issues_save_creates_json_files(
        self, mock_boundary_class, temp_data_dir, sample_sub_issues_data
    ):
        """Test that save operation creates sub-issues JSON files."""
        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock existing methods
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        mock_boundary.get_repository_pull_requests.return_value = []
        mock_boundary.get_all_pull_request_comments.return_value = []

        # Mock sub-issues methods
        mock_boundary.get_repository_issues.return_value = sample_sub_issues_data[
            "issues"
        ]
        mock_boundary.get_repository_sub_issues.return_value = sample_sub_issues_data[
            "sub_issues"
        ]

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify sub-issues JSON file was created
        data_path = Path(temp_data_dir)
        assert (data_path / "sub_issues.json").exists()

        # Verify sub_issues.json content
        with open(data_path / "sub_issues.json") as f:
            sub_issues_data = json.load(f)
        assert len(sub_issues_data) == 2
        assert sub_issues_data[0]["parent_issue_number"] == 1
        assert sub_issues_data[0]["sub_issue_number"] == 2
        assert sub_issues_data[0]["position"] == 1
        assert sub_issues_data[1]["parent_issue_number"] == 1
        assert sub_issues_data[1]["sub_issue_number"] == 3
        assert sub_issues_data[1]["position"] == 2

        # Verify issues include sub-issues references
        with open(data_path / "issues.json") as f:
            issues_data = json.load(f)
        parent_issue = next(issue for issue in issues_data if issue["number"] == 1)
        assert "sub_issues" in parent_issue
        assert len(parent_issue["sub_issues"]) == 2

    @pytest.mark.restore_workflow
    @pytest.mark.storage
    @patch("src.github.service.GitHubApiBoundary")
    def test_sub_issues_restore_workflow(
        self, mock_boundary_class, temp_data_dir, sample_sub_issues_data
    ):
        """Test complete sub-issues restore workflow."""
        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock restoration methods
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.create_issue.side_effect = [
            {"number": 101, "title": "Main Feature Implementation"},  # Issue 1 -> 101
            {"number": 102, "title": "Sub-task: Database Schema"},  # Issue 2 -> 102
            {"number": 103, "title": "Sub-task: API Endpoints"},  # Issue 3 -> 103
        ]
        mock_boundary.add_sub_issue.return_value = {"success": True}

        # Create test data files
        data_path = Path(temp_data_dir)
        with open(data_path / "labels.json", "w") as f:
            json.dump([], f)
        with open(data_path / "issues.json", "w") as f:
            json.dump(sample_sub_issues_data["issues"], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "sub_issues.json", "w") as f:
            json.dump(sample_sub_issues_data["sub_issues"], f)
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

        # Execute restore operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_sub_issues=True,
        )

        # Verify issues were created
        assert mock_boundary.create_issue.call_count == 3

        # Verify sub-issue relationships were created
        assert mock_boundary.add_sub_issue.call_count == 2
        # Check that sub-issues were added with correct mapped numbers
        mock_boundary.add_sub_issue.assert_any_call("owner/repo", 101, 102)
        mock_boundary.add_sub_issue.assert_any_call("owner/repo", 101, 103)

    @pytest.mark.restore_workflow
    @pytest.mark.complex_hierarchy
    @pytest.mark.storage
    @patch("src.github.service.GitHubApiBoundary")
    def test_complex_hierarchy_restore(
        self, mock_boundary_class, temp_data_dir, complex_hierarchy_data
    ):
        """Test restore of complex multi-level hierarchy."""
        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock restoration methods
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.create_issue.side_effect = [
            {"number": 201, "title": "Grandparent Issue"},  # Issue 1 -> 201
            {"number": 202, "title": "Parent Issue A"},  # Issue 2 -> 202
            {"number": 203, "title": "Parent Issue B"},  # Issue 3 -> 203
            {"number": 204, "title": "Child Issue A1"},  # Issue 4 -> 204
            {"number": 205, "title": "Child Issue B1"},  # Issue 5 -> 205
        ]
        mock_boundary.add_sub_issue.return_value = {"success": True}

        # Create test data files
        data_path = Path(temp_data_dir)
        with open(data_path / "labels.json", "w") as f:
            json.dump([], f)
        with open(data_path / "issues.json", "w") as f:
            json.dump(complex_hierarchy_data["issues"], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "sub_issues.json", "w") as f:
            json.dump(complex_hierarchy_data["sub_issues"], f)
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

        # Execute restore operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_sub_issues=True,
        )

        # Verify all issues were created
        assert mock_boundary.create_issue.call_count == 5

        # Verify sub-issue relationships were created in correct order
        assert mock_boundary.add_sub_issue.call_count == 4
        # Grandparent -> Parent A
        mock_boundary.add_sub_issue.assert_any_call("owner/repo", 201, 202)
        # Grandparent -> Parent B
        mock_boundary.add_sub_issue.assert_any_call("owner/repo", 201, 203)
        # Parent A -> Child A1
        mock_boundary.add_sub_issue.assert_any_call("owner/repo", 202, 204)
        # Parent B -> Child B1
        mock_boundary.add_sub_issue.assert_any_call("owner/repo", 203, 205)

    @pytest.mark.save_workflow
    @pytest.mark.mixed_states
    @pytest.mark.github_api
    @patch("src.github.service.GitHubApiBoundary")
    def test_sub_issues_backup_with_existing_data(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test sub-issues backup when repository already has mixed data."""
        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock existing repository data
        mock_boundary.get_repository_labels.return_value = [
            {
                "name": "bug",
                "color": "d73a4a",
                "description": "Bug report",
                "url": "https://api.github.com/repos/owner/repo/labels/bug",
                "id": 1001,
            }
        ]
        mock_boundary.get_repository_issues.return_value = [
            {
                "id": 5001,
                "number": 50,
                "title": "Existing Issue",
                "body": "An existing issue",
                "state": "OPEN",
                "user": {
                    "login": "existing",
                    "id": 9001,
                    "avatar_url": "https://github.com/existing.png",
                    "html_url": "https://github.com/existing",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-01T10:00:00Z",
                "updated_at": "2023-01-01T16:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/50",
                "comments": 0,
            }
        ]
        mock_boundary.get_all_issue_comments.return_value = []
        mock_boundary.get_repository_pull_requests.return_value = []
        mock_boundary.get_all_pull_request_comments.return_value = []
        mock_boundary.get_repository_sub_issues.return_value = []

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify all files were created even with empty sub-issues
        data_path = Path(temp_data_dir)
        assert (data_path / "labels.json").exists()
        assert (data_path / "issues.json").exists()
        assert (data_path / "comments.json").exists()
        assert (data_path / "sub_issues.json").exists()
        assert (data_path / "pull_requests.json").exists()
        assert (data_path / "pr_comments.json").exists()

        # Verify sub_issues.json is empty list
        with open(data_path / "sub_issues.json") as f:
            sub_issues_data = json.load(f)
        assert sub_issues_data == []

    @patch("src.github.service.GitHubApiBoundary")
    def test_sub_issues_with_missing_parent_handling(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test handling of sub-issues when parent issue is missing."""
        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock restoration methods - only create one issue
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.create_issue.return_value = {
            "number": 301,
            "title": "Orphaned Sub-issue",
        }  # Only child issue
        mock_boundary.add_sub_issue.return_value = {"success": True}

        # Create test data with orphaned sub-issue
        data_path = Path(temp_data_dir)
        orphaned_issue = {
            "id": 3002,
            "number": 2,
            "title": "Orphaned Sub-issue",
            "body": "This sub-issue has no parent",
            "state": "OPEN",
            "user": {
                "login": "orphan",
                "id": 9999,
                "avatar_url": "https://github.com/orphan.png",
                "html_url": "https://github.com/orphan",
            },
            "assignees": [],
            "labels": [],
            "created_at": "2023-01-11T10:00:00Z",
            "updated_at": "2023-01-16T16:00:00Z",
            "closed_at": None,
            "html_url": "https://github.com/owner/repo/issues/2",
            "comments": 0,
        }
        orphaned_sub_issue = {
            "sub_issue_id": 3002,
            "sub_issue_number": 2,
            "parent_issue_id": 9999,  # Parent doesn't exist
            "parent_issue_number": 999,
            "position": 1,
        }

        with open(data_path / "labels.json", "w") as f:
            json.dump([], f)
        with open(data_path / "issues.json", "w") as f:
            json.dump([orphaned_issue], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "sub_issues.json", "w") as f:
            json.dump([orphaned_sub_issue], f)
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

        # Execute restore operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_sub_issues=True,
        )

        # Verify issue was created but no sub-issue relationship
        assert mock_boundary.create_issue.call_count == 1
        assert mock_boundary.add_sub_issue.call_count == 0

    @patch("src.github.service.GitHubApiBoundary")
    def test_empty_sub_issues_restore(self, mock_boundary_class, temp_data_dir):
        """Test restore operation when no sub-issues exist."""
        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock restoration methods
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.create_issue.return_value = {
            "number": 401,
            "title": "Regular Issue",
        }
        mock_boundary.add_sub_issue.return_value = {"success": True}

        # Create test data with no sub-issues
        data_path = Path(temp_data_dir)
        regular_issue = {
            "id": 4001,
            "number": 1,
            "title": "Regular Issue",
            "body": "Just a regular issue",
            "state": "OPEN",
            "user": {
                "login": "regular",
                "id": 4001,
                "avatar_url": "https://github.com/regular.png",
                "html_url": "https://github.com/regular",
            },
            "assignees": [],
            "labels": [],
            "created_at": "2023-01-10T10:00:00Z",
            "updated_at": "2023-01-15T16:00:00Z",
            "closed_at": None,
            "html_url": "https://github.com/owner/repo/issues/1",
            "comments": 0,
        }

        with open(data_path / "labels.json", "w") as f:
            json.dump([], f)
        with open(data_path / "issues.json", "w") as f:
            json.dump([regular_issue], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "sub_issues.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_reviews.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_review_comments.json", "w") as f:
            json.dump([], f)

        # Execute restore operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_sub_issues=True,
        )

        # Verify issue was created but no sub-issue operations
        assert mock_boundary.create_issue.call_count == 1
        assert mock_boundary.add_sub_issue.call_count == 0
