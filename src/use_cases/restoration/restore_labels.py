import time

from ..requests import RestoreLabelsRequest, OperationResult, ApplyLabelStrategyRequest
from .. import UseCase
from ...github.protocols import RepositoryService
from ..conflict_resolution.fail_if_existing_strategy import (
    FailIfExistingStrategyUseCase,
)
from ..conflict_resolution.fail_if_conflict_strategy import (
    FailIfConflictStrategyUseCase,
)
from ..conflict_resolution.delete_all_strategy import DeleteAllStrategyUseCase
from ..conflict_resolution.overwrite_strategy import OverwriteStrategyUseCase
from ..conflict_resolution.skip_strategy import SkipStrategyUseCase


class RestoreLabelsUseCase(UseCase[RestoreLabelsRequest, OperationResult]):
    def __init__(
        self,
        github_service: RepositoryService,
        fail_if_existing: FailIfExistingStrategyUseCase,
        fail_if_conflict: FailIfConflictStrategyUseCase,
        delete_all: DeleteAllStrategyUseCase,
        overwrite: OverwriteStrategyUseCase,
        skip: SkipStrategyUseCase,
    ):
        self._github_service = github_service
        self._strategies = {
            "fail-if-existing": fail_if_existing,
            "fail-if-conflict": fail_if_conflict,
            "delete-all": delete_all,
            "overwrite": overwrite,
            "skip": skip,
        }

    def execute(self, request: RestoreLabelsRequest) -> OperationResult:
        start_time = time.time()

        try:
            # Get existing labels
            from ...github import converters

            raw_existing = self._github_service.get_repository_labels(
                request.repository_name
            )
            existing_labels = [
                converters.convert_to_label(label_dict) for label_dict in raw_existing
            ]

            # Apply conflict resolution strategy
            strategy = self._strategies.get(request.conflict_strategy)
            if not strategy:
                raise ValueError(f"Unknown strategy: {request.conflict_strategy}")

            strategy_result = strategy.execute(
                ApplyLabelStrategyRequest(
                    repository_name=request.repository_name,
                    existing_labels=existing_labels,
                    labels_to_restore=request.labels,
                    conflict_strategy=request.conflict_strategy,
                )
            )

            if not strategy_result.success:
                execution_time = time.time() - start_time
                return OperationResult(
                    success=False,
                    data_type="labels",
                    error_message=strategy_result.error_message,
                    execution_time_seconds=execution_time,
                )

            # Create labels (strategy may have modified the list)
            labels_to_create = strategy_result.filtered_labels or request.labels
            created_count = 0

            for label in labels_to_create:
                try:
                    self._github_service.create_label(
                        request.repository_name,
                        label.name,
                        label.color,
                        label.description or "",
                    )
                    created_count += 1
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to create label '{label.name}': {e}"
                    ) from e

            execution_time = time.time() - start_time

            return OperationResult(
                success=True,
                data_type="labels",
                items_processed=created_count,
                execution_time_seconds=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return OperationResult(
                success=False,
                data_type="labels",
                error_message=str(e),
                execution_time_seconds=execution_time,
            )
