"""Tests for GitHubService dynamic method generation."""

import pytest
from unittest.mock import Mock, patch
from github_data.github.service import GitHubService


def test_github_service_initializes_with_registry():
    """GitHubService should initialize operation registry."""
    mock_boundary = Mock()

    with patch(
        "github_data.github.service.GitHubOperationRegistry"
    ) as mock_registry_class:
        mock_registry = Mock()
        mock_registry.list_operations.return_value = ["get_repository_releases"]
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=False)

        # Registry should be initialized
        mock_registry_class.assert_called_once()
        assert service._operation_registry == mock_registry


def test_dynamic_method_generation_for_registered_operation():
    """Service should dynamically generate methods from registry."""
    mock_boundary = Mock()
    mock_boundary.get_test_data.return_value = [{"id": 1, "name": "test"}]

    # Patch registry to return a test operation
    with patch(
        "github_data.github.service.GitHubOperationRegistry"
    ) as mock_registry_class:
        mock_operation = Mock()
        mock_operation.method_name = "get_test_data"
        mock_operation.entity_name = "test_entity"
        mock_operation.boundary_method = "get_test_data"
        mock_operation.converter_name = None
        mock_operation.should_cache.return_value = False
        mock_operation.spec = {"boundary_method": "get_test_data"}

        mock_registry = Mock()
        mock_registry.list_operations.return_value = ["get_test_data"]
        mock_registry.get_operation.return_value = mock_operation
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=False)

        # Method should be dynamically available
        assert hasattr(service, "get_test_data")

        # Should be callable
        service.get_test_data(repo_name="owner/repo")

        # Boundary method should have been called
        mock_boundary.get_test_data.assert_called_once_with(repo_name="owner/repo")


def test_unknown_method_raises_helpful_error():
    """Unknown method should raise AttributeError with available operations."""
    mock_boundary = Mock()

    with patch(
        "github_data.github.service.GitHubOperationRegistry"
    ) as mock_registry_class:
        mock_registry = Mock()
        mock_registry.list_operations.return_value = ["get_repository_releases"]
        mock_registry.get_operation.return_value = None  # Method not found
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=False)

        with pytest.raises(AttributeError) as exc_info:
            service.nonexistent_method()

        error_msg = str(exc_info.value)
        assert "nonexistent_method" in error_msg
        assert "Available operations" in error_msg


def test_dynamic_method_applies_converter():
    """Dynamic method should apply converter if specified."""
    from github_data.entities.releases.models import Release

    mock_boundary = Mock()
    mock_boundary.get_test_releases.return_value = [
        {
            "id": 1,
            "tag_name": "v1.0",
            "name": "Release 1.0",
            "body": "",
            "draft": False,
            "prerelease": False,
            "created_at": "2023-01-01T00:00:00Z",
            "published_at": "2023-01-01T00:00:00Z",
            "html_url": "https://test.com",
            "assets": [],
            "target_commitish": "main",
            "author": {
                "login": "test",
                "id": 1,
                "avatar_url": "",
                "html_url": "",
                "type": "User",
            },
        }
    ]

    with patch(
        "github_data.github.service.GitHubOperationRegistry"
    ) as mock_registry_class:
        mock_operation = Mock()
        mock_operation.method_name = "get_test_releases"
        mock_operation.entity_name = "releases"
        mock_operation.boundary_method = "get_test_releases"
        mock_operation.converter_name = "convert_to_release"
        mock_operation.should_cache.return_value = False
        mock_operation.spec = {
            "boundary_method": "get_test_releases",
            "converter": "convert_to_release",
        }

        mock_registry = Mock()
        mock_registry.list_operations.return_value = ["get_test_releases"]
        mock_registry.get_operation.return_value = mock_operation
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=False)

        result = service.get_test_releases(repo_name="owner/repo")

        # Should return converted objects
        assert len(result) == 1
        assert isinstance(result[0], Release)
        assert result[0].tag_name == "v1.0"


