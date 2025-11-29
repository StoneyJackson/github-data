"""Tests to verify all entities have been migrated to distributed converters."""

from github_data_core.entities.registry import EntityRegistry
from github_data_tools.github.converter_registry import ConverterRegistry


class TestConverterMigrationComplete:
    """Verify all entities have migrated to distributed converter pattern."""

    def test_all_entities_have_converter_declarations(self):
        """All entities with GitHub API operations must declare their converters."""
        entity_registry = EntityRegistry()

        # Track entities without converter declarations
        missing_converters = []

        for entity_name, entity in entity_registry._entities.items():
            config = entity.config

            # Skip entities without GitHub API operations (e.g., git_repository)
            if not hasattr(config, "github_api_operations"):
                continue

            # Check if entity has converters attribute
            if not hasattr(config, "converters"):
                missing_converters.append(entity_name)
                continue

            # Check if converters is a non-empty dict
            if not isinstance(config.converters, dict) or len(config.converters) == 0:
                missing_converters.append(entity_name)

        assert not missing_converters, (
            f"The following entities have not declared converters: "
            f"{missing_converters}. All entities with GitHub API operations "
            f"must have a 'converters' dict in their entity_config.py"
        )

    def test_all_operations_use_distributed_converters(self):
        """All operations must reference converters that come from entity packages."""
        converter_registry = ConverterRegistry()

        # Track any converters still loading from legacy location
        legacy_converters = []

        for converter_name, metadata in converter_registry._converter_metadata.items():
            if metadata.get("entity") == "legacy":
                legacy_converters.append(converter_name)

        assert not legacy_converters, (
            f"The following converters are still loading from legacy "
            f"location: {legacy_converters}. All entity-specific "
            f"converters must be moved to entity packages."
        )

    def test_only_common_converters_in_monolithic_file(self):
        """converters.py should only contain common/shared converters."""
        from github_data_tools.github import converters as legacy_module

        # Define allowed common converters
        allowed_common = {
            "convert_to_user",
            "_parse_datetime",
            "_parse_date",
            # Add other explicitly allowed common converters
        }

        # Find all convert_to_* functions in legacy module
        legacy_functions = [
            name
            for name in dir(legacy_module)
            if name.startswith("convert_to_") and callable(getattr(legacy_module, name))
        ]

        # Check for entity-specific converters still in legacy location
        entity_specific = set(legacy_functions) - allowed_common

        assert not entity_specific, (
            f"Found entity-specific converters in converters.py: {entity_specific}. "
            f"Only common/shared converters should remain in converters.py"
        )
