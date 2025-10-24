"""Base protocols and types for entity system."""

from typing import Protocol, Optional, List, Union, Set, Type, Any


class EntityConfig(Protocol):
    """Protocol for entity configuration metadata.

    All entity configs must define these attributes to be discovered.
    """

    name: str  # Entity identifier (e.g., "comment_attachments")
    env_var: str                        # Environment variable name
    default_value: Union[bool, Set[int]]  # Default enabled state
    value_type: Type                    # bool or Union[bool, Set[int]]
    dependencies: List[str] = []        # List of entity names this depends on
    save_strategy_class: Optional[Type] = None  # Override auto-discovery
    restore_strategy_class: Optional[Type] = None  # Override auto-discovery
    storage_filename: Optional[str] = None        # Override convention
    description: str = ""               # Documentation


class BaseSaveStrategy(Protocol):
    """Protocol for save strategies."""

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the save operation."""
        ...


class BaseRestoreStrategy(Protocol):
    """Protocol for restore strategies."""

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the restore operation."""
        ...
