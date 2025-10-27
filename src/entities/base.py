"""Base protocols and types for entity system."""

from typing import Protocol, Optional, List, Union, Set, Type, Any, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from src.entities.strategy_context import StrategyContext


class EntityConfig(Protocol):
    """Protocol for entity configuration metadata.

    All entity configs must define these attributes to be discovered.
    """

    name: str  # Entity identifier (e.g., "comment_attachments")
    env_var: str  # Environment variable name
    default_value: Union[bool, Set[int]]  # Default enabled state
    value_type: Type  # bool or Union[bool, Set[int]]
    dependencies: List[str] = []  # List of entity names this depends on
    description: str = ""  # Documentation

    # Service requirements for operations (NEW)
    required_services_save: List[str] = []  # Services needed for save
    required_services_restore: List[str] = []  # Services needed for restore

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["BaseSaveStrategy"]:
        """Factory method for creating save strategy instances.

        Args:
            context: Typed strategy context with validated services

        Returns:
            Configured save strategy instance, or None if not applicable
        """
        ...

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["BaseRestoreStrategy"]:
        """Factory method for creating restore strategy instances.

        Args:
            context: Typed strategy context with validated services

        Returns:
            Configured restore strategy instance, or None if not applicable
        """
        ...


class BaseSaveStrategy(Protocol):
    """Protocol for save strategies."""

    def get_entity_name(self) -> str:
        """Get the entity name this strategy handles."""
        ...

    def read(self, *args: Any, **kwargs: Any) -> Any:
        """Read entities from source."""
        ...

    def transform(self, *args: Any, **kwargs: Any) -> Any:
        """Transform entities for storage."""
        ...

    def write(self, *args: Any, **kwargs: Any) -> Any:
        """Write entities to storage."""
        ...

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the save operation."""
        ...


class BaseRestoreStrategy(Protocol):
    """Protocol for restore strategies."""

    def get_entity_name(self) -> str:
        """Get the entity name this strategy handles."""
        ...

    def read(self, *args: Any, **kwargs: Any) -> Any:
        """Read entities from storage."""
        ...

    def transform(self, *args: Any, **kwargs: Any) -> Any:
        """Transform entities for restoration."""
        ...

    def write(self, *args: Any, **kwargs: Any) -> Any:
        """Write entities to GitHub."""
        ...

    def post_create_actions(self, *args: Any, **kwargs: Any) -> Any:
        """Perform post-creation actions."""
        ...

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the restore operation."""
        ...


@dataclass
class RegisteredEntity:
    """Represents a registered entity with runtime state.

    Combines entity configuration with runtime enabled state
    and lazily-loaded strategies.
    """

    config: EntityConfig
    enabled: Union[bool, Set[int]]
    save_strategy: Optional[BaseSaveStrategy] = None
    restore_strategy: Optional[BaseRestoreStrategy] = None

    def is_enabled(self) -> bool:
        """Check if entity is enabled.

        Returns:
            True if enabled (bool=True or non-empty set), False otherwise
        """
        if isinstance(self.enabled, bool):
            return self.enabled
        else:  # Set[int]
            return len(self.enabled) > 0

    def get_dependencies(self) -> List[str]:
        """Get list of dependency entity names.

        Returns:
            List of entity names this entity depends on
        """
        return self.config.dependencies

    def get_save_strategy(self) -> Optional[BaseSaveStrategy]:
        """Get save strategy (lazy load if needed).

        Returns:
            Save strategy instance or None
        """
        # TODO: Implement lazy loading in future task
        return self.save_strategy

    def get_restore_strategy(self) -> Optional[BaseRestoreStrategy]:
        """Get restore strategy (lazy load if needed).

        Returns:
            Restore strategy instance or None
        """
        # TODO: Implement lazy loading in future task
        return self.restore_strategy
