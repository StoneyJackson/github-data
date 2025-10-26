"""Save operations module.

Legacy save_repository_data_with_config removed.
Use StrategyBasedSaveOrchestrator with EntityRegistry instead.
"""

from .orchestrator import StrategyBasedSaveOrchestrator

__all__ = ["StrategyBasedSaveOrchestrator"]
