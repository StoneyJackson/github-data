"""Factory for creating save and restore strategies."""

import importlib
import logging
from typing import Any, List, Optional, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from src.entities.registry import EntityRegistry
    from src.operations.save.strategy import SaveEntityStrategy
    from src.operations.restore.strategy import RestoreEntityStrategy

logger = logging.getLogger(__name__)


class StrategyFactory:
    """Factory for creating entity strategies from EntityRegistry."""

    def __init__(self, registry: "EntityRegistry"):
        """Initialize strategy factory.

        Args:
            registry: EntityRegistry for entity management
        """
        self.registry = registry

    def create_save_strategies(
        self,
        git_service: Optional[Any] = None,
        **additional_context: Any
    ) -> List["SaveEntityStrategy"]:
        """Create save strategies for all enabled entities.

        Args:
            git_service: Optional git service for entities that need it
            **additional_context: Additional context for strategy creation

        Returns:
            List of save strategy instances in dependency order

        Raises:
            RuntimeError: If any strategy factory method fails
        """
        context = {
            'git_service': git_service,
            **additional_context
        }

        strategies = []
        enabled_entities = self.registry.get_enabled_entities()

        for entity in enabled_entities:
            try:
                strategy = entity.config.create_save_strategy(**context)
                if strategy is not None:
                    strategies.append(strategy)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to create save strategy for '{entity.config.name}': {e}. "
                    f"Cannot proceed with save operation."
                ) from e

        return strategies

    def create_restore_strategies(
        self,
        git_service: Optional[Any] = None,
        conflict_strategy: Optional[Any] = None,
        include_original_metadata: bool = True,
        **additional_context: Any
    ) -> List["RestoreEntityStrategy"]:
        """Create restore strategies for all enabled entities.

        Args:
            git_service: Optional git service for entities that need it
            conflict_strategy: Optional conflict resolution strategy
            include_original_metadata: Whether to preserve original metadata
            **additional_context: Additional context for strategy creation

        Returns:
            List of restore strategy instances in dependency order

        Raises:
            RuntimeError: If any strategy factory method fails
        """
        context = {
            'git_service': git_service,
            'conflict_strategy': conflict_strategy,
            'include_original_metadata': include_original_metadata,
            **additional_context
        }

        strategies = []
        enabled_entities = self.registry.get_enabled_entities()

        for entity in enabled_entities:
            try:
                strategy = entity.config.create_restore_strategy(**context)
                if strategy is not None:
                    strategies.append(strategy)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to create restore strategy for '{entity.config.name}': {e}. "
                    f"Cannot proceed with restore operation."
                ) from e

        return strategies

    def load_save_strategy(self, entity_name: str, git_service: Optional[Any] = None) -> Optional["SaveEntityStrategy"]:
        """Load save strategy for entity by name.

        Args:
            entity_name: Name of entity
            git_service: Optional git service for git_repository

        Returns:
            Save strategy instance or None
        """
        try:
            entity = self.registry.get_entity(entity_name)
        except ValueError:
            logger.warning(f"Entity not found: {entity_name}")
            return None

        # Check for override
        if entity.config.save_strategy_class:
            if isinstance(entity.config.save_strategy_class, str):
                # It's a string class name, we'll use it below
                class_name = entity.config.save_strategy_class
            else:
                # It's already a class, instantiate it
                if entity_name == "git_repository" and git_service:
                    return entity.config.save_strategy_class(git_service)
                return entity.config.save_strategy_class()
        else:
            # Use naming convention
            class_name = self._to_class_name(entity.config.name) + "SaveStrategy"

        # Load the strategy class from the module
        dir_name = self._to_directory_name(entity.config.name)
        module_name = f"src.entities.{dir_name}.save_strategy"

        try:
            module = importlib.import_module(module_name)
            strategy_class = getattr(module, class_name)

            # Special handling for git_repository
            if entity_name == "git_repository" and git_service:
                return strategy_class(git_service)

            return strategy_class()
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not load save strategy for {entity_name}: {e}")
            return None

    def load_restore_strategy(
        self, entity_name: str, **kwargs: Any
    ) -> Optional["RestoreEntityStrategy"]:
        """Load restore strategy for entity by name.

        Args:
            entity_name: Name of entity
            **kwargs: Additional arguments for strategy instantiation

        Returns:
            Restore strategy instance or None
        """
        try:
            entity = self.registry.get_entity(entity_name)
        except ValueError:
            logger.warning(f"Entity not found: {entity_name}")
            return None

        dir_name = self._to_directory_name(entity.config.name)
        module_name = f"src.entities.{dir_name}.restore_strategy"

        # Use explicit class name if provided, otherwise use naming convention
        if entity.config.restore_strategy_class:
            if isinstance(entity.config.restore_strategy_class, str):
                class_name = entity.config.restore_strategy_class  # type: ignore[unreachable]
            else:
                # It's already a class, instantiate it
                return cast(
                    "RestoreEntityStrategy", entity.config.restore_strategy_class(**kwargs)
                )
        else:
            class_name = self._to_class_name(entity.config.name) + "RestoreStrategy"

        try:
            module = importlib.import_module(module_name)
            strategy_class = getattr(module, class_name)
            return cast("RestoreEntityStrategy", strategy_class(**kwargs))
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not load restore strategy for {entity_name}: {e}")
            return None
        except TypeError as e:
            # Strategy requires different constructor parameters
            # This happens when entity config doesn't match strategy signature
            logger.warning(f"Could not instantiate restore strategy for {entity_name}: {e}")
            return None

    def _to_directory_name(self, entity_name: str) -> str:
        """Convert entity name to directory name.

        Args:
            entity_name: Entity name (e.g., "git_repository", "labels")

        Returns:
            Directory name (e.g., "git_repositories", "labels")
        """
        # Special case: git_repository -> git_repositories (plural)
        if entity_name == "git_repository":
            return "git_repositories"
        # Default: use entity name as-is
        return entity_name

    def _to_class_name(self, entity_name: str) -> str:
        """Convert snake_case entity name to PascalCase.

        Args:
            entity_name: Snake case name (e.g., "pr_review_comments")

        Returns:
            PascalCase name (e.g., "PrReviewComments")
        """
        parts = entity_name.split("_")
        return "".join(word.capitalize() for word in parts)
