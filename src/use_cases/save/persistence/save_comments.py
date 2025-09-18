import time
from pathlib import Path

from ...requests import SaveCommentsRequest, OperationResult
from ... import UseCase
from ....storage.protocols import StorageService


class SaveCommentsUseCase(UseCase[SaveCommentsRequest, OperationResult]):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: SaveCommentsRequest) -> OperationResult:
        start_time = time.time()

        try:
            output_dir = Path(request.output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            comments_file = output_dir / "comments.json"
            self._storage_service.save_data(request.comments, comments_file)

            execution_time = time.time() - start_time

            return OperationResult(
                success=True,
                data_type="comments",
                items_processed=len(request.comments),
                execution_time_seconds=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return OperationResult(
                success=False,
                data_type="comments",
                items_processed=0,
                error_message=str(e),
                execution_time_seconds=execution_time,
            )
