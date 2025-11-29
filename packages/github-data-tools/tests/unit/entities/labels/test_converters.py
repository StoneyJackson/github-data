# tests/unit/entities/labels/test_converters.py
"""Unit tests for labels converters."""
import pytest


@pytest.mark.unit
def test_convert_to_label_loads_from_labels_entity():
    """convert_to_label should be loadable from labels entity package."""
    from github_data_tools.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    # Should have the converter
    assert "convert_to_label" in registry.list_converters()

    # Should have metadata showing it's from labels entity
    metadata = registry._converter_metadata["convert_to_label"]
    assert metadata["entity"] == "labels"
    assert "entities.labels.converters" in metadata["module"]


@pytest.mark.unit
def test_convert_to_label_transforms_raw_data_correctly():
    """convert_to_label should transform raw GitHub API data to Label model."""
    from github_data_tools.github.converter_registry import get_converter
    from github_data_tools.entities.labels.models import Label

    converter = get_converter("convert_to_label")

    raw_data = {
        "id": 123456,
        "name": "bug",
        "color": "d73a4a",
        "description": "Something isn't working",
        "url": "https://api.github.com/repos/owner/repo/labels/bug",
    }

    result = converter(raw_data)

    assert isinstance(result, Label)
    assert result.id == 123456
    assert result.name == "bug"
    assert result.color == "d73a4a"
    assert result.description == "Something isn't working"
    assert result.url == "https://api.github.com/repos/owner/repo/labels/bug"
