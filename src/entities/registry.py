"""Entity registry for auto-discovery and configuration."""

from typing import Dict
from src.entities.base import RegisteredEntity
import logging

logger = logging.getLogger(__name__)


class EntityRegistry:
    """Central registry for all entities.

    Replaces ApplicationConfig with dynamic entity discovery and registration.
    Auto-discovers entities from src/entities/ directory structure.
    """

    def __init__(self) -> None:
        """Initialize registry and discover entities."""
        self._entities: Dict[str, RegisteredEntity] = {}
        self._discover_entities()

    @classmethod
    def from_environment(cls, strict: bool = False) -> "EntityRegistry":
        """Create registry from environment variables.

        Args:
            strict: If True, fail on dependency violations. If False,
                warn and auto-disable.

        Returns:
            EntityRegistry instance configured from environment
        """
        registry = cls()
        registry._load_from_environment(strict)
        return registry

    def _discover_entities(self) -> None:
        """Auto-discover entities by scanning entities/ directory.

        Looks for *EntityConfig classes in entity_config.py files.
        """
        # TODO: Implement discovery in next task
        pass

    def _load_from_environment(self, strict: bool) -> None:
        """Load entity enabled values from environment variables.

        Args:
            strict: If True, fail on violations. If False, warn and correct.
        """
        # TODO: Implement environment loading in future task
        pass
