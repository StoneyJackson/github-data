"""Integration tests for Pull Request functionality."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.operations.save import save_repository_data_with_strategy_pattern
from src.github import create_github_service
from src.storage import create_storage_service
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

pytestmark = [pytest.mark.integration, pytest.mark.medium]


class TestPullRequestIntegration:
    """Integration tests for pull request save/restore workflows."""

    @patch("src.github.service.GitHubApiBoundary")
    def test_pr_save_creates_json_files(
        self, mock_boundary_class, temp_data_dir, sample_pr_data
    ):
        """Test that save operation creates PR-related JSON files."""
        # Setup mock boundary using factory with sample PR data
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_pr_data)
        mock_boundary_class.return_value = mock_boundary

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
        assert len(pr_data) == 2
        assert pr_data[0]["title"] == "Feature implementation"
        assert pr_data[0]["state"] == "OPEN"
        assert pr_data[0]["base_ref"] == "main"
        assert pr_data[0]["head_ref"] == "feature/new-implementation"

        # Verify pr_comments.json content
        with open(data_path / "pr_comments.json") as f:
            comment_data = json.load(f)
        assert len(comment_data) == 3
        assert comment_data[0]["body"] == "Great implementation!"
        assert comment_data[0]["user"]["login"] == "charlie"
