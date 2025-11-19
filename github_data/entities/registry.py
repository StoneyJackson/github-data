"""Entity registry for auto-discovery and configuration."""

import importlib
import importlib.util
from pathlib import Path
import inspect
import os
from types import ModuleType
from typing import Dict, Set, List, Tuple, Any, Optional, Iterator
from github_data.entities.base import RegisteredEntity
from github_data.config.number_parser import NumberSpecificationParser
import logging

logger = logging.getLogger(__name__)


class EntityRegistry:
    """Central registry for all entities.

    Replaces ApplicationConfig with dynamic entity discovery and registration.
    Auto-discovers entities from src/entities/ directory structure.
    """

    @classmethod
    def from_environment(cls, is_strict: bool = False) -> "EntityRegistry":
        """Create registry from environment variables.

        Args:
            is_strict: If True, fail on dependency violations. If False,
                warn and auto-disable.

        Returns:
            EntityRegistry instance configured from environment
        """
        registry = cls()
        registry._load_from_environment(is_strict)
        return registry

    def __init__(self, entities_dir: Optional[Path] = None) -> None:
        """Initialize registry and discover entities."""
        self._entities_dir: Optional[Path] = entities_dir
        self._entities: Dict[str, RegisteredEntity] = {}
        self._explicitly_set: Set[str] = set()  # Track user-set entities
        self._discover_entities()

    def _discover_entities(self) -> None:
        discovery = EntityDiscovery(self._entities_dir)
        discovery.discover()
        self._entities = discovery.get_entities()

    def _load_from_environment(self, is_strict: bool) -> None:
        loader = EntityEnvironmentLoader(self._entities, self._explicitly_set)
        loader.load(is_strict)

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
        sorter = TopologicalSorter(entities)
        return sorter.sort()

    def get_all_entity_names(self) -> List[str]:
        """Get names of all registered entities.

        Returns:
            List of entity names
        """
        return list(self._entities.keys())


class TopologicalSorter:
    """Sorts entities by dependency order using Kahn's algorithm.

    Performs topological sorting to ensure dependencies come before dependents.
    Detects circular dependencies and raises an error if found.
    """

    def __init__(self, entities: List[RegisteredEntity]) -> None:
        """Initialize sorter with entities to sort.

        Args:
            entities: List of entities to sort by dependency order.
        """
        self._entities = entities
        self._entity_map: Dict[str, RegisteredEntity] = {}
        self._graph: Dict[str, List[str]] = {}
        self._in_degree: Dict[str, int] = {}

    def sort(self) -> List[RegisteredEntity]:
        """Sort entities by dependency order.

        Returns:
            Entities sorted so dependencies come before dependents.

        Raises:
            ValueError: If circular dependency detected.
        """
        self._build_entity_map()
        self._build_dependency_graph()
        sorted_names = self._execute_kahns_algorithm()
        self._check_for_cycles(sorted_names)
        return self._map_names_to_entities(sorted_names)

    def _build_entity_map(self) -> None:
        self._entity_map = {e.config.name: e for e in self._entities}

    def _build_dependency_graph(self) -> None:
        self._graph = {name: [] for name in self._entity_map}
        self._in_degree = {name: 0 for name in self._entity_map}

        for name, entity in self._entity_map.items():
            for dep in entity.get_dependencies():
                if dep in self._entity_map:
                    self._graph[dep].append(name)
                    self._in_degree[name] += 1

    def _execute_kahns_algorithm(self) -> List[str]:
        queue = [name for name, degree in self._in_degree.items() if degree == 0]
        sorted_names: List[str] = []

        while queue:
            queue.sort()
            current = queue.pop(0)
            sorted_names.append(current)

            for neighbor in self._graph[current]:
                self._in_degree[neighbor] -= 1
                if self._in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return sorted_names

    def _check_for_cycles(self, sorted_names: List[str]) -> None:
        if len(sorted_names) != len(self._entity_map):
            remaining = set(self._entity_map.keys()) - set(sorted_names)
            raise ValueError(
                f"circular dependency detected among entities: {remaining}"
            )

    def _map_names_to_entities(self, sorted_names: List[str]) -> List[RegisteredEntity]:
        return [self._entity_map[name] for name in sorted_names]


