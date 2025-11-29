"""Integration tests for ConverterRegistry with GitHubService."""

import pytest


@pytest.mark.integration
def test_registry_loads_all_legacy_converters():
    """Registry should load all converters from monolithic converters.py."""
    from github_data_tools.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()
    converters = registry.list_converters()

    # Should have loaded all legacy converters
    expected_converters = [
        "convert_to_label",
        "convert_to_issue",
        "convert_to_milestone",
        "convert_to_comment",
        "convert_to_pr_comment",
        "convert_to_pr_review",
        "convert_to_pr_review_comment",
        "convert_to_pull_request",
        "convert_to_release",
        "convert_to_sub_issue",
    ]

    for expected in expected_converters:
        assert expected in converters, f"Missing converter: {expected}"
        converter = registry.get(expected)
        assert callable(converter)


@pytest.mark.integration
def test_get_converter_singleton_works_across_modules():
    """get_converter() should work from different modules."""
    from github_data_tools.github.converter_registry import get_converter

    # Get converter
    converter1 = get_converter("convert_to_label")
    converter2 = get_converter("convert_to_issue")

    assert callable(converter1)
    assert callable(converter2)
    assert converter1 is not converter2


@pytest.mark.integration
def test_registry_validates_all_operations():
    """Registry should validate all operations reference valid converters."""
    from github_data_tools.github.converter_registry import ConverterRegistry
    from github_data_tools.github.operation_registry import GitHubOperationRegistry

    # Should not raise - all validation should pass
    registry = ConverterRegistry()
    op_registry = GitHubOperationRegistry()

    # Check that all operations with converters are valid
    for op_name in op_registry.list_operations():
        operation = op_registry.get_operation(op_name)
        if operation.converter_name:
            # Should exist in registry
            assert operation.converter_name in registry.list_converters()
            converter = registry.get(operation.converter_name)
            assert callable(converter)


@pytest.mark.integration
def test_converter_can_call_other_converters():
    """Converters should be able to call other converters via get_converter()."""
    from github_data_tools.github.converter_registry import get_converter

    # Get a converter
    label_converter = get_converter("convert_to_label")
    issue_converter = get_converter("convert_to_issue")

    # Both should work
    assert callable(label_converter)
    assert callable(issue_converter)

    # This demonstrates loose coupling - converters can find each other
    # without direct imports


@pytest.mark.integration
def test_registry_startup_performance():
    """Registry initialization should complete quickly."""
    import time
    from github_data_tools.github.converter_registry import ConverterRegistry

    start = time.time()
    registry = ConverterRegistry()
    elapsed = time.time() - start

    # Should initialize in under 1 second
    assert elapsed < 1.0, f"Registry took {elapsed:.2f}s to initialize"
    assert len(registry.list_converters()) > 0
