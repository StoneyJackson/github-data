from ...requests import SubIssueHierarchyRequest, CircularDependencyResponse
from ... import UseCase


class DetectCircularDependenciesUseCase(
    UseCase[SubIssueHierarchyRequest, CircularDependencyResponse]
):
    def execute(self, request: SubIssueHierarchyRequest) -> CircularDependencyResponse:
        parents_by_child = {}
        circular_dependencies = []

        # Build parent-child mapping
        for sub_issue in request.sub_issues:
            parent_id = sub_issue.parent_issue_number
            child_id = sub_issue.sub_issue_number

            if (
                parent_id in request.issue_number_mapping
                and child_id in request.issue_number_mapping
            ):
                parents_by_child[child_id] = parent_id

        # Detect cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node: int) -> bool:
            if node in rec_stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            if node in parents_by_child:
                parent = parents_by_child[node]
                if has_cycle(parent):
                    circular_dependencies.append(f"#{node} -> #{parent}")
                    return True

            rec_stack.remove(node)
            return False

        # Check all nodes for cycles
        for child_id in parents_by_child.keys():
            if child_id not in visited:
                has_cycle(child_id)

        return CircularDependencyResponse(
            has_circular_dependencies=len(circular_dependencies) > 0,
            circular_dependency_chains=circular_dependencies,
        )
