"""Strategy-based save orchestrator."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from .strategy import SaveEntityStrategy
from src.config.settings import ApplicationConfig
from src.operations.strategy_factory import StrategyFactory

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class StrategyBasedSaveOrchestrator:
    """Orchestrator that executes save operations using registered strategies."""

    def __init__(
        self,
        config: ApplicationConfig,
        github_service: "RepositoryService",
        storage_service: "StorageService",
    ) -> None:
        self._config = config
        self._github_service = github_service
        self._storage_service = storage_service
        self._strategies: Dict[str, SaveEntityStrategy] = {}
        self._context: Dict[str, Any] = {}

        # Auto-register strategies based on configuration
        for strategy in StrategyFactory.create_save_strategies(config):
            self.register_strategy(strategy)

    def register_strategy(self, strategy: SaveEntityStrategy) -> None:
        """Register an entity save strategy."""
        self._strategies[strategy.get_entity_name()] = strategy

    def execute_save(
        self,
        repo_name: str,
        output_path: str,
        requested_entities: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute save operation using registered strategies."""
        if requested_entities is None:
            requested_entities = StrategyFactory.get_enabled_entities(self._config)

        results = []

        # Resolve dependency order
        execution_order = self._resolve_execution_order(requested_entities)

        # Execute strategies in dependency order
        for entity_name in execution_order:
            if entity_name in self._strategies:
                result = self._execute_strategy(entity_name, repo_name, output_path)
                results.append(result)

        return results

    def _resolve_execution_order(self, requested_entities: List[str]) -> List[str]:
        """Resolve execution order based on dependencies."""
        resolved = []
        remaining = set(requested_entities)

        while remaining:
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

            for entity in ready:
                resolved.append(entity)
                remaining.remove(entity)

        return resolved

    def _execute_strategy(
        self, entity_name: str, repo_name: str, output_path: str
    ) -> Dict[str, Any]:
        """Execute a single entity save strategy."""
        strategy = self._strategies[entity_name]

        try:
            # Collect data
            entities = strategy.collect_data(self._github_service, repo_name)
            print(f"Collected {len(entities)} {entity_name}")

            # Store original context to detect changes
            original_context = self._context.copy()

            # Process data
            processed_entities = strategy.process_data(entities, self._context)

            # Save data
            result = strategy.save_data(
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
                        self._storage_service.save_data(value, entity_file)

            return {
                "entity_name": entity_name,
                "success": True,
                "entities_processed": len(entities),
                "entities_saved": len(processed_entities),
                **result,
            }

        except Exception as e:
            return {
                "entity_name": entity_name,
                "success": False,
                "error": str(e),
                "entities_processed": 0,
                "entities_saved": 0,
            }
