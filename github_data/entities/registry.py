"""Entity registry for auto-discovery and configuration."""

import importlib
import importlib.util
from pathlib import Path
import inspect
import os
from typing import Dict, Set, List
from github_data.entities.base import RegisteredEntity
from github_data.config.number_parser import NumberSpecificationParser
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
        self._explicitly_set: Set[str] = set()  # Track user-set entities
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
                # Use default value (not explicitly set)
                entity.enabled = entity.config.default_value
                continue

            # Mark as explicitly set by user
            self._explicitly_set.add(entity_name)

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
        # Iterate until no more changes (for transitive dependencies)
        changes_made = True
        while changes_made:
            changes_made = False
            for entity_name, entity in self._entities.items():
                if not entity.is_enabled():
                    continue

                # Check all dependencies
                for dep_name in entity.get_dependencies():
                    if dep_name not in self._entities:
                        logger.warning(
                            f"Entity {entity_name} depends on unknown "
                            f"entity: {dep_name}"
                        )
                        continue

                    dep_entity = self._entities[dep_name]

                    if not dep_entity.is_enabled():
                        # Dependency is disabled
                        is_explicit = entity_name in self._explicitly_set

                        if is_explicit and strict:
                            # User explicitly enabled this but dependency is disabled
                            raise ValueError(
                                f"{entity.config.env_var}=true requires "
                                f"{dep_entity.config.env_var}=true. "
                                f"Cannot enable {entity_name} without {dep_name}."
                            )
                        else:
                            # Auto-disable with warning
                            logger.warning(
                                f"Warning: {entity.config.env_var} requires "
                                f"{dep_entity.config.env_var}. Disabling {entity_name}."
                            )
                            entity.enabled = False
                            changes_made = True  # Need another pass
                            break  # Stop checking other deps for this entity

    def _topological_sort(
        self, entities: List[RegisteredEntity]
    ) -> List[RegisteredEntity]:
        """Sort entities by dependency order using topological sort.

        Args:
            entities: List of entities to sort

        Returns:
            Entities sorted so dependencies come before dependents

        Raises:
            ValueError: If circular dependency detected
        """
        # Build name -> entity mapping
        entity_map = {e.config.name: e for e in entities}

        # Build adjacency list (dependency graph)
        graph: Dict[str, List[str]] = {name: [] for name in entity_map}
        in_degree: Dict[str, int] = {name: 0 for name in entity_map}

        for name, entity in entity_map.items():
            for dep in entity.get_dependencies():
                if dep in entity_map:
                    graph[dep].append(name)
                    in_degree[name] += 1

        # Kahn's algorithm for topological sort
        queue = [name for name, degree in in_degree.items() if degree == 0]
        sorted_names = []

        while queue:
            # Sort queue for deterministic output
            queue.sort()
            current = queue.pop(0)
            sorted_names.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(sorted_names) != len(entity_map):
            remaining = set(entity_map.keys()) - set(sorted_names)
            raise ValueError(
                f"circular dependency detected among entities: {remaining}"
            )

        # Return entities in sorted order
        return [entity_map[name] for name in sorted_names]

    def get_entity(self, name: str) -> RegisteredEntity:
        """Get entity by name.

        Args:
            name: Entity name

        Returns:
            RegisteredEntity instance

        Raises:
            ValueError: If entity not found
        """
        if name not in self._entities:
            raise ValueError(f"Unknown entity: {name}")
        return self._entities[name]

    def get_enabled_entities(self) -> List[RegisteredEntity]:
        """Get all enabled entities in dependency order.

        Returns:
            List of enabled entities sorted by dependencies
        """
        enabled = [e for e in self._entities.values() if e.is_enabled()]
        return self._topological_sort(enabled)

    def get_all_entity_names(self) -> List[str]:
        """Get names of all registered entities.

        Returns:
            List of entity names
        """
        return list(self._entities.keys())
