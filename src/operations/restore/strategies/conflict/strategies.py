"""Concrete conflict resolution strategies."""

from typing import Any
from .base import BaseConflictStrategy


class SkipConflictStrategy(BaseConflictStrategy):
    """Strategy that skips existing entities to avoid conflicts."""

    def resolve_conflict(self, existing_entity: Any, new_entity: Any) -> Any:
        """Skip the new entity if existing entity is found."""
        return None  # Skip creation


class OverwriteConflictStrategy(BaseConflictStrategy):
    """Strategy that overwrites existing entities with new ones."""

    def resolve_conflict(self, existing_entity: Any, new_entity: Any) -> Any:
        """Overwrite existing entity with new entity."""
        return new_entity  # Create/overwrite


class RenameConflictStrategy(BaseConflictStrategy):
    """Strategy that renames new entities to avoid conflicts."""

    def resolve_conflict(self, existing_entity: Any, new_entity: Any) -> Any:
        """Rename new entity to avoid conflict."""
        # This would need entity-specific logic for renaming
        # For now, just return the new entity unchanged
        return new_entity


class MergeConflictStrategy(BaseConflictStrategy):
    """Strategy that merges existing and new entities."""

    def resolve_conflict(self, existing_entity: Any, new_entity: Any) -> Any:
        """Merge existing and new entity attributes."""
        # This would need entity-specific logic for merging
        # For now, just return the new entity unchanged
        return new_entity
