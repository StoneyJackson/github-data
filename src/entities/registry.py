"""Entity registry for auto-discovery and configuration."""

import importlib
import importlib.util
from pathlib import Path
import inspect
import os
from typing import Dict
from src.entities.base import RegisteredEntity
from src.config.number_parser import NumberSpecificationParser
import logging

logger = logging.getLogger(__name__)


def _get_entities_path() -> Path:
    """Get path to entities directory.

    Returns:
        Path to src/entities directory
    """
    # Get the directory containing this file (src/entities/)
    return Path(__file__).parent


class EntityRegistry:
    """Central registry for all entities.

    Replaces ApplicationConfig with dynamic entity discovery and registration.
    Auto-discovers entities from src/entities/ directory structure.
    """

    def __init__(self) -> None:
        """Initialize registry and discover entities."""
        self._entities: Dict[str, RegisteredEntity] = {}
        self._discover_entities()

    @classmethod
    def from_environment(cls, strict: bool = False) -> "EntityRegistry":
        """Create registry from environment variables.

        Args:
            strict: If True, fail on dependency violations. If False,
                warn and auto-disable.

        Returns:
            EntityRegistry instance configured from environment
        """
        registry = cls()
        registry._load_from_environment(strict)
        return registry

    def _discover_entities(self) -> None:
        """Auto-discover entities by scanning entities/ directory.

        Looks for *EntityConfig classes in entity_config.py files.
        Registers each discovered entity with default enabled state.
        """
        entities_path = _get_entities_path()

        if not entities_path.exists():
            logger.warning(f"Entities directory not found: {entities_path}")
            return

        # Scan for entity directories
        for entity_dir in entities_path.iterdir():
            if not entity_dir.is_dir():
                continue
            if entity_dir.name.startswith("_"):
                continue

            # Look for entity_config.py
            config_file = entity_dir / "entity_config.py"
            if not config_file.exists():
                continue

            # Import the module
            module_name = f"src.entities.{entity_dir.name}.entity_config"
            try:
                spec = importlib.util.spec_from_file_location(module_name, config_file)
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find EntityConfig classes (classes ending with EntityConfig)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name.endswith("EntityConfig"):
                        # Create RegisteredEntity with default state
                        config = obj()
                        entity = RegisteredEntity(
                            config=config, enabled=config.default_value
                        )
                        self._entities[config.name] = entity
                        logger.info(f"Discovered entity: {config.name}")

            except Exception as e:
                logger.error(f"Failed to load entity from {entity_dir.name}: {e}")
                continue

    def _load_from_environment(self, strict: bool) -> None:
        """Load entity enabled values from environment variables.

        Args:
            strict: If True, fail on violations. If False, warn and correct.
        """
        for entity_name, entity in self._entities.items():
            env_var = entity.config.env_var
            value = os.getenv(env_var)

            if value is None:
                # Use default value
                entity.enabled = entity.config.default_value
                continue

            # Parse based on value_type
            if entity.config.value_type == bool:
                # Parse as boolean
                try:
                    entity.enabled = NumberSpecificationParser.parse_boolean_value(
                        value
                    )
                except ValueError as e:
                    raise ValueError(f"Environment variable {env_var}: {str(e)}")
            else:
                # Parse as Union[bool, Set[int]]
                if NumberSpecificationParser.is_boolean_value(value):
                    entity.enabled = NumberSpecificationParser.parse_boolean_value(
                        value
                    )
                else:
                    try:
                        entity.enabled = NumberSpecificationParser.parse(value)
                    except ValueError as e:
                        raise ValueError(f"Environment variable {env_var}: {str(e)}")

        # Validate dependencies after loading all values
        self._validate_dependencies(strict)

    def _validate_dependencies(self, strict: bool) -> None:
        """Validate entity dependencies.

        Args:
            strict: If True, fail on explicit conflicts.
                If False, warn and auto-disable.

        Raises:
            ValueError: If strict=True and explicit conflict detected
        """
        # TODO: Implement dependency validation in next task
        pass
