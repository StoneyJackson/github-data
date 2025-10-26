"""Strategy-based restore orchestrator."""

import json
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from .strategy import RestoreEntityStrategy
from src.entities.labels.restore_strategy import OverwriteConflictStrategy
from src.operations.strategy_factory import StrategyFactory

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService
    from src.git.protocols import GitRepositoryService
    from src.entities.registry import EntityRegistry


class StrategyBasedRestoreOrchestrator:
    """Orchestrator that executes restore operations using EntityRegistry."""

    def __init__(
        self,
        registry: "EntityRegistry",
        github_service: "RepositoryService",
        storage_service: "StorageService",
        include_original_metadata: bool = True,
        git_service: Optional["GitRepositoryService"] = None,
    ) -> None:
        """Initialize restore orchestrator.

        Args:
            registry: EntityRegistry for entity management
            github_service: GitHub API service
            storage_service: Storage service for reading data
            include_original_metadata: Whether to include original metadata
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
        # Note: include_original_metadata is stored but not passed to all strategies
        # Each strategy uses its own defaults or config
        self._include_original_metadata = include_original_metadata
        self._strategies = self._factory.create_restore_strategies(
            git_service=git_service
        )

    def execute_restore(
        self,
        repo_name: str,
        input_path: str,
    ) -> List[Dict[str, Any]]:
        """Execute restore operation using registered strategies.

        Args:
            repo_name: Repository name (owner/repo)
            input_path: Input directory path

        Returns:
            List of result dictionaries for each entity
        """
        results = []

        # Execute strategies in dependency order (already sorted by registry)
        for strategy in self._strategies:
            entity_name = strategy.get_entity_name()
            result = self._execute_strategy(strategy, repo_name, input_path)
            results.append(result)
            print(f"Restored {entity_name}: {result.get('entities_created', 0)} items")

        return results

    def _execute_strategy(
        self, strategy: RestoreEntityStrategy, repo_name: str, input_path: str
    ) -> Dict[str, Any]:
        """Execute a single entity restoration strategy."""
        entity_name = strategy.get_entity_name()

        try:
            # Read data
            entities = strategy.read(input_path, self._storage_service)
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
                        from src.github import converters

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
                entity_data = strategy.transform(entity, self._context)
                if entity_data is None:
                    continue  # Skip entity (e.g., missing dependency)

                created_data = strategy.write(
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
