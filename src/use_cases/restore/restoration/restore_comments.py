import time

from ...requests import RestoreCommentsRequest, OperationResult
from ... import UseCase
from ....github.protocols import RepositoryService
from ....entities import Comment


class RestoreCommentsUseCase(UseCase[RestoreCommentsRequest, OperationResult]):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: RestoreCommentsRequest) -> OperationResult:
        start_time = time.time()

        try:
            created_count = 0

            # Sort comments by creation time to keep chronological conversation order
            sorted_comments = sorted(request.comments, key=lambda c: c.created_at)

            for comment in sorted_comments:
                # Map original issue number to new issue number
                if comment.issue_number not in request.issue_number_mapping:
                    print(
                        f"Warning: Comment {comment.id} references unmapped "
                        f"issue #{comment.issue_number}, skipping"
                    )
                    continue

                new_issue_number = request.issue_number_mapping[comment.issue_number]

                # Prepare comment body with metadata if requested
                comment_body = self._prepare_comment_body(
                    comment, request.include_original_metadata
                )

                # Create comment
                self._github_service.create_issue_comment(
                    request.repository_name, new_issue_number, comment_body
                )
                created_count += 1

            execution_time = time.time() - start_time

            return OperationResult(
                success=True,
                data_type="comments",
                items_processed=created_count,
                execution_time_seconds=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return OperationResult(
                success=False,
                data_type="comments",
                error_message=str(e),
                execution_time_seconds=execution_time,
            )

    def _prepare_comment_body(self, comment: Comment, include_metadata: bool) -> str:
        if include_metadata:
            from ....github.metadata import add_comment_metadata_footer

            return add_comment_metadata_footer(comment)
        return comment.body or ""
