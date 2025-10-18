"""Milestone save strategy implementation."""

from typing import Any, Dict, List
from src.operations.save.strategy import SaveEntityStrategy


class MilestonesSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository milestones."""

    def get_entity_name(self) -> str:
        """Return the entity name for file naming and logging."""
        return "milestones"

    def get_dependencies(self) -> List[str]:
        """Milestones have no dependencies."""
        return []

    def get_converter_name(self) -> str:
        """Return the converter function name."""
        return "convert_to_milestone"

    def get_service_method(self) -> str:
        """Return the service method name for data collection."""
        return "get_repository_milestones"

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process milestone data - no special processing needed."""
        return entities

    def should_skip(self, config: Any) -> bool:
        """Skip milestone operations if disabled in config."""
        return not getattr(config, "include_milestones", True)
