import time
from pathlib import Path

from ..requests import SavePullRequestsRequest, OperationResult
from .. import UseCase
from ...storage.protocols import StorageService


class SavePullRequestsUseCase(UseCase[SavePullRequestsRequest, OperationResult]):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: SavePullRequestsRequest) -> OperationResult:
        start_time = time.time()

        try:
            output_dir = Path(request.output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            prs_file = output_dir / "pull_requests.json"
            self._storage_service.save_data(request.pull_requests, prs_file)

            execution_time = time.time() - start_time

            return OperationResult(
                success=True,
                data_type="pull_requests",
                items_processed=len(request.pull_requests),
                execution_time_seconds=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return OperationResult(
                success=False,
                data_type="pull_requests",
                items_processed=0,
                error_message=str(e),
                execution_time_seconds=execution_time,
            )
