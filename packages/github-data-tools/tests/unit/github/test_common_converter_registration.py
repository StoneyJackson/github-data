"""Test that common converters are properly registered."""

from github_data_tools.github.converter_registry import ConverterRegistry


class TestCommonConverterRegistration:
    """Verify common converters are registered in registry."""

    def test_user_converter_registered(self):
        """convert_to_user should be registered."""
        registry = ConverterRegistry()

        converter = registry.get("convert_to_user")
        assert callable(converter)

    def test_common_converters_have_metadata(self):
        """Common converters should have proper metadata."""
        registry = ConverterRegistry()

        # User converter should have metadata
        assert "convert_to_user" in registry._converter_metadata

        metadata = registry._converter_metadata["convert_to_user"]
        assert metadata["entity"] == "common"
        assert metadata["module"] == "github_data_tools.github.converters"
