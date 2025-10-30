"""Strategy-based save orchestrator."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from github_data.operations.strategy_factory import StrategyFactory

if TYPE_CHECKING:
    from github_data.storage.protocols import StorageService
    from github_data.github.protocols import RepositoryService
    from github_data.git.protocols import GitRepositoryService
    from github_data.entities.registry import EntityRegistry
    from github_data.entities.base import BaseSaveStrategy


class StrategyBasedSaveOrchestrator:
    """Orchestrator that executes save operations using EntityRegistry."""

    def __init__(
        self,
        registry: "EntityRegistry",
        github_service: "RepositoryService",
        storage_service: "StorageService",
        git_service: Optional["GitRepositoryService"] = None,
    ) -> None:
        """Initialize save orchestrator.

        Args:
            registry: EntityRegistry for entity management
            github_service: GitHub API service
            storage_service: Storage service for writing data
            git_service: Optional git service for repository cloning
        """
        self._registry = registry
        self._github_service = github_service
        self._storage_service = storage_service
        self._git_service = git_service
        self._context: Dict[str, Any] = {}

        # Create strategy factory
        self._factory = StrategyFactory(registry=registry)

        # Load strategies for enabled entities
        self._strategies = self._factory.create_save_strategies(git_service=git_service)

    def execute_save(
        self,
        repo_name: str,
        output_path: str,
    ) -> List[Dict[str, Any]]:
        """Execute save operation using registered strategies.

        Args:
            repo_name: Repository name (owner/repo)
            output_path: Output directory path

        Returns:
            List of result dictionaries for each entity
        """
        results = []

        # Execute strategies in dependency order (already sorted by registry)
        for strategy in self._strategies:
            entity_name = strategy.get_entity_name()
            result = self._execute_strategy(strategy, repo_name, output_path)
            results.append(result)
            print(f"Saved {entity_name}: {result['count']} items")

        return results

    def _is_selective_mode(self, entity_name: str) -> bool:
        """Check if entity is in selective mode (Set[int] instead of bool).

        Args:
            entity_name: Entity name to check

        Returns:
            True if entity has Set[int] value (selective mode)
        """
        try:
            entity = self._registry.get_entity(entity_name)
            return isinstance(entity.enabled, set)
        except ValueError:
            return False

    def _execute_strategy(
        self, strategy: "BaseSaveStrategy", repo_name: str, output_path: str
    ) -> Dict[str, Any]:
        """Execute a single entity save strategy."""
        entity_name = strategy.get_entity_name()

        try:
            # Read data
            entities = strategy.read(self._github_service, repo_name)
            print(f"Collected {len(entities)} {entity_name}")

            # Store original context to detect changes
            original_context = self._context.copy()

            # Transform data
            processed_entities = strategy.transform(entities, self._context)

            # In selective mode, skip saving if no entities remain after processing
            if self._is_selective_mode(entity_name) and not processed_entities:
                return {
                    "entity_name": entity_name,
                    "success": True,
                    "entities_processed": len(entities),
                    "entities_saved": 0,
                    "count": 0,
                    "data_type": entity_name,
                    "items_processed": 0,
                    "execution_time_seconds": 0,
                }

            # Write data
            result = strategy.write(
                processed_entities, output_path, self._storage_service
            )

            # Update context with saved entities for dependent strategies
            self._context[entity_name] = processed_entities

            # If context was changed during processing
            # (e.g., sub-issues updating issues),
            # re-save the affected entities
            for key, value in self._context.items():
                if key != entity_name and key in original_context:
                    if value != original_context[key]:
                        # Re-save the updated entity
                        from pathlib import Path

                        output_dir = Path(output_path)
                        entity_file = output_dir / f"{key}.json"
                        self._storage_service.write(value, entity_file)

            return {
                "entity_name": entity_name,
                "success": True,
                "entities_processed": len(entities),
                "entities_saved": len(processed_entities),
                "count": len(processed_entities),
                **result,
            }

        except Exception as e:
            return {
                "entity_name": entity_name,
                "success": False,
                "error": str(e),
                "entities_processed": 0,
                "entities_saved": 0,
                "count": 0,
            }
