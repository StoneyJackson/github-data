from typing import List, Dict

from ...requests import AssociateSubIssuesRequest, AssociateSubIssuesResponse
from ... import UseCase
from ....models import SubIssue


class AssociateSubIssuesUseCase(
    UseCase[AssociateSubIssuesRequest, AssociateSubIssuesResponse]
):
    def execute(self, request: AssociateSubIssuesRequest) -> AssociateSubIssuesResponse:
        # Create a copy of issues to avoid modifying the original list
        issues_copy = [issue.model_copy() for issue in request.issues]

        # Create a mapping from issue number to issue index
        issue_number_to_index = {issue.number: i for i, issue in enumerate(issues_copy)}

        # Group sub-issues by parent issue number
        sub_issues_by_parent: Dict[int, List[SubIssue]] = {}
        for sub_issue in request.sub_issues:
            parent_number = sub_issue.parent_issue_number
            if parent_number not in sub_issues_by_parent:
                sub_issues_by_parent[parent_number] = []
            sub_issues_by_parent[parent_number].append(sub_issue)

        # Associate sub-issues with their parent issues
        items_processed = 0
        for parent_number, child_sub_issues in sub_issues_by_parent.items():
            if parent_number in issue_number_to_index:
                parent_index = issue_number_to_index[parent_number]
                # Sort sub-issues by position
                sorted_sub_issues = sorted(child_sub_issues, key=lambda si: si.position)
                issues_copy[parent_index].sub_issues = sorted_sub_issues
                items_processed += len(sorted_sub_issues)

        return AssociateSubIssuesResponse(
            updated_issues=issues_copy, items_processed=items_processed
        )
