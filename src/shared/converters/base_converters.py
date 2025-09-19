"""Base converter patterns for API response transformation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, TypeVar, Generic
from datetime import datetime

T = TypeVar("T")


class BaseConverter(ABC, Generic[T]):
    """Base class for entity-specific converters."""

    @abstractmethod
    def from_graphql(self, data: Dict[str, Any]) -> T:
        """Convert GraphQL response to entity model."""
        pass

    @abstractmethod
    def from_rest(self, data: Dict[str, Any]) -> T:
        """Convert REST API response to entity model."""
        pass

    @abstractmethod
    def to_api_format(self, entity: T) -> Dict[str, Any]:
        """Convert entity model to API request format."""
        pass

    def _parse_datetime(self, date_str: str | None) -> datetime | None:
        """Helper to parse GitHub datetime strings."""
        if not date_str:
            return None
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
