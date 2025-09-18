from typing import Any, Dict
from ...requests import (
    OperationResult,
    LoadSubIssuesRequest,
    ValidateSubIssueDataRequest,
    SubIssueHierarchyRequest,
    RestoreSubIssuesRequest,
)
from ..loading.load_sub_issues import LoadSubIssuesUseCase
from ..sub_issue_management.validate_sub_issue_data import ValidateSubIssueDataUseCase
from ..sub_issue_management.detect_circular_dependencies import (
    DetectCircularDependenciesUseCase,
)
from ..sub_issue_management.organize_by_depth import OrganizeByDepthUseCase
from ..restoration.restore_sub_issues import RestoreSubIssuesUseCase
from . import RestoreJob


class RestoreSubIssuesJob(RestoreJob):
    def __init__(
        self,
        repository_name: str,
        input_path: str,
        load_sub_issues: LoadSubIssuesUseCase,
        validate_sub_issues: ValidateSubIssueDataUseCase,
        detect_circular_deps: DetectCircularDependenciesUseCase,
        organize_by_depth: OrganizeByDepthUseCase,
        restore_sub_issues: RestoreSubIssuesUseCase,
    ):
        super().__init__("restore_sub_issues", dependencies=["restore_issues"])
        self.repository_name = repository_name
        self.input_path = input_path
        self._load_sub_issues = load_sub_issues
        self._validate_sub_issues = validate_sub_issues
        self._detect_circular_deps = detect_circular_deps
        self._organize_by_depth = organize_by_depth
        self._restore_sub_issues = restore_sub_issues

    def execute(self, context: Dict[str, Any]) -> OperationResult:
        try:
            # Get issue number mapping from dependency
            issue_number_mapping = context.get("issue_number_mapping", {})
            if not issue_number_mapping:
                return OperationResult(
                    success=False,
                    data_type="sub_issues",
                    error_message=(
                        "Issue number mapping not available from RestoreIssuesJob"
                    ),
                )

            # Load sub-issues from file
            load_response = self._load_sub_issues.execute(
                LoadSubIssuesRequest(input_path=self.input_path)
            )

            if not load_response.sub_issues:
                return OperationResult(
                    success=True, data_type="sub_issues", items_processed=0
                )

            # Filter sub-issues to only include those with valid parents
            valid_sub_issues = [
                sub_issue
                for sub_issue in load_response.sub_issues
                if sub_issue.parent_issue_number in issue_number_mapping
                and sub_issue.sub_issue_number in issue_number_mapping
            ]

            # Validate sub-issue data
            validation_result = self._validate_sub_issues.execute(
                ValidateSubIssueDataRequest(
                    sub_issues=valid_sub_issues,
                    issue_number_mapping=issue_number_mapping,
                )
            )

            if not validation_result.success:
                return validation_result

            # If no valid sub-issues, return success with 0 processed
            if not valid_sub_issues:
                return OperationResult(
                    success=True, data_type="sub_issues", items_processed=0
                )

            # Detect circular dependencies
            circular_deps_response = self._detect_circular_deps.execute(
                SubIssueHierarchyRequest(
                    sub_issues=valid_sub_issues,
                    issue_number_mapping=issue_number_mapping,
                )
            )

            if circular_deps_response.has_circular_dependencies:
                return OperationResult(
                    success=False,
                    data_type="sub_issues",
                    error_message=(
                        f"Circular dependencies detected: "
                        f"{circular_deps_response.circular_dependency_chains}"
                    ),
                )

            # Organize by depth for proper ordering
            hierarchy_response = self._organize_by_depth.execute(
                SubIssueHierarchyRequest(
                    sub_issues=valid_sub_issues,
                    issue_number_mapping=issue_number_mapping,
                )
            )

            # Restore sub-issues in dependency order
            result = self._restore_sub_issues.execute(
                RestoreSubIssuesRequest(
                    repository_name=self.repository_name,
                    sub_issues_by_depth=hierarchy_response.sub_issues_by_depth,
                    issue_number_mapping=issue_number_mapping,
                )
            )

            return result

        except Exception as e:
            return OperationResult(
                success=False,
                data_type="sub_issues",
                error_message=f"Sub-issue restoration job failed: {str(e)}",
            )
