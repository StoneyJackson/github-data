from ...requests import ValidateSubIssueDataRequest, OperationResult
from ... import UseCase


class ValidateSubIssueDataUseCase(
    UseCase[ValidateSubIssueDataRequest, OperationResult]
):
    def execute(self, request: ValidateSubIssueDataRequest) -> OperationResult:
        try:
            # At this point, all sub-issues should have valid parents and children
            # since filtering is done in the job
            missing_parents = []
            missing_children = []

            for sub_issue in request.sub_issues:
                if sub_issue.parent_issue_number not in request.issue_number_mapping:
                    missing_parents.append(sub_issue.parent_issue_number)

                if sub_issue.sub_issue_number not in request.issue_number_mapping:
                    missing_children.append(sub_issue.sub_issue_number)

            if missing_parents or missing_children:
                error_parts = []
                if missing_parents:
                    error_parts.append(f"Missing parent issues: {missing_parents}")
                if missing_children:
                    error_parts.append(f"Missing child issues: {missing_children}")

                return OperationResult(
                    success=False,
                    data_type="sub_issue_validation",
                    error_message="; ".join(error_parts),
                )

            return OperationResult(
                success=True,
                data_type="sub_issue_validation",
                items_processed=len(request.sub_issues),
            )

        except Exception as e:
            return OperationResult(
                success=False,
                data_type="sub_issue_validation",
                error_message=f"Sub-issue validation failed: {str(e)}",
            )
