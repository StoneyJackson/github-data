"""
Integration tests for release save/restore complete cycles.
Following docs/testing/README.md comprehensive guidelines.
"""

import pytest
import json
from unittest.mock import Mock
from datetime import datetime, timezone

from github_data.entities.releases.models import Release, ReleaseAsset
from github_data.entities.users.models import GitHubUser
from github_data.entities.releases.save_strategy import ReleasesSaveStrategy
from github_data.entities.releases.restore_strategy import ReleasesRestoreStrategy

# Required markers following docs/testing/README.md
pytestmark = [
    pytest.mark.integration,
    pytest.mark.medium,
    pytest.mark.releases,
    pytest.mark.release_integration,
    pytest.mark.save_workflow,
    pytest.mark.restore_workflow,
    pytest.mark.end_to_end,
]


class TestReleaseSaveRestoreIntegration:
    """Integration tests for complete release save/restore cycles."""

    def test_release_save_restore_cycle_basic(self, tmp_path):
        """Test basic save/restore cycle with releases only (no assets)."""
        # Setup
        save_path = tmp_path / "save"
        save_path.mkdir()

        # Create sample releases
        author = GitHubUser(
            id=1,
            login="testuser",
            avatar_url="https://avatars.githubusercontent.com/u/1?v=4",
            html_url="https://github.com/testuser",
        )

        releases = [
            Release(
                id=1,
                tag_name="v1.0.0",
                target_commitish="main",
                name="Version 1.0.0",
                body="Initial release",
                draft=False,
                prerelease=False,
                immutable=False,
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                published_at=datetime(2025, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
                author=author,
                assets=[],
                html_url="https://github.com/owner/repo/releases/tag/v1.0.0",
            ),
            Release(
                id=2,
                tag_name="v2.0.0",
                target_commitish="main",
                name="Version 2.0.0",
                body="Second release",
                draft=False,
                prerelease=False,
                immutable=False,
                created_at=datetime(2025, 2, 1, 12, 0, 0, tzinfo=timezone.utc),
                published_at=datetime(2025, 2, 1, 13, 0, 0, tzinfo=timezone.utc),
                author=author,
                assets=[],
                html_url="https://github.com/owner/repo/releases/tag/v2.0.0",
            ),
        ]

        # Mock storage service
        mock_storage = Mock()
        saved_data = []

        def mock_write_data(file_path, data):
            saved_data.extend(data)
            # Simulate actual file creation
            with open(file_path, "w") as f:
                json.dump(
                    [release.model_dump(mode="json") for release in data],
                    f,
                    default=str,
                )

        mock_storage.write.side_effect = mock_write_data
        mock_storage.read.return_value = releases

        # SAVE PHASE
        save_strategy = ReleasesSaveStrategy()

        # Simulate save operation
        save_strategy.transform(releases, {})
        release_file = save_path / "releases.json"
        mock_write_data(release_file, releases)

        # Verify file was created
        assert release_file.exists()

        # RESTORE PHASE
        restore_strategy = ReleasesRestoreStrategy()

        # Mock GitHub service for restore
        mock_github_service = Mock()
        mock_github_service.create_release.side_effect = [
            {"id": 101, "tag_name": "v1.0.0"},
            {"id": 102, "tag_name": "v2.0.0"},
        ]

        # Load data
        loaded_releases = restore_strategy.read(str(save_path), mock_storage)

        # Restore releases
        context = {}
        created = []
        for release in loaded_releases:
            transform_data = restore_strategy.transform(release, context)
            created_data = restore_strategy.write(
                mock_github_service, "test/repo", transform_data
            )
            created.append(created_data)

        # Verify restore results
        assert len(loaded_releases) == 2
        assert mock_github_service.create_release.call_count == 2
        assert created[0]["tag_name"] == "v1.0.0"
        assert created[1]["tag_name"] == "v2.0.0"

    def test_release_save_restore_with_assets(self, tmp_path):
        """Test save/restore cycle with releases containing assets."""
        # Setup
        save_path = tmp_path / "save"
        save_path.mkdir()

        # Create sample releases with assets
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
            local_path="release-assets/v1.0.0/app-linux.tar.gz",
        )

        releases = [
            Release(
                id=1,
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
                assets=[asset1],
                html_url="https://github.com/owner/repo/releases/tag/v1.0.0",
            ),
        ]

        # Mock storage service
        mock_storage = Mock()

        def mock_write_data(file_path, data):
            with open(file_path, "w") as f:
                json.dump(
                    [release.model_dump(mode="json") for release in data],
                    f,
                    default=str,
                )

        mock_storage.write.side_effect = mock_write_data
        mock_storage.read.return_value = releases

        # SAVE PHASE
        release_file = save_path / "releases.json"
        mock_write_data(release_file, releases)

        # Verify file was created
        assert release_file.exists()

        # RESTORE PHASE
        restore_strategy = ReleasesRestoreStrategy()

        # Mock GitHub service
        mock_github_service = Mock()
        mock_github_service.create_release.return_value = {
            "id": 101,
            "tag_name": "v1.0.0",
        }

        # Load and restore
        loaded_releases = restore_strategy.read(str(save_path), mock_storage)
        assert len(loaded_releases) == 1
        assert len(loaded_releases[0].assets) == 1
        assert loaded_releases[0].assets[0].name == "app-linux.tar.gz"
        assert (
            loaded_releases[0].assets[0].local_path
            == "release-assets/v1.0.0/app-linux.tar.gz"
        )

    def test_release_restore_handles_immutable(self, tmp_path):
        """Test restore adds note for immutable releases."""
        # Setup
        save_path = tmp_path / "save"
        save_path.mkdir()

        author = GitHubUser(
            id=1,
            login="testuser",
            avatar_url="https://avatars.githubusercontent.com/u/1?v=4",
            html_url="https://github.com/testuser",
        )

        releases = [
            Release(
                id=1,
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
            ),
        ]

        # Mock storage service
        mock_storage = Mock()

        def mock_write_data(file_path, data):
            with open(file_path, "w") as f:
                json.dump(
                    [release.model_dump(mode="json") for release in data],
                    f,
                    default=str,
                )

        mock_storage.write.side_effect = mock_write_data
        mock_storage.read.return_value = releases

        # SAVE PHASE
        release_file = save_path / "releases.json"
        mock_write_data(release_file, releases)

        # RESTORE PHASE
        restore_strategy = ReleasesRestoreStrategy()
        mock_github_service = Mock()
        mock_github_service.create_release.return_value = {"id": 101}

        # Load and transform
        loaded_releases = restore_strategy.read(str(save_path), mock_storage)
        transform_data = restore_strategy.transform(loaded_releases[0], {})

        # Verify immutable note added to body
        assert "immutable" in transform_data["body"].lower()
        assert "Original body" in transform_data["body"]
