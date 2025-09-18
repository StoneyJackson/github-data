import time
from pathlib import Path

from ...requests import LoadSubIssuesRequest, LoadSubIssuesResponse
from ... import UseCase
from ....storage.protocols import StorageService
from ....entities import SubIssue


class LoadSubIssuesUseCase(UseCase[LoadSubIssuesRequest, LoadSubIssuesResponse]):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: LoadSubIssuesRequest) -> LoadSubIssuesResponse:
        start_time = time.time()

        try:
            sub_issues_file = Path(request.input_path) / "sub_issues.json"
            sub_issues = self._storage_service.load_data(sub_issues_file, SubIssue)

            execution_time = time.time() - start_time

            return LoadSubIssuesResponse(
                sub_issues=sub_issues,
                items_loaded=len(sub_issues),
                execution_time_seconds=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"Failed to load sub-issues: {str(e)}") from e
