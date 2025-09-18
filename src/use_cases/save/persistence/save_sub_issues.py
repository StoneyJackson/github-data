import time
from pathlib import Path

from ...requests import SaveSubIssuesRequest, OperationResult
from ... import UseCase
from ....storage.protocols import StorageService


class SaveSubIssuesUseCase(UseCase[SaveSubIssuesRequest, OperationResult]):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: SaveSubIssuesRequest) -> OperationResult:
        start_time = time.time()

        try:
            output_dir = Path(request.output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            sub_issues_file = output_dir / "sub_issues.json"
            self._storage_service.save_data(request.sub_issues, sub_issues_file)

            execution_time = time.time() - start_time

            return OperationResult(
                success=True,
                data_type="sub_issues",
                items_processed=len(request.sub_issues),
                execution_time_seconds=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return OperationResult(
                success=False,
                data_type="sub_issues",
                items_processed=0,
                error_message=str(e),
                execution_time_seconds=execution_time,
            )
