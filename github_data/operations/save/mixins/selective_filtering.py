"""Selective filtering mixin for save strategies."""

from abc import ABC, abstractmethod
from typing import List, Any, Union, Set, Dict


class SelectiveFilteringMixin(ABC):
    """Mixin providing generic selective filtering capabilities."""

    def __init__(self, include_spec: Union[bool, Set[int]], *args: Any, **kwargs: Any):
        """Initialize with filtering specification."""
        super().__init__(*args, **kwargs)
        self._include_spec = include_spec

    def apply_selective_filtering(
        self, entities: List[Any], context: Dict[str, Any]
    ) -> List[Any]:
        """Apply selective filtering based on include specification."""
        # Context parameter is available for future extensibility
        _ = context
        if isinstance(self._include_spec, bool):
            return self._handle_boolean_filtering(entities)
        else:
            return self._handle_selective_filtering(entities)

    def _handle_boolean_filtering(self, entities: List[Any]) -> List[Any]:
        """Handle boolean include/exclude all logic."""
        return entities if self._include_spec else []

    def _handle_selective_filtering(self, entities: List[Any]) -> List[Any]:
        """Handle selective filtering by entity numbers."""
        entity_name = self.get_entity_name()

        # Filter entities
        filtered_entities = []
        for entity in entities:
            # Type check: Set[int] in _handle_selective_filtering
            assert isinstance(self._include_spec, set)
            if self._should_include_entity(entity, self._include_spec):
                filtered_entities.append(entity)

        # Report results
        # Type check: Set[int] in _handle_selective_filtering
        assert isinstance(self._include_spec, set)
        self._report_filtering_results(
            filtered_entities, entities, self._include_spec, entity_name
        )

        return filtered_entities

    def _should_include_entity(self, entity: Any, include_spec: Set[int]) -> bool:
        """Determine if entity should be included based on specification."""
        return hasattr(entity, "number") and entity.number in include_spec

    def _report_filtering_results(
        self,
        filtered_entities: List[Any],
        all_entities: List[Any],
        include_spec: Set[int],
        entity_name: str,
    ) -> None:
        """Report filtering results with missing number warnings."""
        found_numbers = {entity.number for entity in filtered_entities}
        missing_numbers = include_spec - found_numbers

        if missing_numbers:
            entity_display = entity_name.replace("_", " ").title()
            print(
                f"Warning: {entity_display} not found in repository: "
                f"{sorted(missing_numbers)}"
            )

        print(
            f"Selected {len(filtered_entities)} {entity_name} from "
            f"{len(all_entities)} total"
        )

    @abstractmethod
    def get_entity_name(self) -> str:
        """Return the entity name for logging and reporting."""
        pass
