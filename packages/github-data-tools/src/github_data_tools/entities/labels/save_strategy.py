"""Labels save strategy implementation."""

from typing import List, Dict, Any

from github_data_tools.operations.save.strategy import SaveEntityStrategy


class LabelsSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository labels."""

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "labels"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return []  # Labels have no dependencies

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        return "convert_to_label"

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        return "get_repository_labels"

    def transform(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Transform labels data."""
        # Labels don't require any processing
        return entities
