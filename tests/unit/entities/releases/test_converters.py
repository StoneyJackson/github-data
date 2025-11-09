# tests/unit/entities/releases/test_converters.py
"""Unit tests for releases converters."""
import pytest


@pytest.mark.unit
def test_convert_to_release_loads_from_releases_entity():
    """convert_to_release should load from releases entity package."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    assert "convert_to_release" in registry.list_converters()

    metadata = registry._converter_metadata["convert_to_release"]
    assert metadata["entity"] == "releases"
    assert "entities.releases.converters" in metadata["module"]


@pytest.mark.unit
def test_convert_to_release_asset_loads_from_releases_entity():
    """convert_to_release_asset should load from releases entity package."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    assert "convert_to_release_asset" in registry.list_converters()

    metadata = registry._converter_metadata["convert_to_release_asset"]
    assert metadata["entity"] == "releases"
    assert "entities.releases.converters" in metadata["module"]


@pytest.mark.unit
def test_convert_to_release_transforms_data():
    """convert_to_release should transform raw data correctly."""
    from github_data.github.converter_registry import get_converter
    from github_data.entities.releases.models import Release

    converter = get_converter("convert_to_release")

    raw_data = {
        "id": 12345,
        "tag_name": "v1.0.0",
        "target_commitish": "main",
        "name": "Version 1.0.0",
        "body": "Release notes",
        "draft": False,
        "prerelease": False,
        "created_at": "2024-01-01T00:00:00Z",
        "published_at": "2024-01-01T12:00:00Z",
        "author": {
            "id": 1,
            "login": "testuser",
            "type": "User",
        },
        "assets": [],
        "html_url": "https://github.com/test/repo/releases/tag/v1.0.0",
    }

    result = converter(raw_data)

    assert isinstance(result, Release)
    assert result.id == 12345
    assert result.tag_name == "v1.0.0"


@pytest.mark.unit
def test_convert_to_release_asset_transforms_data():
    """convert_to_release_asset should transform raw data correctly."""
    from github_data.github.converter_registry import get_converter
    from github_data.entities.releases.models import ReleaseAsset

    converter = get_converter("convert_to_release_asset")

    raw_data = {
        "id": 67890,
        "name": "release.zip",
        "content_type": "application/zip",
        "size": 1024000,
        "download_count": 42,
        "browser_download_url": (
            "https://github.com/test/repo/releases/download/" "v1.0.0/release.zip"
        ),
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "uploader": {
            "id": 1,
            "login": "testuser",
            "type": "User",
        },
    }

    result = converter(raw_data)

    assert isinstance(result, ReleaseAsset)
    assert result.id == 67890
    assert result.name == "release.zip"
