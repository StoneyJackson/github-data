import time

from ...requests import RestoreSubIssuesRequest, OperationResult
from ... import UseCase
from ....github.protocols import RepositoryService


class RestoreSubIssuesUseCase(UseCase[RestoreSubIssuesRequest, OperationResult]):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: RestoreSubIssuesRequest) -> OperationResult:
        start_time = time.time()

        try:
            created_count = 0

            # Process sub-issues by depth to maintain hierarchy
            for depth in sorted(request.sub_issues_by_depth.keys()):
                sub_issues_at_depth = request.sub_issues_by_depth[depth]

                for sub_issue in sub_issues_at_depth:
                    # Map original issue numbers to new issue numbers
                    if (
                        sub_issue.parent_issue_number
                        not in request.issue_number_mapping
                    ):
                        print(
                            f"Warning: Sub-issue references unmapped parent "
                            f"#{sub_issue.parent_issue_number}, skipping"
                        )
                        continue

                    if sub_issue.sub_issue_number not in request.issue_number_mapping:
                        print(
                            f"Warning: Sub-issue references unmapped child "
                            f"#{sub_issue.sub_issue_number}, skipping"
                        )
                        continue

                    parent_number = request.issue_number_mapping[
                        sub_issue.parent_issue_number
                    ]
                    child_number = request.issue_number_mapping[
                        sub_issue.sub_issue_number
                    ]

                    # Create sub-issue relationship
                    self._github_service.add_sub_issue(
                        request.repository_name, parent_number, child_number
                    )
                    created_count += 1

            execution_time = time.time() - start_time

            return OperationResult(
                success=True,
                data_type="sub_issues",
                items_processed=created_count,
                execution_time_seconds=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return OperationResult(
                success=False,
                data_type="sub_issues",
                error_message=str(e),
                execution_time_seconds=execution_time,
            )
