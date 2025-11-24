"""GitHub API operation registry for dynamic method generation."""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when operation spec validation fails."""

    pass


class Operation:
    """Represents a single GitHub API operation."""

    def __init__(self, method_name: str, entity_name: str, spec: Dict[str, Any]):
        """
        Initialize operation from spec.

        Args:
            method_name: Name of the service method (e.g., 'get_repository_releases')
            entity_name: Name of entity this operation belongs to (e.g., 'releases')
            spec: Operation specification dictionary
        """
        self.method_name = method_name
        self.entity_name = entity_name
        self.spec = spec

        # Parse spec fields
        self.boundary_method = spec["boundary_method"]
        self.converter_name = spec.get("converter")
        self.cache_key_template = spec.get("cache_key_template")
        self.requires_retry = spec.get("requires_retry", self._is_write_operation())

    def _is_write_operation(self) -> bool:
        """Detect write operations by method name prefix."""
        write_prefixes = ("create_", "update_", "delete_", "close_")
        return self.method_name.startswith(write_prefixes)

    def validate(self, converter_registry: Any = None) -> None:
        """
        Validate operation spec.

        Args:
            converter_registry: Optional ConverterRegistry instance for validation

        Raises:
            ValidationError: If spec is invalid
        """
        # boundary_method already validated in __init__ (KeyError if missing)

        # Validate converter exists if specified
        if self.converter_name:
            if not self._converter_exists(self.converter_name, converter_registry):
                raise ValidationError(f"Converter '{self.converter_name}' not found")

    def _converter_exists(
        self, converter_name: str, converter_registry: Any = None
    ) -> bool:
        """Check if converter function exists in the registry."""
        if converter_registry:
            # Use provided registry instance (avoids circular dependency during init)
            return converter_name in converter_registry._converters

        # Fallback: try to get from global registry
        try:
            from github_data.github.converter_registry import get_converter

            get_converter(converter_name)
            return True
        except Exception:
            # Converter not found or registry not ready
            return False

    def should_cache(self) -> bool:
        """Determine if this operation should use caching."""
        return not self._is_write_operation()

    def get_cache_key(self, **kwargs: Any) -> str:
        """
        Generate cache key from parameters.

        Parameters are sorted alphabetically by name to ensure consistent
        cache keys regardless of the order they are passed.

        Args:
            **kwargs: Method parameters

        Returns:
            Cache key string
        """
        if self.cache_key_template:
            return str(self.cache_key_template.format(**kwargs))

        # Auto-generate: "method_name:param1:param2:..."
        # Sort parameters by name for consistency
        param_values = ":".join(str(kwargs[k]) for k in sorted(kwargs.keys()))
        return f"{self.method_name}:{param_values}"


class GitHubOperationRegistry:
    """Registry for dynamically discovered GitHub API operations."""

    def __init__(self, skip_validation: bool = False) -> None:
        """
        Initialize registry and discover operations from entity configs.

        Args:
            skip_validation: If True, skip validation
                (used during ConverterRegistry init)
        """
        self._operations: Dict[str, Operation] = {}
        self._load_operations()
        if not skip_validation:
            self._validate_all()

    def _load_operations(self) -> None:
        """Scan all entity configs and register operations."""
        from github_data.entities.registry import EntityRegistry

        entity_registry = EntityRegistry()

        for entity_name, entity in entity_registry._entities.items():
            config = entity.config

            # Skip entities without github_api_operations
            if not hasattr(config, "github_api_operations"):
                continue

            # Register each operation
            for method_name, spec in config.github_api_operations.items():
                operation = Operation(
                    method_name=method_name, entity_name=entity_name, spec=spec
                )
                self._operations[method_name] = operation

        entity_count = len(set(op.entity_name for op in self._operations.values()))
        logger.info(
            f"Registered {len(self._operations)} GitHub API operations "
            f"from {entity_count} entities"
        )

    def _validate_all(self) -> None:
        """Validate all operation specs at startup (fail fast)."""
        for method_name, operation in self._operations.items():
            try:
                operation.validate()
            except ValidationError as e:
                raise ValidationError(
                    f"Invalid operation spec for '{method_name}' "
                    f"in entity '{operation.entity_name}': {e}"
                ) from e

    def get_operation(self, method_name: str) -> Optional[Operation]:
        """Get registered operation by method name."""
        return self._operations.get(method_name)

    def list_operations(self) -> List[str]:
        """List all registered operation names."""
        return list(self._operations.keys())
