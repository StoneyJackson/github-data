"""
Use cases package - backward compatibility layer.

DEPRECATED: This package structure is deprecated in favor of entity-specific use cases.
New code should import directly from src.entities.<entity_name> packages.

This module provides backward compatibility for existing imports.
"""

import warnings
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class UseCase(ABC, Generic[T, R]):
    @abstractmethod
    def execute(self, request: T) -> R:
        pass


# Re-export entity-specific use cases for backward compatibility
try:
    from ..entities.labels import SaveLabelsUseCase, RestoreLabelsUseCase  # noqa: F401
    from ..entities.issues import SaveIssuesUseCase, RestoreIssuesUseCase  # noqa: F401
    from ..entities.comments import (  # noqa: F401
        SaveCommentsUseCase,
        RestoreCommentsUseCase,
    )
    from ..entities.pull_requests import (  # noqa: F401
        SavePullRequestsUseCase,
        RestorePullRequestsUseCase,
    )

    # Issue deprecation warning
    warnings.warn(
        "Importing from src.use_cases is deprecated. "
        "Use 'from src.entities.<entity> import UseCase' instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    __all__ = [
        "UseCase",
        "SaveLabelsUseCase",
        "RestoreLabelsUseCase",
        "SaveIssuesUseCase",
        "RestoreIssuesUseCase",
        "SaveCommentsUseCase",
        "RestoreCommentsUseCase",
        "SavePullRequestsUseCase",
        "RestorePullRequestsUseCase",
    ]
except ImportError:
    # During initial migration, entity imports might not be available yet
    __all__ = ["UseCase"]
