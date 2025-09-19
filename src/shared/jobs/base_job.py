"""Base job patterns for entity operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypeVar, Generic, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from ...github.protocols import RepositoryService
from ...storage.protocols import StorageService

T = TypeVar("T")


@dataclass
class JobResult(Generic[T]):
    """Standard job result wrapper."""

    success: bool
    data: T | None = None
    error: str | None = None
    metadata: Dict[str, Any] | None = None


class BaseEntityJob(ABC, Generic[T]):
    """Base class for entity-specific jobs."""

    def __init__(
        self,
        github_service: RepositoryService,
        storage_service: StorageService,
        repository: str,
        max_workers: int = 10,
    ):
        self.github_service = github_service
        self.storage_service = storage_service
        self.repository = repository
        self.max_workers = max_workers

    @abstractmethod
    def execute(self) -> JobResult[List[T]]:
        """Execute the job and return results."""
        pass

    def _parallel_process(
        self,
        items: List[Any],
        process_func: Callable[[Any], Any],
        max_workers: int | None = None,
    ) -> List[Any]:
        """Helper for parallel processing of items."""
        workers = max_workers or self.max_workers
        results = []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_item = {
                executor.submit(process_func, item): item for item in items
            }

            for future in as_completed(future_to_item):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as exc:
                    item = future_to_item[future]
                    print(f"Item {item} generated an exception: {exc}")

        return results
