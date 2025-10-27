"""Factory for creating save and restore strategies."""

import logging
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.registry import EntityRegistry
    from src.entities.base import BaseSaveStrategy, BaseRestoreStrategy, EntityConfig
    from src.entities.strategy_context import StrategyContext

logger = logging.getLogger(__name__)


class StrategyFactory:
    """Factory for creating entity strategies from EntityRegistry."""

    def __init__(self, registry: "EntityRegistry"):
        """Initialize strategy factory.

        Args:
            registry: EntityRegistry for entity management
        """
        self.registry = registry

    def _validate_requirements(
        self,
        config: "EntityConfig",
        context: "StrategyContext",
        operation: str,
    ) -> None:
        """Validate required services are available in context.

        Args:
            config: Entity configuration
            context: Strategy context to validate
            operation: "save" or "restore"

        Raises:
            RuntimeError: If required service not available
        """
        # Get requirements for this operation (default empty list for backward compatibility)
        required = getattr(config, f"required_services_{operation}", [])

        for service_name in required:
            # Check if service is available (not None)
            private_attr = f"_{service_name}"
            if getattr(context, private_attr, None) is None:
                raise RuntimeError(
                    f"Entity '{config.name}' requires '{service_name}' "
                    f"for {operation} operation, but it was not provided in context"
                )

    def create_save_strategies(
        self,
        git_service: Optional[Any] = None,
        **additional_context: Any,
    ) -> List["BaseSaveStrategy"]:
        """Create save strategies for all enabled entities.

        Args:
            git_service: Optional git service for entities that need it
            **additional_context: Additional context for strategy creation

        Returns:
            List of save strategy instances in dependency order

        Raises:
            RuntimeError: If any entity's service requirements not met
        """
        from src.entities.strategy_context import StrategyContext

        # Create typed context from parameters
        context = StrategyContext(
            _git_service=git_service,
            _github_service=additional_context.get("github_service"),
            _conflict_strategy=additional_context.get("conflict_strategy"),
            _include_original_metadata=additional_context.get(
                "include_original_metadata", True
            ),
        )

        strategies = []
        enabled_entities = self.registry.get_enabled_entities()

        for entity in enabled_entities:
            # Validate requirements BEFORE creating strategy
            self._validate_requirements(entity.config, context, "save")

            try:
                strategy = entity.config.create_save_strategy(context)
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
        github_service: Optional[Any] = None,
        conflict_strategy: Optional[Any] = None,
        include_original_metadata: bool = True,
        **additional_context: Any,
    ) -> List["BaseRestoreStrategy"]:
        """Create restore strategies for all enabled entities.

        Args:
            git_service: Optional git service for entities that need it
            github_service: Optional GitHub API service for entities that need it
            conflict_strategy: Optional conflict resolution strategy
            include_original_metadata: Whether to preserve original metadata
            **additional_context: Additional context for strategy creation

        Returns:
            List of restore strategy instances in dependency order

        Raises:
            RuntimeError: If any entity's service requirements not met
        """
        from src.entities.strategy_context import StrategyContext

        # Create typed context from parameters
        context = StrategyContext(
            _git_service=git_service,
            _github_service=github_service,
            _conflict_strategy=conflict_strategy,
            _include_original_metadata=include_original_metadata,
        )

        strategies = []
        enabled_entities = self.registry.get_enabled_entities()

        for entity in enabled_entities:
            # Validate requirements BEFORE creating strategy
            self._validate_requirements(entity.config, context, "restore")

            try:
                strategy = entity.config.create_restore_strategy(context)
                if strategy is not None:
                    strategies.append(strategy)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to create restore strategy for "
                    f"'{entity.config.name}': {e}. "
                    f"Cannot proceed with restore operation."
                ) from e

        return strategies
