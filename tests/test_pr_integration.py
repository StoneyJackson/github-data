"""Integration tests for Pull Request functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.operations.save import save_repository_data_with_strategy_pattern
from src.github import create_github_service
from src.storage import create_storage_service
from tests.shared import temp_data_dir, sample_pr_data

pytestmark = [pytest.mark.integration]


class TestPullRequestIntegration:
    """Integration tests for pull request save/restore workflows."""


    @patch("src.github.service.GitHubApiBoundary")
    def test_pr_save_creates_json_files(
        self, mock_boundary_class, temp_data_dir, sample_pr_data
    ):
        """Test that save operation creates PR-related JSON files."""
        # Setup mock boundary to return sample data
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock existing methods (empty data for this test)
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        mock_boundary.get_repository_sub_issues.return_value = []

        # Mock new PR methods
        mock_boundary.get_repository_pull_requests.return_value = sample_pr_data[
            "pull_requests"
        ]
        mock_boundary.get_all_pull_request_comments.return_value = sample_pr_data[
            "pr_comments"
        ]

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify PR JSON files were created
        data_path = Path(temp_data_dir)
        assert (data_path / "pull_requests.json").exists()
        assert (data_path / "pr_comments.json").exists()

        # Verify pull_requests.json content
        with open(data_path / "pull_requests.json") as f:
            pr_data = json.load(f)
        assert len(pr_data) == 1
        assert pr_data[0]["title"] == "Add authentication feature"
        assert pr_data[0]["state"] == "MERGED"
        assert pr_data[0]["base_ref"] == "main"
        assert pr_data[0]["head_ref"] == "feature/auth"

        # Verify pr_comments.json content
        with open(data_path / "pr_comments.json") as f:
            comment_data = json.load(f)
        assert len(comment_data) == 1
        assert comment_data[0]["body"] == "LGTM, good work!"
        assert comment_data[0]["user"]["login"] == "bob"
