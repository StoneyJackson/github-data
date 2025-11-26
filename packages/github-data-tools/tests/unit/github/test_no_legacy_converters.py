"""Test that legacy converter loading has been removed."""

from github_data_tools.github.converter_registry import ConverterRegistry


class TestNoLegacyConverters:
    """Verify legacy converter loading is removed."""

    def test_registry_has_no_legacy_load_method(self):
        """ConverterRegistry should not have _load_legacy_converters method."""
        registry = ConverterRegistry()

        # Method should not exist
        assert not hasattr(
            registry, "_load_legacy_converters"
        ), "Legacy converter loading method should be removed"

    def test_no_legacy_converters_in_metadata(self):
        """No converters should be marked as 'legacy' entity."""
        registry = ConverterRegistry()

        legacy_converters = [
            name
            for name, meta in registry._converter_metadata.items()
            if meta.get("entity") == "legacy"
        ]

        assert (
            len(legacy_converters) == 0
        ), f"Found legacy converters: {legacy_converters}"

    def test_all_converters_from_entity_packages(self):
        """All converters should come from entity packages or common module."""
        registry = ConverterRegistry()

        for name, meta in registry._converter_metadata.items():
            module = meta["module"]
            entity = meta["entity"]

            # Should be either from entity package or common converters
            assert (
                "github_data.entities." in module
                or module == "github_data_tools.github.converters"
                and entity == "common"
            ), f"Converter {name} from unexpected location: {module}"

    def test_entity_converters_not_in_monolithic_file(self):
        """Monolithic converters.py should only contain common converters."""
        import inspect
        from github_data_tools.github import converters as converters_module

        # Get all functions from the module
        functions = [
            name
            for name, obj in inspect.getmembers(converters_module)
            if inspect.isfunction(obj) and not name.startswith("_")
        ]

        # Entity-specific converters that should NOT be in this file
        entity_specific = [
            "convert_to_label",
            "convert_to_issue",
            "convert_to_comment",
            "convert_to_milestone",
            "convert_to_release",
            "convert_to_release_asset",
            "convert_to_pull_request",
            "convert_to_pr_comment",
            "convert_to_pr_review",
            "convert_to_pr_review_comment",
            "convert_to_sub_issue",
        ]

        found_entity_specific = [name for name in functions if name in entity_specific]

        assert len(found_entity_specific) == 0, (
            f"Found entity-specific converters in monolithic file: "
            f"{found_entity_specific}"
        )
