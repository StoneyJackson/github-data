import time
from typing import Optional

from ...requests import RestoreIssuesRequest, RestoreIssuesResponse
from ... import UseCase
from ....github.protocols import RepositoryService
from ....entities import Issue


class RestoreIssuesUseCase(UseCase[RestoreIssuesRequest, RestoreIssuesResponse]):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: RestoreIssuesRequest) -> RestoreIssuesResponse:
        start_time = time.time()
        issue_number_mapping = {}

        try:
            for issue in request.issues:
                # Prepare issue body with metadata if requested
                issue_body = self._prepare_issue_body(
                    issue, request.include_original_metadata
                )
                label_names = [label.name for label in issue.labels]

                # Create issue
                created_issue = self._github_service.create_issue(
                    request.repository_name, issue.title, issue_body, label_names
                )
                issue_number_mapping[issue.number] = created_issue["number"]

                # Handle closed state
                if issue.state == "closed":
                    self._close_issue_if_needed(
                        request.repository_name,
                        created_issue["number"],
                        issue.state_reason,
                    )

            execution_time = time.time() - start_time

            return RestoreIssuesResponse(
                issue_number_mapping=issue_number_mapping,
                issues_created=len(issue_number_mapping),
                execution_time_seconds=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = (
                str(e) or f"Exception of type {type(e).__name__} with no message"
            )
            raise RuntimeError(f"Failed to restore issues: {error_msg}") from e

    def _prepare_issue_body(self, issue: Issue, include_metadata: bool) -> str:
        if include_metadata:
            from ....github.metadata import add_issue_metadata_footer

            return add_issue_metadata_footer(issue)
        return issue.body or ""

    def _close_issue_if_needed(
        self, repo_name: str, issue_number: int, state_reason: Optional[str]
    ) -> None:
        try:
            self._github_service.close_issue(repo_name, issue_number, state_reason)
        except Exception as e:
            print(f"Warning: Failed to close issue #{issue_number}: {e}")