def test_dynamic_method_uses_caching_for_read_operations():
    """Dynamic read operations should use caching logic."""
    mock_boundary = Mock()
    mock_boundary.get_test_data.return_value = [{"id": 1}]

    with patch(
        "github_data.github.service.GitHubOperationRegistry"
    ) as mock_registry_class:
        mock_operation = Mock()
        mock_operation.method_name = "get_test_data"
        mock_operation.entity_name = "test_entity"
        mock_operation.boundary_method = "get_test_data"
        mock_operation.converter_name = None
        mock_operation.should_cache.return_value = True
        mock_operation.get_cache_key.return_value = "get_test_data:owner/repo"
        mock_operation.spec = {"boundary_method": "get_test_data"}

        mock_registry = Mock()
        mock_registry.list_operations.return_value = ["get_test_data"]
        mock_registry.get_operation.return_value = mock_operation
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=True)

        # Patch _execute_with_cross_cutting_concerns to verify cache_key
        with patch.object(
            service,
            "_execute_with_cross_cutting_concerns",
            wraps=service._execute_with_cross_cutting_concerns,
        ) as mock_execute:
            service.get_test_data(repo_name="owner/repo")

            # Verify that caching logic was invoked with a cache key
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args
            assert call_args.kwargs["cache_key"] == "get_test_data:owner/repo"


def test_dynamic_method_skips_caching_for_write_operations():
    """Dynamic write operations should not use caching."""
    mock_boundary = Mock()
    mock_boundary.create_test_data.return_value = {"id": 1, "name": "test"}

    with patch(
        "github_data.github.service.GitHubOperationRegistry"
    ) as mock_registry_class:
        mock_operation = Mock()
        mock_operation.method_name = "create_test_data"
        mock_operation.entity_name = "test_entity"
        mock_operation.boundary_method = "create_test_data"
        mock_operation.converter_name = None
        mock_operation.should_cache.return_value = False
        mock_operation.spec = {"boundary_method": "create_test_data"}

        mock_registry = Mock()
        mock_registry.list_operations.return_value = ["create_test_data"]
        mock_registry.get_operation.return_value = mock_operation
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=True)

        # Multiple calls should always hit boundary
        service.create_test_data(repo_name="owner/repo", name="test")
        service.create_test_data(repo_name="owner/repo", name="test")

        assert mock_boundary.create_test_data.call_count == 2


def test_all_entity_operations_are_registered(validate_github_service_registry):
    """Integration test: all entity operations should be registered."""
    service = validate_github_service_registry

    # Registry should exist and be initialized
    assert service._operation_registry is not None

    # Get operations list (may be empty if no entities have been migrated yet)
    operations = service._operation_registry.list_operations()

    # The fixture validates that all declared operations are properly registered
    # If this test passes, the validation succeeded
    # Once entities are migrated, operations will be > 0
    assert isinstance(operations, list)


def test_explicit_method_overrides_registry():
    """Explicit service methods should take precedence over registry (escape hatch)."""
    mock_boundary = Mock()
    mock_boundary.get_test_data.return_value = [{"id": 1, "name": "boundary"}]

    with patch(
        "github_data.github.service.GitHubOperationRegistry"
    ) as mock_registry_class:
        # Registry has an operation for "custom_explicit_method"
        mock_operation = Mock()
        mock_operation.method_name = "custom_explicit_method"
        mock_operation.entity_name = "test_entity"
        mock_operation.boundary_method = "get_test_data"
        mock_operation.converter_name = None
        mock_operation.should_cache.return_value = False
        mock_operation.spec = {"boundary_method": "get_test_data"}

        mock_registry = Mock()
        mock_registry.list_operations.return_value = ["custom_explicit_method"]
        mock_registry.get_operation.return_value = mock_operation
        mock_registry_class.return_value = mock_registry

        # Create service
        service = GitHubService(boundary=mock_boundary, caching_enabled=False)

        # Add an explicit method to the service instance (simulating escape hatch)
        def explicit_implementation():
            return "explicit_result"

        service.custom_explicit_method = explicit_implementation

        # Call the method - should use explicit implementation, not registry
        result = service.custom_explicit_method()

        # Should return result from explicit method, not registry
        assert result == "explicit_result"

        # Boundary should NOT have been called (proving registry was bypassed)
        mock_boundary.get_test_data.assert_not_called()

        # Registry get_operation should NOT have been called
        # (because __getattr__ is not invoked when attribute exists)
        mock_registry.get_operation.assert_not_called()
