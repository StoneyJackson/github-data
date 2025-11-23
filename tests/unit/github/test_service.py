"""Tests for GitHubService repository methods."""

import pytest
from unittest.mock import Mock
from github_data.github.service import GitHubService


pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
]


class TestGitHubServiceRepositoryMethods:
    """Test GitHub service repository methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_boundary = Mock()
        self.mock_rate_limiter = Mock()
        self.mock_rate_limiter.execute_with_retry.side_effect = lambda op, _: op()

        self.service = GitHubService(
            boundary=self.mock_boundary,
            rate_limiter=self.mock_rate_limiter,
            caching_enabled=False,
        )

    def test_get_repository_metadata_returns_data_when_exists(self):
        """Test get_repository_metadata returns data for existing repository."""
        expected_data = {"id": 123, "name": "repo", "full_name": "owner/repo"}
        self.mock_boundary.get_repository_metadata.return_value = expected_data

        result = self.service.get_repository_metadata("owner/repo")

        assert result == expected_data
        self.mock_boundary.get_repository_metadata.assert_called_once_with("owner/repo")

    def test_get_repository_metadata_returns_none_on_404(self):
        """Test get_repository_metadata returns None when repository not found."""
        from github import UnknownObjectException

        self.mock_boundary.get_repository_metadata.side_effect = UnknownObjectException(
            status=404, data={"message": "Not Found"}
        )

        result = self.service.get_repository_metadata("owner/nonexistent")

        assert result is None

    def test_get_repository_metadata_propagates_other_exceptions(self):
        """Test get_repository_metadata propagates non-404 exceptions."""
        from github import GithubException

        self.mock_boundary.get_repository_metadata.side_effect = GithubException(
            status=403, data={"message": "Forbidden"}
        )

        with pytest.raises(GithubException):
            self.service.get_repository_metadata("owner/repo")

    def test_create_repository_calls_boundary(self):
        """Test create_repository delegates to boundary layer."""
        expected_data = {"id": 456, "name": "new-repo", "private": True}
        self.mock_boundary.create_repository.return_value = expected_data

        result = self.service.create_repository(
            "owner/new-repo", private=True, description="Test repo"
        )

        assert result == expected_data
        self.mock_boundary.create_repository.assert_called_once_with(
            "owner/new-repo", private=True, description="Test repo"
        )
