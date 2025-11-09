"""Unit tests for ConverterRegistry."""

import pytest


def test_converter_not_found_error_is_exception():
    """ConverterNotFoundError should be an Exception subclass."""
    from github_data.github.converter_registry import ConverterNotFoundError

    error = ConverterNotFoundError("test message")
    assert isinstance(error, Exception)
    assert str(error) == "test message"


def test_validation_error_is_exception():
    """ValidationError should be an Exception subclass."""
    from github_data.github.converter_registry import ValidationError

    error = ValidationError("invalid config")
    assert isinstance(error, Exception)
    assert str(error) == "invalid config"


def test_converter_registry_instantiates():
    """ConverterRegistry should instantiate successfully."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    assert registry is not None
    assert hasattr(registry, "_converters")
    assert hasattr(registry, "_converter_metadata")
    assert isinstance(registry._converters, dict)
    assert isinstance(registry._converter_metadata, dict)


def test_get_returns_registered_converter():
    """get() should return registered converter function."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    # Manually register a test converter
    def test_converter(data):
        return "converted"

    registry._converters["test_converter"] = test_converter

    result = registry.get("test_converter")
    assert result is test_converter
    assert callable(result)


def test_get_raises_not_found_for_missing_converter():
    """get() should raise ConverterNotFoundError for unregistered converter."""
    from github_data.github.converter_registry import (
        ConverterRegistry,
        ConverterNotFoundError,
    )

    registry = ConverterRegistry()

    with pytest.raises(ConverterNotFoundError) as exc_info:
        registry.get("nonexistent_converter")

    assert "nonexistent_converter" in str(exc_info.value)
    assert "not found" in str(exc_info.value)


def test_get_suggests_similar_names_for_typos():
    """get() should suggest similar converter names for typos."""
    from github_data.github.converter_registry import (
        ConverterRegistry,
        ConverterNotFoundError,
    )

    registry = ConverterRegistry()
    registry._converters["convert_to_label"] = lambda x: x
    registry._converters["convert_to_release"] = lambda x: x

    with pytest.raises(ConverterNotFoundError) as exc_info:
        # Typo: "lable" instead of "label"
        registry.get("convert_to_lable")

    error_msg = str(exc_info.value)
    assert "Did you mean" in error_msg
    assert "convert_to_label" in error_msg


def test_list_converters_returns_all_names():
    """list_converters() should return all registered converter names."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    # Registry now auto-loads on init, so add custom converters
    registry._converters["converter_a"] = lambda x: x
    registry._converters["converter_b"] = lambda x: x
    registry._converters["converter_c"] = lambda x: x

    names = registry.list_converters()

    assert isinstance(names, list)
    assert "converter_a" in names
    assert "converter_b" in names
    assert "converter_c" in names
    # Should have more than 3 (legacy + our custom ones)
    assert len(names) > 3


def test_list_converters_auto_loads_on_init():
    """Registry should auto-load converters on instantiation."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    names = registry.list_converters()

    assert isinstance(names, list)
    # Should have auto-loaded legacy converters at minimum
    assert len(names) > 0
    assert any(name.startswith("convert_to_") for name in names)


def test_load_converter_imports_from_spec():
    """_load_converter() should import converter from module spec."""
    from github_data.github.converter_registry import ConverterRegistry

    # Create registry (will auto-load)
    registry = ConverterRegistry()

    # Clear converters to test _load_converter in isolation
    registry._converters.clear()
    registry._converter_metadata.clear()

    # Using entity converters module
    spec = {
        "module": "github_data.entities.labels.converters",
        "function": "convert_to_label",
        "target_model": "Label",
    }

    registry._load_converter("convert_to_label", spec, "labels")

    # Should have loaded the converter
    assert "convert_to_label" in registry.list_converters()
    converter = registry.get("convert_to_label")
    assert callable(converter)

    # Should have metadata
    metadata = registry._converter_metadata["convert_to_label"]
    assert metadata["entity"] == "labels"
    assert metadata["module"] == "github_data.entities.labels.converters"
    assert metadata["target_model"] == "Label"


def test_load_converter_detects_naming_collisions():
    """_load_converter() should detect when two entities declare same name."""
    from github_data.github.converter_registry import ConverterRegistry, ValidationError

    # Create registry (will auto-load)
    registry = ConverterRegistry()

    # Clear converters to test _load_converter in isolation
    registry._converters.clear()
    registry._converter_metadata.clear()

    # Load first converter
    spec = {
        "module": "github_data.entities.labels.converters",
        "function": "convert_to_label",
        "target_model": "Label",
    }
    registry._load_converter("convert_to_label", spec, "labels")

    # Try to load another converter with same name from different entity
    duplicate_spec = {
        "module": "github_data.entities.issues.converters",
        "function": "convert_to_issue",  # Different function, same name
        "target_model": "Issue",
    }

    with pytest.raises(ValidationError) as exc_info:
        registry._load_converter("convert_to_label", duplicate_spec, "issues")

    error_msg = str(exc_info.value)
    assert "naming collision" in error_msg.lower()
    assert "labels" in error_msg
    assert "issues" in error_msg


def test_load_converter_raises_validation_error_for_bad_module():
    """_load_converter() should raise ValidationError for missing module."""
    from github_data.github.converter_registry import ConverterRegistry, ValidationError

    registry = ConverterRegistry()

    spec = {
        "module": "nonexistent.module.path",
        "function": "convert_to_something",
        "target_model": "Something",
    }

    with pytest.raises(ValidationError) as exc_info:
        registry._load_converter("convert_to_something", spec, "test_entity")

    error_msg = str(exc_info.value)
    assert "Failed to load converter" in error_msg
    assert "test_entity" in error_msg


