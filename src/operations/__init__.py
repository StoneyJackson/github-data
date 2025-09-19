"""Operations package - main orchestration interface."""

# Legacy compatibility imports - preserve existing save/restore functions
from .save import save_repository_data_with_services
from .restore.restore import restore_repository_data_with_strategy_pattern

__all__ = [
    # Legacy functions
    "save_repository_data_with_services",
    "restore_repository_data_with_strategy_pattern",
]
