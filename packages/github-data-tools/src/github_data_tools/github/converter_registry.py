"""
Converter Registry for distributed entity converters.

Provides centralized discovery, loading, and validation of converter functions
declared in entity configurations.
"""

import difflib
import importlib
import logging
from typing import Dict, Callable, Any

logger = logging.getLogger(__name__)


class ConverterNotFoundError(Exception):
    """Raised when a converter is not found in the registry."""

    pass


class ValidationError(Exception):
    """Raised when converter configuration is invalid."""

    pass


class ConverterRegistry:
    """
    Registry for entity data converters with eager loading.

    Scans all entity configs at initialization, imports converter modules,
    and validates all declarations. Provides fail-fast startup validation
    to catch configuration errors before any operations run.
    """

    def __init__(self) -> None:
        """Initialize registry with eager loading and validation."""
        self._converters: Dict[str, Callable] = {}
        self._converter_metadata: Dict[str, Dict[str, Any]] = {}
        self._load_all_converters()  # Eager loading
        self._validate_all()  # Fail-fast validation

        logger.info(
            f"ConverterRegistry initialized with {len(self._converters)} converters"
        )

    def get(self, name: str) -> Callable:
        """
        Get converter by name.

        Args:
            name: Converter function name (e.g., 'convert_to_release')

        Returns:
            Converter function

        Raises:
            ConverterNotFoundError: If converter not registered
        """
        if name not in self._converters:
            # Provide helpful error with suggestions for typos
            similar = difflib.get_close_matches(name, self._converters.keys())
            msg = f"Converter '{name}' not found"
            if similar:
                msg += f". Did you mean: {', '.join(similar)}?"
            raise ConverterNotFoundError(msg)

        return self._converters[name]

    def list_converters(self) -> list[str]:
        """List all registered converter names."""
        return list(self._converters.keys())

    def _load_converter(
        self, name: str, spec: Dict[str, Any], entity_name: str
    ) -> None:
        """Load a single converter from spec."""
        module_path = spec["module"]
        function_name = spec["function"]

        try:
            # Eagerly import the module
            module = importlib.import_module(module_path)
            converter_func = getattr(module, function_name)

            # Check for naming collisions
            if name in self._converters:
                existing_meta = self._converter_metadata[name]
                raise ValidationError(
                    f"Converter naming collision: '{name}' declared by both "
                    f"'{existing_meta['entity']}' and '{entity_name}'"
                )

            # Register converter
            self._converters[name] = converter_func
            self._converter_metadata[name] = {
                "entity": entity_name,
                "module": module_path,
                "target_model": spec.get("target_model"),
            }

            logger.debug(f"Loaded converter '{name}' from {entity_name}")

        except (ImportError, AttributeError) as e:
            raise ValidationError(
                f"Failed to load converter '{name}' from entity '{entity_name}': {e}"
            ) from e

    def _load_all_converters(self) -> None:
        """Scan EntityRegistry and eagerly import all declared converters."""
        from pathlib import Path
        from github_data_core.entities.registry import EntityRegistry
        from github_data_tools.github.common_converters_config import (
            CommonConvertersConfig,
        )

        # Load common converters first
        common_config = CommonConvertersConfig()
        if isinstance(common_config.converters, dict):
            for converter_name, spec in common_config.converters.items():
                if isinstance(spec, dict):
                    self._load_converter(converter_name, spec, "common")

        # Load entity-specific converters
        # Point to github-data-tools entities directory
        entities_dir = Path(__file__).parent.parent / "entities"
        entity_registry = EntityRegistry(entities_dir=entities_dir)

        for entity_name, entity in entity_registry._entities.items():
            config = entity.config

            # Skip entities without converter declarations
            if not hasattr(config, "converters"):
                logger.debug(f"Entity '{entity_name}' has no converters declared")
                continue

            # Import and register each converter
            converters_dict = config.converters
            if isinstance(converters_dict, dict):
                for converter_name, spec in converters_dict.items():
                    if isinstance(spec, dict):
                        self._load_converter(converter_name, spec, entity_name)

    def _validate_all(self) -> None:
        """Comprehensive validation at startup (fail-fast)."""
        # 1. Validate all converters are callable
        for name, func in self._converters.items():
            if not callable(func):
                meta = self._converter_metadata[name]  # type: ignore[unreachable]
                raise ValidationError(
                    f"Converter '{name}' from entity '{meta['entity']}' is not callable"
                )

        # 2. Cross-validate: operations reference valid converters
        # We pass self to the operation registry's validation
        # to avoid circular dependency
        from github_data_tools.github.operation_registry import (
            GitHubOperationRegistry,
        )

        # Create operation registry but skip its validation
        # (it will validate with our registry)
        operation_registry = GitHubOperationRegistry(skip_validation=True)

        # Now validate all operations with this converter registry instance
        for op_name in operation_registry.list_operations():
            operation = operation_registry.get_operation(op_name)
            if operation and operation.converter_name:
                operation.validate(converter_registry=self)


# Module-level singleton instance
_registry_instance = None


def get_converter(name: str) -> Callable:
    """
    Get converter by name from the global registry.

    This is a convenience function for use within converter implementations
    that need to call other converters.

    Args:
        name: Converter function name

    Returns:
        Converter function
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ConverterRegistry()
    return _registry_instance.get(name)