def test_load_converter_raises_validation_error_for_bad_function():
    """_load_converter() should raise ValidationError for missing function."""
    from github_data.github.converter_registry import ConverterRegistry, ValidationError

    registry = ConverterRegistry()

    spec = {
        "module": "github_data.github.converters",  # Module exists
        "function": "nonexistent_function",  # Function doesn't
        "target_model": "Something",
    }

    with pytest.raises(ValidationError) as exc_info:
        registry._load_converter("bad_converter", spec, "test_entity")

    error_msg = str(exc_info.value)
    assert "Failed to load converter" in error_msg


def test_load_all_converters_discovers_entity_converters():
    """_load_all_converters() should scan EntityRegistry and load converters."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    # Should have loaded converters from entity configs during init
    converters = registry.list_converters()

    # Check for converters from entities that have converter configs
    assert len(converters) > 0

    # Should have entity converters
    assert any(name.startswith("convert_to_") for name in converters)


def test_load_all_converters_skips_entities_without_converters():
    """_load_all_converters() should skip entities with no converter config."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    # Should handle gracefully during init (no errors)
    # Should still have some converters loaded from entities with converters
    assert len(registry.list_converters()) > 0


def test_registry_initialization_loads_all_converters():
    """Registry should load all converters on instantiation."""
    from github_data.github.converter_registry import ConverterRegistry

    # Simply instantiating should load everything
    registry = ConverterRegistry()

    # Should have loaded converters
    converters = registry.list_converters()
    assert len(converters) > 0

    # Should have entity converters
    assert "convert_to_label" in converters
    assert "convert_to_issue" in converters
    assert "convert_to_milestone" in converters


def test_common_converters_are_registered():
    """Common converters should be registered with 'common' entity."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    # Common converters that all entities use
    common_converter_names = [
        "convert_to_user",
        "_parse_datetime",
        "_extract_pr_number_from_url",
    ]

    for name in common_converter_names:
        assert name in registry._converters, f"Common converter {name} not found"

        meta = registry._converter_metadata[name]
        assert (
            meta["entity"] == "common"
        ), f"Converter {name} should be from 'common' entity, not {meta['entity']}"
        assert (
            meta["module"] == "github_data.github.converters"
        ), f"Converter {name} should be from converters module"


def test_validate_all_checks_converters_are_callable():
    """_validate_all() should verify all converters are callable."""
    from github_data.github.converter_registry import ConverterRegistry, ValidationError

    registry = ConverterRegistry()

    # Add a non-callable "converter"
    registry._converters["bad_converter"] = "not a function"
    registry._converter_metadata["bad_converter"] = {
        "entity": "test",
        "module": "test.module",
        "target_model": None,
    }

    with pytest.raises(ValidationError) as exc_info:
        registry._validate_all()

    error_msg = str(exc_info.value)
    assert "not callable" in error_msg.lower()
    assert "bad_converter" in error_msg


def test_validate_all_checks_operation_converter_references():
    """_validate_all() should verify operations reference valid converters."""
    from github_data.github.converter_registry import ConverterRegistry
    from github_data.github.operation_registry import (
        GitHubOperationRegistry,
        ValidationError,
    )

    # First, create a working registry
    registry = ConverterRegistry()

    # Get an operation that references a converter
    op_registry = GitHubOperationRegistry()
    operations = op_registry.list_operations()

    # Find an operation with a converter
    op_with_converter = None
    for op_name in operations:
        op = op_registry.get_operation(op_name)
        if op.converter_name:
            op_with_converter = op
            break

    # If we found an operation with a converter, it should be valid
    if op_with_converter:
        # Should not raise - converter should exist
        registry._validate_all()

        # Now test invalid case - remove the converter
        converter_name = op_with_converter.converter_name
        if converter_name in registry._converters:
            del registry._converters[converter_name]

            with pytest.raises(ValidationError) as exc_info:
                registry._validate_all()

            error_msg = str(exc_info.value)
            assert "not found" in error_msg.lower()
            assert converter_name in error_msg


def test_registry_validates_on_initialization():
    """Registry should run full validation on instantiation."""
    from github_data.github.converter_registry import ConverterRegistry

    # Should not raise - all converters and operations should be valid
    registry = ConverterRegistry()

    # Should have converters
    assert len(registry.list_converters()) > 0

    # All should be callable
    for name in registry.list_converters():
        converter = registry.get(name)
        assert callable(converter)


def test_get_converter_function_returns_converter():
    """get_converter() module function should return converter from singleton."""
    from github_data.github.converter_registry import get_converter

    # Should work without explicitly creating registry
    converter = get_converter("convert_to_label")

    assert callable(converter)
    assert converter is not None


def test_get_converter_uses_singleton_registry():
    """get_converter() should reuse the same registry instance."""
    from github_data.github import converter_registry

    # Reset singleton for clean test
    converter_registry._registry_instance = None

    # First call creates registry
    converter1 = converter_registry.get_converter("convert_to_label")
    registry1 = converter_registry._registry_instance

    # Second call reuses same registry
    converter2 = converter_registry.get_converter("convert_to_issue")
    registry2 = converter_registry._registry_instance

    # Should be same registry instance
    assert registry1 is registry2

    # Both converters should work
    assert callable(converter1)
    assert callable(converter2)


def test_get_converter_raises_for_unknown_converter():
    """get_converter() should raise ConverterNotFoundError for invalid name."""
    from github_data.github.converter_registry import (
        get_converter,
        ConverterNotFoundError,
    )

    with pytest.raises(ConverterNotFoundError):
        get_converter("nonexistent_converter")
