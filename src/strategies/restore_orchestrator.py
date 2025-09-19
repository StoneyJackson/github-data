"""Strategy-based restore orchestrator."""

import json
from typing import List, Dict, Any, TYPE_CHECKING
from .restore_strategy import RestoreEntityStrategy
from ..entities.labels.restore_strategy import OverwriteConflictStrategy

if TYPE_CHECKING:
    from ..storage.protocols import StorageService
    from ..github.protocols import RepositoryService


class StrategyBasedRestoreOrchestrator:
    """Orchestrator that executes restore operations using registered strategies."""

    def __init__(
        self, github_service: "RepositoryService", storage_service: "StorageService"
    ) -> None:
        self._github_service = github_service
        self._storage_service = storage_service
        self._strategies: Dict[str, RestoreEntityStrategy] = {}
        self._context: Dict[str, Any] = {}

    def register_strategy(self, strategy: RestoreEntityStrategy) -> None:
        """Register an entity restoration strategy."""
        self._strategies[strategy.get_entity_name()] = strategy

    def execute_restore(
        self, repo_name: str, input_path: str, requested_entities: List[str]
    ) -> List[Dict[str, Any]]:
        """Execute restore operation using registered strategies."""
        results = []

        # Resolve dependency order
        execution_order = self._resolve_execution_order(requested_entities)

        # Execute strategies in dependency order
        for entity_name in execution_order:
            if entity_name in self._strategies:
                result = self._execute_strategy(entity_name, repo_name, input_path)
                results.append(result)

        return results

    def _resolve_execution_order(self, requested_entities: List[str]) -> List[str]:
        """Resolve execution order based on dependencies."""
        resolved = []
        remaining = set(requested_entities)

        while remaining:
            # Find entities with no unresolved dependencies
            ready = []
            for entity in remaining:
                if entity in self._strategies:
                    deps = self._strategies[entity].get_dependencies()
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

    def _execute_strategy(
        self, entity_name: str, repo_name: str, input_path: str
    ) -> Dict[str, Any]:
        """Execute a single entity restoration strategy."""
        strategy = self._strategies[entity_name]

        try:
            # Load data
            entities = strategy.load_data(input_path, self._storage_service)
            print(f"Loaded {len(entities)} {entity_name} to restore")

            # Handle conflicts if applicable (specifically for labels)
            if hasattr(strategy, "resolve_conflicts"):
                if entity_name == "labels":
                    # Special handling for labels with different conflict strategies
                    entities_to_create = strategy.resolve_conflicts(
                        self._github_service, repo_name, entities
                    )

                    # Check if using overwrite strategy which handles creation directly
                    if hasattr(strategy, "_conflict_strategy") and isinstance(
                        strategy._conflict_strategy, OverwriteConflictStrategy
                    ):
                        # Get existing labels for overwrite strategy
                        from ..github import converters

                        raw_existing = self._github_service.get_repository_labels(
                            repo_name
                        )
                        existing_labels = [
                            converters.convert_to_label(label_dict)
                            for label_dict in raw_existing
                        ]

                        strategy._conflict_strategy.handle_overwrite(
                            self._github_service, repo_name, existing_labels, entities
                        )
                        return {
                            "entity_name": entity_name,
                            "success": True,
                            "entities_processed": len(entities),
                            "entities_created": len(entities),
                        }

                    entities = entities_to_create
                else:
                    entities = strategy.resolve_conflicts(
                        self._github_service, repo_name, entities
                    )

            # Create entities
            created_count = 0
            for entity in entities:
                entity_data = strategy.transform_for_creation(entity, self._context)
                if entity_data is None:
                    continue  # Skip entity (e.g., missing dependency)

                created_data = strategy.create_entity(
                    self._github_service, repo_name, entity_data
                )
                strategy.post_create_actions(
                    self._github_service, repo_name, entity, created_data, self._context
                )
                created_count += 1

            return {
                "entity_name": entity_name,
                "success": True,
                "entities_processed": len(entities),
                "entities_created": created_count,
            }

        except (FileNotFoundError, json.JSONDecodeError):
            # Re-raise specific exceptions for backwards compatibility
            raise
        except Exception as e:
            return {
                "entity_name": entity_name,
                "success": False,
                "error": str(e),
                "entities_processed": 0,
                "entities_created": 0,
            }
