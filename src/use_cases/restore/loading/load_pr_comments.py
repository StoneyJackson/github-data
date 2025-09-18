import time
from pathlib import Path

from ...requests import LoadPRCommentsRequest, LoadPRCommentsResponse
from ... import UseCase
from ....storage.protocols import StorageService
from ....models import PullRequestComment


class LoadPRCommentsUseCase(UseCase[LoadPRCommentsRequest, LoadPRCommentsResponse]):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: LoadPRCommentsRequest) -> LoadPRCommentsResponse:
        start_time = time.time()

        try:
            pr_comments_file = Path(request.input_path) / "pr_comments.json"
            pr_comments = self._storage_service.load_data(
                pr_comments_file, PullRequestComment
            )

            execution_time = time.time() - start_time

            return LoadPRCommentsResponse(
                pr_comments=pr_comments,
                items_loaded=len(pr_comments),
                execution_time_seconds=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"Failed to load PR comments: {str(e)}") from e
