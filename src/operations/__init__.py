"""Operations package - orchestrator interface.

Legacy save/restore functions removed. Use orchestrators with EntityRegistry.
"""

from .save.orchestrator import StrategyBasedSaveOrchestrator
from .restore.orchestrator import StrategyBasedRestoreOrchestrator

__all__ = [
    "StrategyBasedSaveOrchestrator",
    "StrategyBasedRestoreOrchestrator",
]
