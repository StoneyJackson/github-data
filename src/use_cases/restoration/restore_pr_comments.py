import time

from ..requests import RestorePRCommentsRequest, OperationResult
from .. import UseCase
from ...github.protocols import RepositoryService
from ...models import PullRequestComment


class RestorePRCommentsUseCase(UseCase[RestorePRCommentsRequest, OperationResult]):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: RestorePRCommentsRequest) -> OperationResult:
        start_time = time.time()

        try:
            created_count = 0

            for pr_comment in request.pr_comments:
                # Map original PR number to new PR number
                if pr_comment.pull_request_number not in request.pr_number_mapping:
                    print(
                        f"Warning: PR comment {pr_comment.id} references "
                        f"unmapped PR #{pr_comment.pull_request_number}, skipping"
                    )
                    continue

                new_pr_number = request.pr_number_mapping[
                    pr_comment.pull_request_number
                ]

                # Prepare comment body with metadata if requested
                comment_body = self._prepare_comment_body(
                    pr_comment, request.include_original_metadata
                )

                # Create PR comment
                self._github_service.create_pull_request_comment(
                    request.repository_name, new_pr_number, comment_body
                )
                created_count += 1

            execution_time = time.time() - start_time

            return OperationResult(
                success=True,
                data_type="pr_comments",
                items_processed=created_count,
                execution_time_seconds=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return OperationResult(
                success=False,
                data_type="pr_comments",
                error_message=str(e),
                execution_time_seconds=execution_time,
            )

    def _prepare_comment_body(
        self, pr_comment: PullRequestComment, include_metadata: bool
    ) -> str:
        if include_metadata:
            from ...github.metadata import add_pr_comment_metadata_footer

            return add_pr_comment_metadata_footer(pr_comment)
        return pr_comment.body or ""
