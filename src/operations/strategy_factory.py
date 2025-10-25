"""Factory for creating save and restore strategies."""

import importlib
import logging
from typing import Any, Optional, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from src.config.settings import ApplicationConfig
    from src.entities.registry import EntityRegistry, RegisteredEntity
    from src.operations.save.strategy import SaveEntityStrategy
    from src.operations.restore.strategy import RestoreEntityStrategy

logger = logging.getLogger(__name__)


class StrategyFactory:
    """Factory for creating entity strategies.

    Supports loading strategies from both EntityRegistry (new system)
    and ApplicationConfig (legacy system for unmigrated entities).
    """

    def __init__(
        self,
        registry: Optional["EntityRegistry"] = None,
        config: Optional["ApplicationConfig"] = None,
    ):
        """Initialize strategy factory.

        Args:
            registry: EntityRegistry for migrated entities
            config: ApplicationConfig for unmigrated entities (legacy)
        """
        self.registry = registry
        self.config = config

    def load_save_strategy(self, entity_name: str) -> Optional["SaveEntityStrategy"]:
        """Load save strategy for entity by name.

        Args:
            entity_name: Name of entity (e.g., "labels", "issues")

        Returns:
            Save strategy instance or None if not found
        """
        # Try loading from registry first (migrated entities)
        if self.registry:
            try:
                entity = self.registry.get_entity(entity_name)
                return self._load_save_strategy_from_registry(entity)
            except ValueError:
                # Entity not in registry, try ApplicationConfig
                pass

        # Fall back to ApplicationConfig (unmigrated entities)
        if self.config:
            return self._load_save_strategy_from_config(entity_name)

        return None

    def _load_save_strategy_from_registry(
        self, entity: "RegisteredEntity"
    ) -> Optional["SaveEntityStrategy"]:
        """Load save strategy from registry entity using convention.

        Args:
            entity: RegisteredEntity instance

        Returns:
            Save strategy instance or None
        """
        # Check for override in entity config
        entity_name = entity.config.name
        dir_name = self._to_directory_name(entity_name)
        module_name = f"src.entities.{dir_name}.save_strategy"

        # Use explicit class name if provided, otherwise use naming convention
        if entity.config.save_strategy_class:
            if isinstance(entity.config.save_strategy_class, str):
                class_name = entity.config.save_strategy_class  # type: ignore[unreachable]
            else:
                # It's already a class, instantiate it
                return cast("SaveEntityStrategy", entity.config.save_strategy_class())
        else:
            class_name = self._to_class_name(entity_name) + "SaveStrategy"

        try:
            module = importlib.import_module(module_name)
            strategy_class = getattr(module, class_name)
            return cast("SaveEntityStrategy", strategy_class())
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not load save strategy for {entity_name}: {e}")
            return None

    def _load_save_strategy_from_config(
        self, entity_name: str
    ) -> Optional["SaveEntityStrategy"]:
        """Load save strategy from ApplicationConfig (legacy).

        Args:
            entity_name: Entity name

        Returns:
            Save strategy instance or None
        """
        # TODO: Implement ApplicationConfig loading for unmigrated entities
        logger.warning(
            f"ApplicationConfig loading not yet implemented for {entity_name}"
        )
        return None

    def load_restore_strategy(
        self, entity_name: str, **kwargs: Any
    ) -> Optional["RestoreEntityStrategy"]:
        """Load restore strategy for entity by name.

        Args:
            entity_name: Name of entity (e.g., "labels", "issues")
            **kwargs: Additional arguments for strategy instantiation

        Returns:
            Restore strategy instance or None if not found
        """
        # Try loading from registry first (migrated entities)
        if self.registry:
            try:
                entity = self.registry.get_entity(entity_name)
                return self._load_restore_strategy_from_registry(entity, **kwargs)
            except ValueError:
                # Entity not in registry, try ApplicationConfig
                pass

        # Fall back to ApplicationConfig (unmigrated entities)
        if self.config:
            return self._load_restore_strategy_from_config(entity_name, **kwargs)

        return None

    def _load_restore_strategy_from_registry(
        self, entity: "RegisteredEntity", **kwargs: Any
    ) -> Optional["RestoreEntityStrategy"]:
        """Load restore strategy from registry entity using convention.

        Args:
            entity: RegisteredEntity instance
            **kwargs: Additional arguments for strategy instantiation

        Returns:
            Restore strategy instance or None
        """
        entity_name = entity.config.name
        dir_name = self._to_directory_name(entity_name)
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
            class_name = self._to_class_name(entity_name) + "RestoreStrategy"

        try:
            module = importlib.import_module(module_name)
            strategy_class = getattr(module, class_name)
            return cast("RestoreEntityStrategy", strategy_class(**kwargs))
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not load restore strategy for {entity_name}: {e}")
            return None

    def _load_restore_strategy_from_config(
        self, entity_name: str, **kwargs: Any
    ) -> Optional["RestoreEntityStrategy"]:
        """Load restore strategy from ApplicationConfig (legacy).

        Args:
            entity_name: Entity name
            **kwargs: Additional arguments for strategy instantiation

        Returns:
            Restore strategy instance or None
        """
        # TODO: Implement ApplicationConfig loading for unmigrated entities
        logger.warning(
            f"ApplicationConfig loading not yet implemented for {entity_name}"
        )
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
        """Convert entity name to class name.

        Args:
            entity_name: Snake case name (e.g., "pr_review_comments")

        Returns:
            PascalCase name (e.g., "PrReviewComments")
        """
        # Handle special case: git_repository -> GitRepository
        parts = entity_name.split("_")
        return "".join(word.capitalize() for word in parts)
