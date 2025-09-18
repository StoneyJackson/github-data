from collections import defaultdict

from ...requests import SubIssueHierarchyRequest, SubIssueHierarchyResponse
from ... import UseCase
from ....entities import SubIssue


class OrganizeByDepthUseCase(
    UseCase[SubIssueHierarchyRequest, SubIssueHierarchyResponse]
):
    def execute(self, request: SubIssueHierarchyRequest) -> SubIssueHierarchyResponse:
        # Build parent-child mapping
        children_by_parent = defaultdict(list)
        parents_by_child = {}

        for sub_issue in request.sub_issues:
            parent_id = sub_issue.parent_issue_number
            child_id = sub_issue.sub_issue_number

            if (
                parent_id in request.issue_number_mapping
                and child_id in request.issue_number_mapping
            ):
                children_by_parent[parent_id].append(sub_issue)
                parents_by_child[child_id] = parent_id

        # Calculate depth for each sub-issue
        sub_issues_by_depth = defaultdict(list)
        processed = set()
        max_depth = 0

        def calculate_depth(sub_issue: SubIssue, current_depth: int = 0) -> None:
            nonlocal max_depth

            if sub_issue.sub_issue_number in processed:
                return

            processed.add(sub_issue.sub_issue_number)
            sub_issues_by_depth[current_depth].append(sub_issue)
            max_depth = max(max_depth, current_depth)

            # Process children at next depth level
            for child_sub_issue in children_by_parent.get(
                sub_issue.sub_issue_number, []
            ):
                calculate_depth(child_sub_issue, current_depth + 1)

        # Find root sub-issues (those whose parent is not also a child)
        root_sub_issues = []
        for sub_issue in request.sub_issues:
            parent_id = sub_issue.parent_issue_number
            # If the parent is not a child of another issue, this is a root sub-issue
            if parent_id not in parents_by_child:
                root_sub_issues.append(sub_issue)

        # Process from roots
        for root in root_sub_issues:
            calculate_depth(root, 0)

        return SubIssueHierarchyResponse(
            sub_issues_by_depth=dict(sub_issues_by_depth),
            max_depth=max_depth,
            circular_dependencies=[],  # Should be detected by separate use case
        )
