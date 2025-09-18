from typing import Any, Dict
from ..requests import OperationResult, RestoreCommentsRequest, LoadCommentsRequest
from ..loading.load_comments import LoadCommentsUseCase
from ..restoration.restore_comments import RestoreCommentsUseCase
from . import RestoreJob


class RestoreCommentsJob(RestoreJob):
    def __init__(
        self,
        repository_name: str,
        input_path: str,
        include_original_metadata: bool,
        load_comments: LoadCommentsUseCase,
        restore_comments: RestoreCommentsUseCase,
    ):
        super().__init__("restore_comments", dependencies=["restore_issues"])
        self.repository_name = repository_name
        self.input_path = input_path
        self.include_original_metadata = include_original_metadata
        self._load_comments = load_comments
        self._restore_comments = restore_comments

    def execute(self, context: Dict[str, Any]) -> OperationResult:
        try:
            # Get issue number mapping from dependency
            issue_number_mapping = context.get("issue_number_mapping")
            if issue_number_mapping is None:
                return OperationResult(
                    success=False,
                    data_type="comments",
                    error_message=(
                        "Issue number mapping not available from RestoreIssuesJob"
                    ),
                )
            # Empty mapping is valid when there are no issues

            # Load comments from file
            load_response = self._load_comments.execute(
                LoadCommentsRequest(input_path=self.input_path)
            )

            # Restore comments
            result = self._restore_comments.execute(
                RestoreCommentsRequest(
                    repository_name=self.repository_name,
                    comments=load_response.comments,
                    issue_number_mapping=issue_number_mapping,
                    include_original_metadata=self.include_original_metadata,
                )
            )

            return result

        except Exception as e:
            return OperationResult(
                success=False,
                data_type="comments",
                error_message=f"Comment restoration job failed: {str(e)}",
            )
