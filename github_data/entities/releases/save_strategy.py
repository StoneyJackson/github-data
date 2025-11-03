"""Release save strategy implementation."""

from typing import Any, Dict, List
from github_data.operations.save.strategy import SaveEntityStrategy


class ReleasesSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository releases."""

    def get_entity_name(self) -> str:
        """Return the entity name for file naming and logging."""
        return "releases"

    def get_dependencies(self) -> List[str]:
        """Releases have no dependencies."""
        return []

    def get_converter_name(self) -> str:
        """Return the converter function name."""
        return "convert_to_release"

    def get_service_method(self) -> str:
        """Return the service method name for data collection."""
        return "get_repository_releases"

    def transform(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process release data - no special processing needed yet."""
        return entities

    def should_skip(self, config: Any) -> bool:
        """Skip release operations if disabled in config."""
        return not getattr(config, "include_releases", True)
