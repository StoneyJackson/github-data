"""Test that legacy converter fallback has been removed."""

from github_data.github.converter_registry import ConverterRegistry


class TestNoLegacyFallback:
    """Verify backward compatibility code has been removed."""

    def test_registry_has_no_legacy_loader_method(self):
        """Registry should not have _load_legacy_converters method."""
        registry = ConverterRegistry()

        # Method should not exist
        assert not hasattr(
            registry, "_load_legacy_converters"
        ), "_load_legacy_converters method should be removed after migration"

    def test_no_converters_marked_as_legacy(self):
        """No converters should have 'legacy' as their entity."""
        registry = ConverterRegistry()

        legacy_converters = [
            name
            for name, meta in registry._converter_metadata.items()
            if meta.get("entity") == "legacy"
        ]

        assert not legacy_converters, (
            f"Found converters marked as legacy: {legacy_converters}. "
            f"All converters should be explicitly declared by entities."
        )
