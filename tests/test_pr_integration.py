"""Integration tests for Pull Request functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.operations.save import save_repository_data

pytestmark = [pytest.mark.integration]


class TestPullRequestIntegration:
    """Integration tests for pull request save/restore workflows."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def sample_pr_data(self):
        """Sample GitHub API PR data that boundary would return."""
        return {
            "pull_requests": [
                {
                    "id": 5001,
                    "number": 1,
                    "title": "Add authentication feature",
                    "body": "This PR adds user authentication support",
                    "state": "MERGED",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "assignees": [],
                    "labels": [
                        {
                            "name": "enhancement",
                            "color": "a2eeef",
                            "description": "New feature or request",
                            "url": (
                                "https://api.github.com/repos/owner/repo"
                                "/labels/enhancement"
                            ),
                            "id": 1002,
                        }
                    ],
                    "created_at": "2023-01-10T10:00:00Z",
                    "updated_at": "2023-01-15T16:00:00Z",
                    "closed_at": "2023-01-15T16:00:00Z",
                    "merged_at": "2023-01-15T16:00:00Z",
                    "merge_commit_sha": "abc123def456",
                    "base_ref": "main",
                    "head_ref": "feature/auth",
                    "html_url": "https://github.com/owner/repo/pull/1",
                    "comments": 1,
                }
            ],
            "pr_comments": [
                {
                    "id": 6001,
                    "body": "LGTM, good work!",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "created_at": "2023-01-15T15:30:00Z",
                    "updated_at": "2023-01-15T15:30:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/pull/1#issuecomment-6001"
                    ),
                    "pull_request_url": "https://github.com/owner/repo/pull/1",
                }
            ],
        }

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
        save_repository_data("fake_token", "owner/repo", temp_data_dir)

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
