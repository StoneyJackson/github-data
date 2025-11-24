"""Tests for release restore strategy."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timezone
from github_data.entities.releases.restore_strategy import ReleasesRestoreStrategy
from github_data.entities.releases.models import Release
from github_data.entities.users.models import GitHubUser


pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.restore_workflow,
]


class TestReleasesRestoreStrategy:
    """Test release restore strategy implementation."""

    def test_get_entity_name(self):
        """Test entity name is correct."""
        strategy = ReleasesRestoreStrategy()
        assert strategy.get_entity_name() == "releases"

    def test_get_dependencies(self):
        """Test releases have no dependencies."""
        strategy = ReleasesRestoreStrategy()
        assert strategy.get_dependencies() == []

    def test_transform_basic_release(self):
        """Test transforming basic release for API."""
        strategy = ReleasesRestoreStrategy()

        author = GitHubUser(
            id=1,
            login="testuser",
            avatar_url="https://avatars.githubusercontent.com/u/1?v=4",
            html_url="https://github.com/testuser",
        )

        release = Release(
            id=123,
            tag_name="v1.0.0",
            target_commitish="main",
            name="Version 1.0.0",
            body="Release notes",
            draft=False,
            prerelease=False,
            immutable=False,
            created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            published_at=datetime(2025, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
            author=author,
            assets=[],
            html_url="https://github.com/owner/repo/releases/tag/v1.0.0",
        )

        result = strategy.transform(release, {})

        assert result["tag_name"] == "v1.0.0"
        assert result["target_commitish"] == "main"
        assert result["name"] == "Version 1.0.0"
        assert result["body"] == "Release notes"
        assert result["draft"] is False
        assert result["prerelease"] is False

    def test_transform_with_optional_fields(self):
        """Test transforming release with optional fields."""
        strategy = ReleasesRestoreStrategy()

        author = GitHubUser(
            id=1,
            login="testuser",
            avatar_url="https://avatars.githubusercontent.com/u/1?v=4",
            html_url="https://github.com/testuser",
        )

        release = Release(
            id=123,
            tag_name="v1.0.0",
            target_commitish="main",
            name=None,  # Optional
            body=None,  # Optional
            draft=True,
            prerelease=True,
            immutable=False,
            created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            published_at=None,  # Optional for drafts
            author=author,
            assets=[],
            html_url="https://github.com/owner/repo/releases/tag/v1.0.0",
        )

        result = strategy.transform(release, {})

        assert result["tag_name"] == "v1.0.0"
        assert result["target_commitish"] == "main"
        assert result.get("name") is None
        assert result.get("body") is None
        assert result["draft"] is True
        assert result["prerelease"] is True

    def test_transform_immutable_release(self):
        """Test transforming immutable release adds note to body."""
        strategy = ReleasesRestoreStrategy()

        author = GitHubUser(
            id=1,
            login="testuser",
            avatar_url="https://avatars.githubusercontent.com/u/1?v=4",
            html_url="https://github.com/testuser",
        )

        release = Release(
            id=123,
            tag_name="v1.0.0",
            target_commitish="main",
            name="Immutable Release",
            body="Original body",
            draft=False,
            prerelease=False,
            immutable=True,  # Cannot set via API
            created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            published_at=datetime(2025, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
            author=author,
            assets=[],
            html_url="https://github.com/owner/repo/releases/tag/v1.0.0",
        )

        result = strategy.transform(release, {})

        assert "immutable" in result["body"].lower()
        assert "Original body" in result["body"]

    def test_write_creates_release(self):
        """Test write method creates release via service."""
        strategy = ReleasesRestoreStrategy()
        mock_service = Mock()

        mock_service.create_release.return_value = {
            "id": 999,
            "tag_name": "v1.0.0",
            "name": "Version 1.0.0",
        }

        entity_data = {
            "tag_name": "v1.0.0",
            "target_commitish": "main",
            "name": "Version 1.0.0",
            "body": "Release notes",
            "draft": False,
            "prerelease": False,
        }

        result = strategy.write(mock_service, "owner/repo", entity_data)

        assert result["id"] == 999
        assert result["tag_name"] == "v1.0.0"
        mock_service.create_release.assert_called_once_with(
            repo_name="owner/repo",
            tag_name="v1.0.0",
            target_commitish="main",
            name="Version 1.0.0",
            body="Release notes",
            draft=False,
            prerelease=False,
        )

    def test_write_handles_existing_tag(self):
        """Test write method handles tag already exists error."""
        strategy = ReleasesRestoreStrategy()
        mock_service = Mock()

        mock_service.create_release.side_effect = Exception("tag already exists")

        entity_data = {
            "tag_name": "v1.0.0",
            "target_commitish": "main",
            "name": "Version 1.0.0",
            "body": "Release notes",
            "draft": False,
            "prerelease": False,
        }

        result = strategy.write(mock_service, "owner/repo", entity_data)

        # Should return mock response and log warning
        assert result["tag_name"] == "v1.0.0"
        assert result["id"] == -1
