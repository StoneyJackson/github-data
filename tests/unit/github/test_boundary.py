"""Tests for GitHubApiBoundary."""

import pytest
from unittest.mock import MagicMock
from github_data.github.boundary import GitHubApiBoundary


class TestGitHubApiBoundary:
    """Test suite for GitHubApiBoundary class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_github = MagicMock()
        self.boundary = GitHubApiBoundary.__new__(GitHubApiBoundary)
        self.boundary._github = self.mock_github

    def test_get_repository_metadata_returns_raw_data(self):
        """Test get_repository_metadata returns raw repository data."""
        # Mock PyGithub repository object
        mock_repo = MagicMock()
        mock_repo.raw_data = {
            "id": 12345,
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "private": False,
        }

        self.mock_github.get_repo.return_value = mock_repo

        result = self.boundary.get_repository_metadata("owner/test-repo")

        assert result == mock_repo.raw_data
        self.mock_github.get_repo.assert_called_once_with("owner/test-repo")

    def test_get_repository_metadata_raises_on_not_found(self):
        """Test get_repository_metadata raises UnknownObjectException for 404."""
        from github import UnknownObjectException

        self.mock_github.get_repo.side_effect = UnknownObjectException(
            status=404, data={"message": "Not Found"}
        )

        with pytest.raises(UnknownObjectException):
            self.boundary.get_repository_metadata("owner/nonexistent")

    def test_create_repository_in_user_account(self):
        """Test create_repository creates repo in user account."""
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_created_repo = MagicMock()
        mock_created_repo.raw_data = {
            "id": 67890,
            "name": "new-repo",
            "full_name": "testuser/new-repo",
            "private": False,
        }

        self.mock_github.get_user.return_value = mock_user
        mock_user.create_repo.return_value = mock_created_repo

        result = self.boundary.create_repository(
            "testuser/new-repo", private=False, description="Test repository"
        )

        assert result == mock_created_repo.raw_data
        mock_user.create_repo.assert_called_once_with(
            name="new-repo", private=False, description="Test repository"
        )

    def test_create_repository_in_organization(self):
        """Test create_repository creates repo in organization."""
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_org = MagicMock()
        mock_created_repo = MagicMock()
        mock_created_repo.raw_data = {
            "id": 67890,
            "name": "new-repo",
            "full_name": "testorg/new-repo",
            "private": True,
        }

        self.mock_github.get_user.return_value = mock_user
        self.mock_github.get_organization.return_value = mock_org
        mock_org.create_repo.return_value = mock_created_repo

        result = self.boundary.create_repository(
            "testorg/new-repo", private=True, description="Test org repo"
        )

        assert result == mock_created_repo.raw_data
        self.mock_github.get_organization.assert_called_once_with("testorg")
        mock_org.create_repo.assert_called_once_with(
            name="new-repo", private=True, description="Test org repo"
        )
