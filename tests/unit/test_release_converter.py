"""Tests for release converter functions."""

import pytest
from github_data.github.converters import convert_to_release
from github_data.entities.releases.models import Release


pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.releases,
]


class TestReleaseConverter:
    """Test release data conversion from GitHub API format."""

    def test_convert_to_release_basic(self):
        """Test converting basic release without assets."""
        raw_data = {
            "id": 67890,
            "tag_name": "v1.0.0",
            "target_commitish": "main",
            "name": "Version 1.0.0",
            "body": "Initial release",
            "draft": False,
            "prerelease": False,
            "created_at": "2025-01-01T12:00:00Z",
            "published_at": "2025-01-01T13:00:00Z",
            "author": {
                "id": 1,
                "login": "testuser",
                "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
                "html_url": "https://github.com/testuser",
            },
            "assets": [],
            "html_url": "https://github.com/owner/repo/releases/tag/v1.0.0",
        }

        release = convert_to_release(raw_data)

        assert isinstance(release, Release)
        assert release.id == 67890
        assert release.tag_name == "v1.0.0"
        assert release.target_commitish == "main"
        assert release.name == "Version 1.0.0"
        assert release.body == "Initial release"
        assert release.draft is False
        assert release.prerelease is False
        assert release.immutable is False  # Default value
        assert len(release.assets) == 0

    def test_convert_to_release_with_assets(self):
        """Test converting release with multiple assets."""
        raw_data = {
            "id": 67890,
            "tag_name": "v1.0.0",
            "target_commitish": "main",
            "name": "Version 1.0.0",
            "body": "Release with assets",
            "draft": False,
            "prerelease": False,
            "created_at": "2025-01-01T12:00:00Z",
            "published_at": "2025-01-01T13:00:00Z",
            "author": {
                "id": 1,
                "login": "testuser",
                "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
                "html_url": "https://github.com/testuser",
            },
            "assets": [
                {
                    "id": 1,
                    "name": "app-linux.tar.gz",
                    "content_type": "application/gzip",
                    "size": 1024000,
                    "download_count": 10,
                    "browser_download_url": "https://example.com/asset1",
                    "created_at": "2025-01-01T12:00:00Z",
                    "updated_at": "2025-01-01T12:00:00Z",
                    "uploader": {
                        "id": 2,
                        "login": "uploader",
                        "avatar_url": "https://avatars.githubusercontent.com/u/2?v=4",
                        "html_url": "https://github.com/uploader",
                    },
                },
                {
                    "id": 2,
                    "name": "app-macos.tar.gz",
                    "content_type": "application/gzip",
                    "size": 2048000,
                    "download_count": 5,
                    "browser_download_url": "https://example.com/asset2",
                    "created_at": "2025-01-01T12:00:00Z",
                    "updated_at": "2025-01-01T12:00:00Z",
                    "uploader": {
                        "id": 2,
                        "login": "uploader",
                        "avatar_url": "https://avatars.githubusercontent.com/u/2?v=4",
                        "html_url": "https://github.com/uploader",
                    },
                },
            ],
            "html_url": "https://github.com/owner/repo/releases/tag/v1.0.0",
        }

        release = convert_to_release(raw_data)

        assert len(release.assets) == 2
        assert release.assets[0].name == "app-linux.tar.gz"
        assert release.assets[0].size == 1024000
        assert release.assets[1].name == "app-macos.tar.gz"
        assert release.assets[1].size == 2048000

    def test_convert_to_release_draft_prerelease(self):
        """Test converting draft prerelease."""
        raw_data = {
            "id": 67890,
            "tag_name": "v2.0.0-beta",
            "target_commitish": "develop",
            "name": "Beta Release",
            "body": None,
            "draft": True,
            "prerelease": True,
            "created_at": "2025-01-01T12:00:00Z",
            "published_at": None,
            "author": {
                "id": 1,
                "login": "testuser",
                "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
                "html_url": "https://github.com/testuser",
            },
            "assets": [],
            "html_url": "https://github.com/owner/repo/releases/tag/v2.0.0-beta",
        }

        release = convert_to_release(raw_data)

        assert release.draft is True
        assert release.prerelease is True
        assert release.published_at is None
        assert release.body is None

    def test_convert_to_release_immutable_flag(self):
        """Test converting release with immutable flag."""
        raw_data = {
            "id": 67890,
            "tag_name": "v1.0.0",
            "target_commitish": "main",
            "name": "Immutable Release",
            "body": "This release is immutable",
            "draft": False,
            "prerelease": False,
            "immutable": True,  # New GitHub 2025 feature
            "created_at": "2025-01-01T12:00:00Z",
            "published_at": "2025-01-01T13:00:00Z",
            "author": {
                "id": 1,
                "login": "testuser",
                "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
                "html_url": "https://github.com/testuser",
            },
            "assets": [],
            "html_url": "https://github.com/owner/repo/releases/tag/v1.0.0",
        }

        release = convert_to_release(raw_data)

        assert release.immutable is True
