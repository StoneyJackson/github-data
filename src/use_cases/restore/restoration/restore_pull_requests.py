import time

from ...requests import RestorePullRequestsRequest, OperationResult
from ... import UseCase
from ....github.protocols import RepositoryService
from ....models import PullRequest


class RestorePullRequestsUseCase(UseCase[RestorePullRequestsRequest, OperationResult]):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: RestorePullRequestsRequest) -> OperationResult:
        start_time = time.time()

        try:
            created_count = 0
            pr_number_mapping = {}

            for pr in request.pull_requests:
                # Prepare PR body with metadata if requested
                pr_body = self._prepare_pr_body(pr, request.include_original_metadata)

                # Create pull request
                created_pr = self._github_service.create_pull_request(
                    request.repository_name,
                    pr.title,
                    pr_body,
                    pr.head_ref,
                    pr.base_ref,
                )

                pr_number_mapping[pr.number] = created_pr["number"]

                # Handle closed/merged state
                if pr.state in ["closed", "merged"]:
                    self._handle_pr_state(
                        request.repository_name, created_pr["number"], pr
                    )

                created_count += 1

            execution_time = time.time() - start_time

            return OperationResult(
                success=True,
                data_type="pull_requests",
                items_processed=created_count,
                execution_time_seconds=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return OperationResult(
                success=False,
                data_type="pull_requests",
                error_message=str(e),
                execution_time_seconds=execution_time,
            )

    def _prepare_pr_body(self, pr: PullRequest, include_metadata: bool) -> str:
        if include_metadata:
            from ....github.metadata import add_pr_metadata_footer

            return add_pr_metadata_footer(pr)
        return pr.body or ""

    def _handle_pr_state(
        self, repo_name: str, pr_number: int, original_pr: PullRequest
    ) -> None:
        try:
            if original_pr.state == "closed":
                # Note: close_pull_request method not available in RepositoryService
                # protocol
                print(f"Warning: Cannot restore closed state for PR #{pr_number}")
            elif original_pr.state == "merged":
                # Note: Cannot actually merge PRs via API after creation
                print(f"Warning: Cannot restore merged state for PR #{pr_number}")
        except Exception as e:
            print(f"Warning: Failed to set PR #{pr_number} state: {e}")
