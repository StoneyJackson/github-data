import time
from pathlib import Path

from ...requests import LoadIssuesRequest, LoadIssuesResponse
from ... import UseCase
from ....storage.protocols import StorageService
from ....models import Issue


class LoadIssuesUseCase(UseCase[LoadIssuesRequest, LoadIssuesResponse]):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: LoadIssuesRequest) -> LoadIssuesResponse:
        start_time = time.time()

        try:
            issues_file = Path(request.input_path) / "issues.json"
            issues = self._storage_service.load_data(issues_file, Issue)

            execution_time = time.time() - start_time

            return LoadIssuesResponse(
                issues=issues,
                items_loaded=len(issues),
                execution_time_seconds=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"Failed to load issues: {str(e)}") from e
