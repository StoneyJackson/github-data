import time
from pathlib import Path

from ...requests import SaveIssuesRequest, OperationResult
from ... import UseCase
from ....storage.protocols import StorageService


class SaveIssuesUseCase(UseCase[SaveIssuesRequest, OperationResult]):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: SaveIssuesRequest) -> OperationResult:
        start_time = time.time()

        try:
            output_dir = Path(request.output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            issues_file = output_dir / "issues.json"
            self._storage_service.save_data(request.issues, issues_file)

            execution_time = time.time() - start_time

            return OperationResult(
                success=True,
                data_type="issues",
                items_processed=len(request.issues),
                execution_time_seconds=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return OperationResult(
                success=False,
                data_type="issues",
                items_processed=0,
                error_message=str(e),
                execution_time_seconds=execution_time,
            )
