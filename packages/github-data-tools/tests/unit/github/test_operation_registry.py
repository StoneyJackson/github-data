"""Tests for GitHub operation registry."""

import pytest
from unittest.mock import Mock, patch
from github_data_tools.github.operation_registry import (
    ValidationError,
    Operation,
    GitHubOperationRegistry,
)


def test_validation_error_can_be_raised():
    """ValidationError should be a proper exception."""
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError("Test error message")

    assert "Test error message" in str(exc_info.value)


def test_operation_parses_minimal_spec():
    """Operation should parse minimal spec with only boundary_method."""
    spec = {"boundary_method": "get_repository_releases"}

    operation = Operation(
        method_name="get_repository_releases", entity_name="releases", spec=spec
    )

    assert operation.method_name == "get_repository_releases"
    assert operation.entity_name == "releases"
    assert operation.boundary_method == "get_repository_releases"
    assert operation.converter_name is None
    assert operation.cache_key_template is None


def test_operation_parses_full_spec():
    """Operation should parse all spec fields."""
    spec = {
        "boundary_method": "get_repository_releases",
        "converter": "convert_to_release",
        "cache_key_template": "releases:{repo_name}",
        "requires_retry": True,
    }

    operation = Operation(
        method_name="get_repository_releases", entity_name="releases", spec=spec
    )

    assert operation.boundary_method == "get_repository_releases"
    assert operation.converter_name == "convert_to_release"
    assert operation.cache_key_template == "releases:{repo_name}"
    assert operation.requires_retry is True


def test_operation_validation_requires_boundary_method():
    """Validation should fail if boundary_method missing."""
    spec = {
        "converter": "convert_to_release"
        # Missing 'boundary_method'
    }

    with pytest.raises(KeyError):
        Operation(
            method_name="get_repository_releases", entity_name="releases", spec=spec
        )


def test_operation_validation_checks_converter_exists():
    """Validation should fail if converter doesn't exist."""
    spec = {
        "boundary_method": "get_repository_releases",
        "converter": "nonexistent_converter",
    }

    operation = Operation(
        method_name="get_repository_releases", entity_name="releases", spec=spec
    )

    with pytest.raises(
        ValidationError, match="Converter 'nonexistent_converter' not found"
    ):
        operation.validate()


def test_operation_validation_passes_for_valid_converter():
    """Validation should pass if converter exists."""
    spec = {
        "boundary_method": "get_repository_releases",
        "converter": "convert_to_release",  # This exists in converters.py
    }

    operation = Operation(
        method_name="get_repository_releases", entity_name="releases", spec=spec
    )

    # Should not raise
    operation.validate()


def test_operation_auto_generates_cache_key_single_param():
    """Cache key should auto-generate from method name and params."""
    spec = {"boundary_method": "get_repository_releases"}
    operation = Operation("get_repository_releases", "releases", spec)

    cache_key = operation.get_cache_key(repo_name="owner/repo")

    assert cache_key == "get_repository_releases:owner/repo"


def test_operation_auto_generates_cache_key_multiple_params():
    """Cache key should include all params in alphabetical order."""
    spec = {"boundary_method": "get_issue_comments"}
    operation = Operation("get_issue_comments", "comments", spec)

    cache_key = operation.get_cache_key(repo_name="owner/repo", issue_number=123)

    # Parameters sorted alphabetically: issue_number, repo_name
    assert cache_key == "get_issue_comments:123:owner/repo"


def test_operation_uses_custom_cache_key_template():
    """Custom cache_key_template should override auto-generation."""
    spec = {
        "boundary_method": "get_repository_releases",
        "cache_key_template": "releases:{repo_name}",
    }
    operation = Operation("get_repository_releases", "releases", spec)

    cache_key = operation.get_cache_key(repo_name="owner/repo")

    assert cache_key == "releases:owner/repo"


