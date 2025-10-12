"""Base conflict resolution strategy implementation."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable


class BaseConflictStrategy(ABC):
    """Base class for conflict resolution strategies."""

    def execute_with_error_handling(
        self, operation_name: str, operation_fn: Callable[[], Any]
    ) -> Dict[str, Any]:
        """Execute operation with standardized error handling."""
        try:
            result = operation_fn()
            return self._success_result(operation_name, result)
        except Exception as e:
            return self._error_result(operation_name, e)

    def _success_result(self, operation_name: str, result: Any) -> Dict[str, Any]:
        """Standard success result format."""
        return {
            "success": True,
            "operation": operation_name,
            "strategy": self.__class__.__name__,
            "result": result,
        }

    def _error_result(self, operation_name: str, error: Exception) -> Dict[str, Any]:
        """Standard error result format."""
        return {
            "success": False,
            "operation": operation_name,
            "strategy": self.__class__.__name__,
            "error": str(error),
            "error_type": error.__class__.__name__,
        }

    @abstractmethod
    def resolve_conflict(self, existing_entity: Any, new_entity: Any) -> Any:
        """Resolve conflict between existing and new entity."""
        pass
