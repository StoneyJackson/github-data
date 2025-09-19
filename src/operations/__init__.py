"""Operations package - main orchestration interface."""

# Strategy-based operations
from .save import save_repository_data_with_strategy_pattern
from .restore.restore import restore_repository_data_with_strategy_pattern

__all__ = [
    "save_repository_data_with_strategy_pattern",
    "restore_repository_data_with_strategy_pattern",
]