def test_operation_cache_key_consistent_regardless_of_param_order():
    """Cache key should be consistent regardless of parameter order."""
    spec = {"boundary_method": "get_issue_comments"}
    operation = Operation("get_issue_comments", "comments", spec)

    # Call with params in different orders
    cache_key_1 = operation.get_cache_key(repo_name="owner/repo", issue_number=123)
    cache_key_2 = operation.get_cache_key(issue_number=123, repo_name="owner/repo")

    # Both should produce the same cache key
    assert cache_key_1 == cache_key_2
    # And should be deterministic (alphabetically sorted by param name)
    assert cache_key_1 == "get_issue_comments:123:owner/repo"


def test_operation_should_cache_for_read_operations():
    """Read operations should use caching."""
    spec = {"boundary_method": "get_repository_releases"}
    operation = Operation("get_repository_releases", "releases", spec)

    assert operation.should_cache() is True


def test_operation_should_not_cache_for_write_operations():
    """Write operations should skip caching."""
    spec = {"boundary_method": "create_release"}
    operation = Operation("create_release", "releases", spec)

    assert operation.should_cache() is False


def test_registry_initializes_empty():
    """Registry should initialize with empty operations."""
    with patch("github_data_core.entities.registry.EntityRegistry") as mock_entity_registry:
        mock_entity_registry.return_value._entities = {}

        registry = GitHubOperationRegistry()

        assert registry.list_operations() == []


def test_registry_discovers_operations_from_entity_configs():
    """Registry should discover operations from entity configs."""
    # Mock entity config with github_api_operations
    mock_config = Mock()
    mock_config.github_api_operations = {
        "get_repository_releases": {
            "boundary_method": "get_repository_releases",
            "converter": "convert_to_release",
        }
    }

    mock_entity = Mock()
    mock_entity.config = mock_config

    with patch("github_data_core.entities.registry.EntityRegistry") as mock_entity_registry:
        mock_entity_registry.return_value._entities = {"releases": mock_entity}

        registry = GitHubOperationRegistry()

        assert "get_repository_releases" in registry.list_operations()
        operation = registry.get_operation("get_repository_releases")
        assert operation is not None
        assert operation.entity_name == "releases"


def test_registry_skips_entities_without_github_api_operations():
    """Registry should skip entities that don't define github_api_operations."""
    mock_config = Mock(spec=[])  # No github_api_operations attribute
    mock_entity = Mock()
    mock_entity.config = mock_config

    with patch("github_data_core.entities.registry.EntityRegistry") as mock_entity_registry:
        mock_entity_registry.return_value._entities = {"some_entity": mock_entity}

        registry = GitHubOperationRegistry()

        assert registry.list_operations() == []


def test_registry_validates_all_operations_at_startup():
    """Registry should validate all specs during initialization."""
    mock_config = Mock()
    mock_config.github_api_operations = {
        "bad_operation": {
            "boundary_method": "some_method",
            "converter": "nonexistent_converter",  # Invalid!
        }
    }

    mock_entity = Mock()
    mock_entity.config = mock_config

    with patch("github_data_core.entities.registry.EntityRegistry") as mock_entity_registry:
        mock_entity_registry.return_value._entities = {"test_entity": mock_entity}

        with pytest.raises(ValidationError, match="Invalid operation spec"):
            GitHubOperationRegistry()


def test_write_operations_auto_detected():
    """Registry should auto-detect write operations."""
    mock_config = Mock()
    mock_config.github_api_operations = {
        "create_release": {"boundary_method": "create_release"},
        "update_label": {"boundary_method": "update_label"},
        "delete_issue": {"boundary_method": "delete_issue"},
        "close_issue": {"boundary_method": "close_issue"},
        "get_repository_releases": {"boundary_method": "get_repository_releases"},
    }

    mock_entity = Mock()
    mock_entity.config = mock_config

    with patch("github_data_core.entities.registry.EntityRegistry") as mock_entity_registry:
        mock_entity_registry.return_value._entities = {"test": mock_entity}

        registry = GitHubOperationRegistry()

        # Write operations should not cache
        assert registry.get_operation("create_release").should_cache() is False
        assert registry.get_operation("update_label").should_cache() is False
        assert registry.get_operation("delete_issue").should_cache() is False
        assert registry.get_operation("close_issue").should_cache() is False

        # Read operation should cache
        assert registry.get_operation("get_repository_releases").should_cache() is True
