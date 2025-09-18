"""
Label conflict resolution strategies.

Defines the available strategies for handling conflicts when restoring labels
that already exist in the target repository.
"""

from enum import Enum
from typing import List

from .entities import Label


class LabelConflictStrategy(Enum):
    """Strategies for handling label conflicts during restoration."""

    FAIL_IF_EXISTING = "fail-if-existing"
    FAIL_IF_CONFLICT = "fail-if-conflict"
    OVERWRITE = "overwrite"
    SKIP = "skip"
    DELETE_ALL = "delete-all"


def parse_conflict_strategy(strategy_str: str) -> LabelConflictStrategy:
    """Parse conflict strategy from string with validation."""
    try:
        return LabelConflictStrategy(strategy_str)
    except ValueError:
        valid_strategies = [s.value for s in LabelConflictStrategy]
        raise ValueError(
            f"Invalid conflict strategy '{strategy_str}'. "
            f"Valid options: {', '.join(valid_strategies)}"
        )


def detect_label_conflicts(
    existing_labels: List[Label], labels_to_restore: List[Label]
) -> List[str]:
    """Detect conflicting label names between existing and restoration sets."""
    existing_names = {label.name for label in existing_labels}
    restore_names = {label.name for label in labels_to_restore}
    return list(existing_names.intersection(restore_names))
