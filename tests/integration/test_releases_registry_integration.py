"""Integration tests for releases entity with operation registry."""

import pytest
from unittest.mock import Mock
from github_data.github.service import GitHubService


pytestmark = [
    pytest.mark.integration,
    pytest.mark.fast,
]


def test_releases_operations_registered_in_service():
    """Releases operations should be auto-discovered and registered."""
    mock_boundary = Mock()
    service = GitHubService(boundary=mock_boundary, caching_enabled=False)

    # Verify releases operations are registered
    registry = service._operation_registry
    assert "get_repository_releases" in registry.list_operations()
    assert "create_release" in registry.list_operations()

    # Verify operation metadata
    get_op = registry.get_operation("get_repository_releases")
    assert get_op.entity_name == "releases"
    assert get_op.boundary_method == "get_repository_releases"
    assert get_op.converter_name == "convert_to_release"


def test_releases_methods_still_work():
    """Releases methods should still work (explicit methods for now)."""
    mock_boundary = Mock()
    mock_boundary.get_repository_releases.return_value = [
        {
            "id": 123,
            "tag_name": "v1.0.0",
            "name": "Release 1.0.0",
            "body": "First release",
            "draft": False,
            "prerelease": False,
            "created_at": "2023-01-01T00:00:00Z",
            "published_at": "2023-01-01T00:00:00Z",
            "html_url": "https://github.com/test/repo/releases/tag/v1.0.0",
            "target_commitish": "main",
            "assets": [],
            "author": {
                "login": "testuser",
                "id": 1,
                "avatar_url": "https://avatars.githubusercontent.com/u/1",
                "html_url": "https://github.com/testuser",
                "type": "User",
            },
        }
    ]

    service = GitHubService(boundary=mock_boundary, caching_enabled=False)

    # Explicit method exists (takes precedence over registry)
    # This verifies nothing broke with registry addition
    result = service.get_repository_releases(repo_name="test/repo")

    # Should call boundary method
    mock_boundary.get_repository_releases.assert_called_once()

    # Should return data (explicit method doesn't convert currently)
    assert len(result) == 1


def test_registry_can_generate_releases_methods():
    """Registry should be capable of generating releases methods."""
    mock_boundary = Mock()

    service = GitHubService(boundary=mock_boundary, caching_enabled=False)
    registry = service._operation_registry

    # Get operation from registry
    get_op = registry.get_operation("get_repository_releases")
    create_op = registry.get_operation("create_release")

    # Verify operations are properly configured
    assert get_op.should_cache() is True  # Read operation
    assert create_op.should_cache() is False  # Write operation

    assert get_op.converter_name == "convert_to_release"
    assert create_op.converter_name == "convert_to_release"
