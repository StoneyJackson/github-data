"""Tests for release entity models."""

import pytest
from datetime import datetime, timezone
from github_data_tools.entities.releases.models import ReleaseAsset, Release
from github_data_tools.entities.users.models import GitHubUser


# Test markers following docs/testing.md
pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
]


class TestReleaseAsset:
    """Unit tests for ReleaseAsset model."""

    def test_release_asset_basic_creation(self):
        """Test creating basic release asset."""
        uploader = GitHubUser(
            id=1,
            login="testuser",
            avatar_url="https://avatars.githubusercontent.com/u/1?v=4",
            html_url="https://github.com/testuser",
        )

        asset = ReleaseAsset(
            id=12345,
            name="app-linux.tar.gz",
            content_type="application/gzip",
            size=1024000,
            download_count=42,
            browser_download_url=(
                "https://github.com/owner/repo/releases/"
                "download/v1.0/app-linux.tar.gz"
            ),
            created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            uploader=uploader,
        )

        assert asset.id == 12345
        assert asset.name == "app-linux.tar.gz"
        assert asset.content_type == "application/gzip"
        assert asset.size == 1024000
        assert asset.download_count == 42
        assert asset.local_path is None  # Optional field

    def test_release_asset_with_local_path(self):
        """Test release asset with local_path set."""
        uploader = GitHubUser(
            id=1,
            login="testuser",
            avatar_url="https://avatars.githubusercontent.com/u/1?v=4",
            html_url="https://github.com/testuser",
        )

        asset = ReleaseAsset(
            id=12345,
            name="app-linux.tar.gz",
            content_type="application/gzip",
            size=1024000,
            download_count=42,
            browser_download_url=(
                "https://github.com/owner/repo/releases/"
                "download/v1.0/app-linux.tar.gz"
            ),
            created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            uploader=uploader,
            local_path="release-assets/v1.0.0/app-linux.tar.gz",
        )

        assert asset.local_path == "release-assets/v1.0.0/app-linux.tar.gz"


class TestRelease:
    """Unit tests for Release model."""

    def test_release_basic_creation(self):
        """Test creating basic release without assets."""
        author = GitHubUser(
            id=1,
            login="testuser",
            avatar_url="https://avatars.githubusercontent.com/u/1?v=4",
            html_url="https://github.com/testuser",
        )

        release = Release(
            id=67890,
            tag_name="v1.0.0",
            target_commitish="main",
            name="Version 1.0.0",
            body="Initial release with bug fixes",
            draft=False,
            prerelease=False,
            immutable=False,
            created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            published_at=datetime(2025, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
            author=author,
            assets=[],
            html_url="https://github.com/owner/repo/releases/tag/v1.0.0",
        )

        assert release.id == 67890
        assert release.tag_name == "v1.0.0"
        assert release.target_commitish == "main"
        assert release.name == "Version 1.0.0"
        assert release.body == "Initial release with bug fixes"
        assert release.draft is False
        assert release.prerelease is False
        assert release.immutable is False
        assert len(release.assets) == 0

    def test_release_with_assets(self):
        """Test release with multiple assets."""
        author = GitHubUser(
            id=1,
            login="testuser",
            avatar_url="https://avatars.githubusercontent.com/u/1?v=4",
            html_url="https://github.com/testuser",
        )

        uploader = GitHubUser(
            id=2,
            login="uploader",
            avatar_url="https://avatars.githubusercontent.com/u/2?v=4",
            html_url="https://github.com/uploader",
        )

        asset1 = ReleaseAsset(
            id=1,
            name="app-linux.tar.gz",
            content_type="application/gzip",
            size=1024000,
            download_count=10,
            browser_download_url="https://example.com/asset1",
            created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            uploader=uploader,
        )

        asset2 = ReleaseAsset(
            id=2,
            name="app-macos.tar.gz",
            content_type="application/gzip",
            size=2048000,
            download_count=5,
            browser_download_url="https://example.com/asset2",
            created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            uploader=uploader,
        )

        release = Release(
            id=67890,
            tag_name="v1.0.0",
            target_commitish="main",
            name="Version 1.0.0",
            body="Release with assets",
            draft=False,
            prerelease=False,
            immutable=False,
            created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            published_at=datetime(2025, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
            author=author,
            assets=[asset1, asset2],
            html_url="https://github.com/owner/repo/releases/tag/v1.0.0",
        )

        assert len(release.assets) == 2
        assert release.assets[0].name == "app-linux.tar.gz"
        assert release.assets[1].name == "app-macos.tar.gz"

    def test_release_draft_prerelease_flags(self):
        """Test draft and prerelease status flags."""
        author = GitHubUser(
            id=1,
            login="testuser",
            avatar_url="https://avatars.githubusercontent.com/u/1?v=4",
            html_url="https://github.com/testuser",
        )

        release = Release(
            id=67890,
            tag_name="v2.0.0-beta",
            target_commitish="develop",
            name="Beta Release",
            body=None,
            draft=True,
            prerelease=True,
            immutable=False,
            created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            published_at=None,  # Not published yet
            author=author,
            assets=[],
            html_url="https://github.com/owner/repo/releases/tag/v2.0.0-beta",
        )

        assert release.draft is True
        assert release.prerelease is True
        assert release.published_at is None


def test_entity_exports():
    """Test that models are properly exported from package."""
    from github_data_tools.entities.releases import Release, ReleaseAsset

    assert Release is not None
    assert ReleaseAsset is not None
