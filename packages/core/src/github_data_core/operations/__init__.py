"""Operations package - base orchestrator interface.

Concrete save/restore orchestrators are in github_data_tools.operations.
"""

from .orchestrator_base import StrategyBasedOrchestrator
from .strategy_factory import StrategyFactory

__all__ = [
    "StrategyBasedOrchestrator",
    "StrategyFactory",
]
