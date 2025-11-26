"""Operations package - orchestrator interface.

Legacy save/restore functions removed. Use orchestrators with EntityRegistry.
"""

from .save.orchestrator import StrategyBasedSaveOrchestrator
from .restore.orchestrator import StrategyBasedRestoreOrchestrator
from github_data_core.operations.orchestrator_base import StrategyBasedOrchestrator

__all__ = [
    "StrategyBasedSaveOrchestrator",
    "StrategyBasedRestoreOrchestrator",
    "StrategyBasedOrchestrator",
]
