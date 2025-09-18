from typing import Any, Dict
from ...requests import (
    OperationResult,
    RestorePullRequestsRequest,
    LoadPullRequestsRequest,
)
from ..loading.load_pull_requests import LoadPullRequestsUseCase
from ..restoration.restore_pull_requests import RestorePullRequestsUseCase
from . import RestoreJob


class RestorePullRequestsJob(RestoreJob):
    def __init__(
        self,
        repository_name: str,
        input_path: str,
        include_original_metadata: bool,
        load_pull_requests: LoadPullRequestsUseCase,
        restore_pull_requests: RestorePullRequestsUseCase,
    ):
        super().__init__("restore_pull_requests")
        self.repository_name = repository_name
        self.input_path = input_path
        self.include_original_metadata = include_original_metadata
        self._load_pull_requests = load_pull_requests
        self._restore_pull_requests = restore_pull_requests

    def execute(self, context: Dict[str, Any]) -> OperationResult:
        try:
            # Load pull requests from file
            load_response = self._load_pull_requests.execute(
                LoadPullRequestsRequest(input_path=self.input_path)
            )

            # Restore pull requests
            result = self._restore_pull_requests.execute(
                RestorePullRequestsRequest(
                    repository_name=self.repository_name,
                    pull_requests=load_response.pull_requests,
                    include_original_metadata=self.include_original_metadata,
                )
            )

            # Store PR number mapping for dependent jobs (if any)
            # Note: This would need to be implemented if PR comment restoration needs it
            # context["pr_number_mapping"] = pr_number_mapping

            return result

        except Exception as e:
            return OperationResult(
                success=False,
                data_type="pull_requests",
                error_message=f"Pull request restoration job failed: {str(e)}",
            )