class EntityDiscovery:
    """Discovers and loads entity configurations from filesystem.

    Scans a directory structure for entity_config.py files and automatically
    discovers EntityConfig classes to populate the entity registry.
    """

    def __init__(self, entities_dir: Optional[Path] = None) -> None:
        """Initialize entity discovery.

        Args:
            entities_dir: Directory to scan for entity configurations.
                If None, uses the directory containing this module.
        """
        self._entities: Dict[str, RegisteredEntity] = {}
        if entities_dir is None:
            self._entities_dir = Path(__file__).parent
        else:
            self._entities_dir = entities_dir

    def discover(self) -> None:
        """Discover and register all entity configurations.

        Scans the entities directory for entity_config.py files and
        registers all EntityConfig classes found.
        """
        for entity_config_file in self._yield_entity_config_files(self._entities_dir):
            self._try_register_entities_in_file(entity_config_file)

    def _try_register_entities_in_file(self, file: Path) -> None:
        try:
            self._register_entities_in_file(file)
        except Exception as e:
            logger.error(f"Failed to load entity from {file.parent.name}: {e}")

    def _yield_entity_config_files(self, path: Path) -> Iterator[Path]:
        for dir in path.iterdir():
            if not dir.is_dir():
                continue
            if dir.name.startswith("_"):
                continue
            config_file = dir / "entity_config.py"
            if not config_file.exists():
                continue
            yield config_file

    def _register_entities_in_file(self, file: Path) -> None:
        module = self._maybe_load_module(file)
        if module is None:
            return
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if name.endswith("EntityConfig"):
                self._register_entity(cls)

    def _maybe_load_module(self, config_file: Path) -> Optional[ModuleType]:
        module_name = self._get_module_name_from_config_file(config_file)
        spec = importlib.util.spec_from_file_location(module_name, config_file)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _get_module_name_from_config_file(self, config_file: Path) -> str:
        return f"github_data.entities.{config_file.parent.name}.entity_config"

    def _register_entity(self, cls: type[Any]) -> None:
        name, entity = self._build_registered_entity(cls)
        self._entities[name] = entity
        logger.info(f"Discovered entity: {name}")

    def _build_registered_entity(self, obj: type[Any]) -> Tuple[str, RegisteredEntity]:
        config = obj()
        entity = RegisteredEntity(config=config, enabled=config.default_value)
        return config.name, entity

    def get_entities(self) -> Dict[str, RegisteredEntity]:
        """Get all discovered entities.

        Returns:
            Dictionary mapping entity names to RegisteredEntity instances.
        """
        return self._entities


class EntityEnvironmentLoader:
    """Loads entity configuration from environment variables.

    Orchestrates loading environment variable values for all entities
    and validating their dependencies.
    """

    def __init__(
        self, entities: Dict[str, RegisteredEntity], explicitly_set: Set[str]
    ) -> None:
        """Initialize environment loader.

        Args:
            entities: Dictionary of entities to configure.
            explicitly_set: Set to track which entities were explicitly
                configured by user (vs. using defaults).
        """
        self._entities = entities
        self._explicitly_set = explicitly_set

    def load(self, is_strict: bool) -> None:
        """Load all entity values from environment and validate dependencies.

        Args:
            is_strict: If True, raise error on dependency violations.
                If False, auto-disable entities with unsatisfied dependencies.
        """
        self._load_all_values()
        self._validate_dependencies(is_strict)

    def _load_all_values(self) -> None:
        for entity_name, entity in self._entities.items():
            loader = EntityValueLoader(entity_name, entity, self._explicitly_set)
            loader.load_from_environment()

    def _validate_dependencies(self, is_strict: bool) -> None:
        validator = DependencyValidator(self._entities, self._explicitly_set, is_strict)
        validator.validate()


class EntityValueLoader:
    """Loads and parses environment variable value for a single entity.

    Handles reading environment variables, parsing boolean and number
    specifications, and tracking whether values were explicitly set.
    """

    def __init__(
        self, entity_name: str, entity: RegisteredEntity, explicitly_set: Set[str]
    ) -> None:
        """Initialize value loader for a single entity.

        Args:
            entity_name: Name of the entity.
            entity: RegisteredEntity instance to configure.
            explicitly_set: Set to update when value is explicitly set.
        """
        self._entity_name = entity_name
        self._entity = entity
        self._explicitly_set = explicitly_set

    def load_from_environment(self) -> None:
        """Load entity value from its environment variable.

        Reads the environment variable defined in entity config, parses
        the value according to the entity's value_type, and sets the
        entity's enabled state.
        """
        value = os.getenv(self._entity.config.env_var)
        if value is None:
            self._use_default_value()
        else:
            self._parse_and_set_value(value)

    def _use_default_value(self) -> None:
        self._entity.enabled = self._entity.config.default_value

    def _parse_and_set_value(self, value: str) -> None:
        self._explicitly_set.add(self._entity_name)
        self._entity.enabled = self._parse_value(value)

    def _parse_value(self, value: str) -> Any:
        if self._entity.config.value_type == bool:
            return self._parse_boolean_value(value)
        else:
            return self._parse_boolean_or_number_spec(value)

    def _parse_boolean_value(self, value: str) -> bool:
        try:
            return NumberSpecificationParser.parse_boolean_value(value)
        except ValueError as e:
            raise ValueError(
                f"Environment variable {self._entity.config.env_var}: {str(e)}"
            )

    def _parse_boolean_or_number_spec(self, value: str) -> Any:
        if NumberSpecificationParser.is_boolean_value(value):
            return self._parse_boolean_value(value)
        else:
            return self._parse_number_spec(value)

    def _parse_number_spec(self, value: str) -> Set[int]:
        try:
            return NumberSpecificationParser.parse(value)
        except ValueError as e:
            raise ValueError(
                f"Environment variable {self._entity.config.env_var}: {str(e)}"
            )


