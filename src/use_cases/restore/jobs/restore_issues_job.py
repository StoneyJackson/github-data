from typing import Any, Dict
from ...requests import OperationResult, RestoreIssuesRequest, LoadIssuesRequest
from ..loading.load_issues import LoadIssuesUseCase
from ..restoration.restore_issues import RestoreIssuesUseCase
from . import RestoreJob


class RestoreIssuesJob(RestoreJob):
    def __init__(
        self,
        repository_name: str,
        input_path: str,
        include_original_metadata: bool,
        load_issues: LoadIssuesUseCase,
        restore_issues: RestoreIssuesUseCase,
    ):
        super().__init__("restore_issues")
        self.repository_name = repository_name
        self.input_path = input_path
        self.include_original_metadata = include_original_metadata
        self._load_issues = load_issues
        self._restore_issues = restore_issues

    def execute(self, context: Dict[str, Any]) -> OperationResult:
        try:
            # Load issues from file
            load_response = self._load_issues.execute(
                LoadIssuesRequest(input_path=self.input_path)
            )

            # Restore issues
            restore_response = self._restore_issues.execute(
                RestoreIssuesRequest(
                    repository_name=self.repository_name,
                    issues=load_response.issues,
                    include_original_metadata=self.include_original_metadata,
                )
            )

            # Store issue number mapping in context for dependent jobs
            context["issue_number_mapping"] = restore_response.issue_number_mapping

            return OperationResult(
                success=True,
                data_type="issues",
                items_processed=restore_response.issues_created,
                execution_time_seconds=restore_response.execution_time_seconds,
            )

        except Exception as e:
            return OperationResult(
                success=False,
                data_type="issues",
                error_message=f"Issue restoration job failed: {str(e)}",
            )
