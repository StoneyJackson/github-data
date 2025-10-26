"""Restore operations module.

Legacy restore_repository_data_with_config removed.
Use StrategyBasedRestoreOrchestrator with EntityRegistry instead.
"""

from .orchestrator import StrategyBasedRestoreOrchestrator

__all__ = ["StrategyBasedRestoreOrchestrator"]
