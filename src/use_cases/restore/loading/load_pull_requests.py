import time
from pathlib import Path

from ...requests import LoadPullRequestsRequest, LoadPullRequestsResponse
from ... import UseCase
from ....storage.protocols import StorageService
from ....models import PullRequest


class LoadPullRequestsUseCase(
    UseCase[LoadPullRequestsRequest, LoadPullRequestsResponse]
):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: LoadPullRequestsRequest) -> LoadPullRequestsResponse:
        start_time = time.time()

        try:
            prs_file = Path(request.input_path) / "pull_requests.json"
            pull_requests = self._storage_service.load_data(prs_file, PullRequest)

            execution_time = time.time() - start_time

            return LoadPullRequestsResponse(
                pull_requests=pull_requests,
                items_loaded=len(pull_requests),
                execution_time_seconds=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"Failed to load pull requests: {str(e)}") from e
