"""Entity coupling mixin for save strategies."""

from abc import ABC, abstractmethod
from typing import List, Any, Set


class EntityCouplingMixin(ABC):
    """Mixin providing parent-child entity coupling capabilities."""

    def filter_children_by_parents(
        self, children: List[Any], parents: List[Any], parent_context_key: str
    ) -> List[Any]:
        """Filter child entities based on saved parent entities."""
        if not parents:
            return self._handle_no_parents(children)

        parent_identifiers = self._extract_parent_identifiers(parents)
        if not parent_identifiers:
            entity_name = self.get_entity_name()
            print(f"No valid parent identifiers found, skipping all {entity_name}")
            return []

        # Filter children
        filtered_children = []
        for child in children:
            if self._child_matches_parent(child, parent_identifiers):
                filtered_children.append(child)

        # Report results
        self._report_coupling_results(filtered_children, children, parents)
        return filtered_children

    def _extract_parent_identifiers(self, parents: List[Any]) -> Set[str]:
        """Extract all possible identifiers from parent entities."""
        identifiers = set()

        for parent in parents:
            # Add entity number
            if hasattr(parent, "number"):
                identifiers.add(str(parent.number))

            # Add URL patterns
            if hasattr(parent, "html_url"):
                identifiers.add(parent.html_url)
                # Extract number and create API URL patterns
                try:
                    number = parent.html_url.split("/")[-1]
                    api_pattern = f"/{self.get_parent_api_path()}/{number}"
                    identifiers.add(api_pattern)
                except (IndexError, ValueError):
                    pass

            # Add additional URL patterns for PRs
            if hasattr(parent, "url"):
                identifiers.add(parent.url)

        return identifiers

    def _child_matches_parent(self, child: Any, parent_identifiers: Set[str]) -> bool:
        """Check if child entity matches any parent identifier."""
        child_url = self._get_child_parent_url(child)
        if not child_url:
            return False

        # Direct match
        if child_url in parent_identifiers:
            return True

        # Partial URL matches
        for identifier in parent_identifiers:
            if identifier in child_url:
                return True

        # Extract and match number from URL
        try:
            number = child_url.split("/")[-1]
            if number in parent_identifiers:
                return True
        except (IndexError, ValueError):
            pass

        return False

    def _handle_no_parents(self, children: List[Any]) -> List[Any]:
        """Handle case when no parent entities are available."""
        if not hasattr(self, "_selective_mode") or not self._selective_mode:
            return children  # Backward compatibility
        else:
            parent_name = self.get_parent_entity_name()
            entity_name = self.get_entity_name()
            print(f"No {parent_name} were saved, skipping all {entity_name}")
            return []

    def _report_coupling_results(
        self, filtered_children: List[Any], all_children: List[Any], parents: List[Any]
    ) -> None:
        """Report coupling results."""
        parent_name = self.get_parent_entity_name()
        child_name = self.get_entity_name()

        total_msg = (
            f"Selected {len(filtered_children)} {child_name} from "
            f"{len(all_children)} total "
            f"(coupling to {len(parents)} saved {parent_name})"
        )
        print(total_msg)

    @abstractmethod
    def get_entity_name(self) -> str:
        """Return the entity name for logging and reporting."""
        pass

    @abstractmethod
    def get_parent_entity_name(self) -> str:
        """Return the parent entity name for logging."""
        pass

    @abstractmethod
    def get_parent_api_path(self) -> str:
        """Return the API path segment for parent entities (e.g., 'issues', 'pulls')."""
        pass

    @abstractmethod
    def _get_child_parent_url(self, child: Any) -> str:
        """Extract the parent URL from child entity."""
        pass
