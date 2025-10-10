import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.main import main
from tests.shared.builders import ConfigBuilder

# Test markers for organization and selective execution
pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow,
    pytest.mark.end_to_end,
    pytest.mark.include_issue_comments,
]


class TestCommentsFeatureEndToEnd:
    """End-to-end tests for the INCLUDE_ISSUE_COMMENTS feature."""

    def test_save_and_restore_cycle_with_comments_enabled(
        self, temp_data_dir, sample_repo_data_with_comments
    ):
        """Test complete save/restore cycle with comments enabled."""
        data_path = Path(temp_data_dir) / "backup"
        data_path.mkdir()

        # Mock environment for save operation
        save_env = (
            ConfigBuilder()
            .with_operation("save")
            .with_data_path(str(data_path))
            .with_issue_comments(True)
            .with_git_repo(False)
            .as_env_dict()
        )

        with patch.dict(os.environ, save_env, clear=True):
            with patch("src.github.create_github_service") as mock_github:
                mock_github.return_value = sample_repo_data_with_comments

                # Execute save operation
                main()

                # Verify comments were saved
                comments_file = data_path / "comments.json"
                assert comments_file.exists()

                with open(comments_file) as f:
                    comments_data = json.load(f)
                assert len(comments_data) > 0

        # Mock environment for restore operation
        restore_env = (
            ConfigBuilder()
            .with_operation("restore")
            .with_repo("owner/repo-new")
            .with_data_path(str(data_path))
            .with_issue_comments(True)
            .with_git_repo(False)
            .as_env_dict()
        )

        with patch.dict(os.environ, restore_env, clear=True):
            with patch("src.github.create_github_service") as mock_github:
                mock_restore_service = MagicMock()
                mock_github.return_value = mock_restore_service

                # Execute restore operation
                main()

                # Verify comments restoration was attempted
                assert mock_restore_service.create_issue_comment.called

    def test_save_excludes_comments_when_disabled(
        self, temp_data_dir, sample_repo_data_with_comments
    ):
        """Test that save operation excludes comments when disabled."""
        data_path = Path(temp_data_dir) / "backup"
        data_path.mkdir()

        env_vars = (
            ConfigBuilder()
            .with_operation("save")
            .with_data_path(str(data_path))
            .with_issue_comments(False)
            .with_git_repo(False)
            .as_env_dict()
        )

        with patch.dict(os.environ, env_vars, clear=True):
            with patch("src.github.create_github_service") as mock_github:
                mock_github.return_value = sample_repo_data_with_comments

                main()

                # Verify comments were NOT saved
                comments_file = data_path / "comments.json"
                assert not comments_file.exists()

                # But other files should exist
                issues_file = data_path / "issues.json"
                labels_file = data_path / "labels.json"
                assert issues_file.exists()
                assert labels_file.exists()


@pytest.fixture
def sample_repo_data_with_comments():
    """Mock GitHub service with sample repository data including comments."""
    mock_service = MagicMock()

    # Configure mock responses
    mock_service.get_repository_labels.return_value = [
        {
            "name": "bug",
            "color": "d73a4a",
            "description": "Bug reports",
            "url": "https://api.github.com/repos/owner/repo/labels/bug",
            "id": 101,
        }
    ]

    mock_service.get_repository_issues.return_value = [
        {
            "id": 789,
            "number": 1,
            "title": "Test Issue",
            "body": "Test issue body",
            "state": "open",
            "user": {
                "login": "testuser",
                "id": 456,
                "avatar_url": "https://avatars.githubusercontent.com/u/456",
                "html_url": "https://github.com/testuser",
            },
            "assignees": [],
            "labels": [
                {
                    "name": "bug",
                    "color": "d73a4a",
                    "description": "Bug reports",
                    "url": "https://api.github.com/repos/owner/repo/labels/bug",
                    "id": 101,
                }
            ],
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "closed_at": None,
            "html_url": "https://github.com/owner/repo/issues/1",
            "comments": 1,
        }
    ]

    mock_service.get_all_issue_comments.return_value = [
        {
            "id": 123,
            "body": "Test comment",
            "user": {
                "login": "testuser",
                "id": 456,
                "avatar_url": "https://avatars.githubusercontent.com/u/456",
                "html_url": "https://github.com/testuser",
            },
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "html_url": "https://github.com/owner/repo/issues/1#issuecomment-123",
            "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
        }
    ]

    return mock_service
