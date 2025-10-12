"""Generic dependency resolution using topological sort."""

from typing import List, Mapping, Protocol


class DependencyProvider(Protocol):
    """Protocol for objects that provide dependency information."""

    def get_entity_name(self) -> str:
        """Return the entity name."""
        ...

    def get_dependencies(self) -> List[str]:
        """Return list of entity names this entity depends on."""
        ...


class DependencyResolver:
    """Generic dependency resolution using topological sort."""

    def resolve_execution_order(
        self, providers: Mapping[str, DependencyProvider], requested_entities: List[str]
    ) -> List[str]:
        """Resolve strategy execution order based on dependencies.

        Args:
            providers: Dictionary mapping entity names to dependency providers
            requested_entities: List of entity names requested for processing

        Returns:
            List of entity names in dependency-resolved execution order

        Raises:
            ValueError: If circular dependencies are detected
        """
        resolved = []
        remaining = set(requested_entities)

        while remaining:
            # Find entities with no unresolved dependencies
            ready = []
            for entity in remaining:
                if entity in providers:
                    deps = providers[entity].get_dependencies()
                    if all(
                        dep in resolved or dep not in requested_entities for dep in deps
                    ):
                        ready.append(entity)

            if not ready:
                raise ValueError(f"Circular dependency detected in: {remaining}")

            # Add ready entities to resolution order
            for entity in ready:
                resolved.append(entity)
                remaining.remove(entity)

        return resolved
