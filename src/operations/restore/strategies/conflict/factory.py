"""Factory for creating conflict resolution strategies."""

from typing import Dict, Type, List
from .base import BaseConflictStrategy
from .strategies import (
    SkipConflictStrategy,
    OverwriteConflictStrategy,
    RenameConflictStrategy,
    MergeConflictStrategy,
)


class ConflictStrategyFactory:
    """Factory for creating conflict resolution strategies."""

    _strategies: Dict[str, Type[BaseConflictStrategy]] = {
        "skip": SkipConflictStrategy,
        "overwrite": OverwriteConflictStrategy,
        "rename": RenameConflictStrategy,
        "merge": MergeConflictStrategy,
    }

    @classmethod
    def create_strategy(cls, strategy_name: str) -> BaseConflictStrategy:
        """Create conflict strategy by name."""
        if strategy_name not in cls._strategies:
            raise ValueError(f"Unknown conflict strategy: {strategy_name}")

        strategy_class = cls._strategies[strategy_name]
        return strategy_class()

    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """Get list of available strategy names."""
        return list(cls._strategies.keys())

    @classmethod
    def register_strategy(
        cls, name: str, strategy_class: Type[BaseConflictStrategy]
    ) -> None:
        """Register a new conflict strategy."""
        cls._strategies[name] = strategy_class
