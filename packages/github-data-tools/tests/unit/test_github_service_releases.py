"""Tests for GitHub service release methods."""

import pytest
from unittest.mock import Mock
from github_data_tools.github.service import GitHubService


pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
]


class TestGitHubServiceReleases:
    """Test GitHub service release methods."""

    def test_get_repository_releases(self):
        """Test fetching repository releases."""
        # Setup mocks
        mock_boundary = Mock()
        mock_rate_limiter = Mock()

        # Configure boundary to return sample releases
        mock_boundary.get_repository_releases.return_value = [
            {
                "id": 1,
                "tag_name": "v1.0.0",
                "name": "Version 1.0.0",
                "draft": False,
                "prerelease": False,
            },
            {
                "id": 2,
                "tag_name": "v2.0.0",
                "name": "Version 2.0.0",
                "draft": False,
                "prerelease": False,
            },
        ]

        # Configure rate limiter to execute operation
        mock_rate_limiter.execute_with_retry.side_effect = lambda op, _: op()

        # Create service
        service = GitHubService(
            boundary=mock_boundary,
            rate_limiter=mock_rate_limiter,
            caching_enabled=False,
        )

        # Execute
        releases = service.get_repository_releases("owner/repo")

        # Verify
        assert len(releases) == 2
        assert releases[0]["tag_name"] == "v1.0.0"
        assert releases[1]["tag_name"] == "v2.0.0"
        mock_boundary.get_repository_releases.assert_called_once_with("owner/repo")

    def test_create_release(self):
        """Test creating a release."""
        # Setup mocks
        mock_boundary = Mock()
        mock_rate_limiter = Mock()

        # Configure boundary to return created release
        mock_boundary.create_release.return_value = {
            "id": 123,
            "tag_name": "v1.0.0",
            "name": "Version 1.0.0",
            "body": "Release notes",
            "draft": False,
            "prerelease": False,
            "created_at": "2025-01-01T12:00:00Z",
        }

        # Configure rate limiter
        mock_rate_limiter.execute_with_retry.side_effect = lambda op, _: op()

        # Create service
        service = GitHubService(
            boundary=mock_boundary,
            rate_limiter=mock_rate_limiter,
            caching_enabled=False,
        )

        # Execute
        result = service.create_release(
            repo_name="owner/repo",
            tag_name="v1.0.0",
            target_commitish="main",
            name="Version 1.0.0",
            body="Release notes",
            draft=False,
            prerelease=False,
        )

        # Verify
        assert result["tag_name"] == "v1.0.0"
        assert result["name"] == "Version 1.0.0"
        mock_boundary.create_release.assert_called_once_with(
            repo_name="owner/repo",
            tag_name="v1.0.0",
            target_commitish="main",
            name="Version 1.0.0",
            body="Release notes",
            draft=False,
            prerelease=False,
        )
