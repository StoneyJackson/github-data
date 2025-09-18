import time
from pathlib import Path

from ...requests import LoadCommentsRequest, LoadCommentsResponse
from ... import UseCase
from ....storage.protocols import StorageService
from ....models import Comment


class LoadCommentsUseCase(UseCase[LoadCommentsRequest, LoadCommentsResponse]):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: LoadCommentsRequest) -> LoadCommentsResponse:
        start_time = time.time()

        try:
            comments_file = Path(request.input_path) / "comments.json"
            comments = self._storage_service.load_data(comments_file, Comment)

            execution_time = time.time() - start_time

            return LoadCommentsResponse(
                comments=comments,
                items_loaded=len(comments),
                execution_time_seconds=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"Failed to load comments: {str(e)}") from e
