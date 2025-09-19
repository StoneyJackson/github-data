"""Base query patterns for GitHub API operations."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseQueries(ABC):
    """Base class for entity-specific queries."""

    @abstractmethod
    def get_graphql_query(self) -> str:
        """Get GraphQL query for bulk entity retrieval."""
        pass

    @abstractmethod
    def get_rest_endpoints(self) -> Dict[str, str]:
        """Get REST API endpoints for entity operations."""
        pass

    def get_pagination_params(self) -> Dict[str, Any]:
        """Get standard pagination parameters."""
        return {"per_page": 100, "page": 1}