class DependencyValidator:
    """Validates entity dependencies across all entities.

    Ensures that enabled entities have their required dependencies enabled.
    Handles transitive dependencies by iterating until no changes occur.
    """

    def __init__(
        self,
        entities: Dict[str, RegisteredEntity],
        explicitly_set: Set[str],
        is_strict: bool,
    ) -> None:
        """Initialize dependency validator.

        Args:
            entities: Dictionary of all entities to validate.
            explicitly_set: Set of entities explicitly configured by user.
            is_strict: If True, raise error on dependency violations.
                If False, auto-disable entities with unsatisfied dependencies.
        """
        self._context = ValidationContext(entities, explicitly_set, is_strict)

    def validate(self) -> None:
        """Validate all entity dependencies.

        Iterates until no changes occur to handle transitive dependencies.
        In non-strict mode, automatically disables entities with unsatisfied
        dependencies. In strict mode, raises ValueError for explicitly-set
        entities with dependency violations.

        Raises:
            ValueError: In strict mode, if explicitly-set entity has
                unsatisfied dependency.
        """
        self._context.mark_change_made()
        while self._context.is_change_made():
            self._context.reset_change_flag()
            self._validate_once()

    def _validate_once(self) -> None:
        for entity_name, entity in self._context.entities.items():
            if not entity.is_enabled():
                continue
            validator = EntityDependencyValidator(entity_name, entity, self._context)
            validator.validate()


class EntityDependencyValidator:
    """Validates dependencies for a single entity.

    Checks that all required dependencies are enabled. In strict mode,
    raises error for explicitly-set entities. In non-strict mode,
    auto-disables entities with unsatisfied dependencies.
    """

    def __init__(
        self,
        entity_name: str,
        entity: RegisteredEntity,
        context: "ValidationContext",
    ) -> None:
        """Initialize validator for a single entity.

        Args:
            entity_name: Name of the entity to validate.
            entity: RegisteredEntity instance to validate.
            context: Shared validation context with entities and settings.
        """
        self._entity_name = entity_name
        self._entity = entity
        self._context = context

    def validate(self) -> None:
        """Validate this entity's dependencies.

        Raises:
            ValueError: In strict mode, if explicitly-set entity has
                unsatisfied dependency.
        """
        for dep_name in self._entity.get_dependencies():
            self._handle_dependency(dep_name)

    def _handle_dependency(self, dep_name: str) -> None:
        if not self._is_dependency_known(dep_name):
            return

        dep_entity = self._context.get_entity(dep_name)
        if dep_entity is None or dep_entity.is_enabled():
            return

        self._handle_disabled_dependency(dep_entity)

    def _is_dependency_known(self, dep_name: str) -> bool:
        if self._context.get_entity(dep_name) is not None:
            return True
        logger.warning(
            f"Entity {self._entity_name} depends on unknown entity: {dep_name}"
        )
        return False

    def _handle_disabled_dependency(self, dep_entity: RegisteredEntity) -> None:
        is_explicitly_set = self._context.is_explicitly_set(self._entity_name)
        if is_explicitly_set and self._context.is_strict:
            self._raise_dependency_error(dep_entity)
        else:
            self._auto_disable_entity(dep_entity)
            self._context.mark_change_made()

    def _raise_dependency_error(self, dep_entity: RegisteredEntity) -> None:
        raise ValueError(
            f"{self._entity.config.env_var}=true requires "
            f"{dep_entity.config.env_var}=true. "
            f"Cannot enable {self._entity.config.name} without "
            f"{dep_entity.config.name}."
        )

    def _auto_disable_entity(self, dep_entity: RegisteredEntity) -> None:
        logger.warning(
            f"Warning: {self._entity.config.env_var} requires "
            f"{dep_entity.config.env_var}. Disabling {self._entity.config.name}."
        )
        self._entity.enabled = False


class ValidationContext:
    """Shared context for dependency validation.

    Groups related parameters that are passed together during validation
    to reduce parameter count and improve cohesion.
    """

    def __init__(
        self,
        entities: Dict[str, RegisteredEntity],
        explicitly_set: Set[str],
        is_strict: bool,
    ) -> None:
        """Initialize validation context.

        Args:
            entities: Dictionary of all entities.
            explicitly_set: Set of explicitly configured entities.
            is_strict: If True, raise error on violations.
        """
        self.entities = entities
        self.explicitly_set = explicitly_set
        self.is_strict = is_strict
        self._is_change_made = False

    def is_explicitly_set(self, entity_name: str) -> bool:
        """Check if entity was explicitly configured by user."""
        return entity_name in self.explicitly_set

    def get_entity(self, name: str) -> Optional[RegisteredEntity]:
        """Get entity by name, or None if not found."""
        return self.entities.get(name)

    def mark_change_made(self) -> None:
        """Mark that a change was made during validation."""
        self._is_change_made = True

    def is_change_made(self) -> bool:
        """Check if a change was made during validation."""
        return self._is_change_made

    def reset_change_flag(self) -> None:
        """Reset the change flag for the next validation pass."""
        self._is_change_made = False
