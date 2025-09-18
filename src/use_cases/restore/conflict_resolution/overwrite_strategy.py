from ...requests import (
    ApplyLabelStrategyRequest,
    ApplyLabelStrategyResponse,
    LabelConflictDetectionRequest,
)
from ... import UseCase
from ....github.protocols import RepositoryService
from .detect_conflicts import DetectLabelConflictsUseCase


class OverwriteStrategyUseCase(
    UseCase[ApplyLabelStrategyRequest, ApplyLabelStrategyResponse]
):
    def __init__(
        self,
        github_service: RepositoryService,
        detect_conflicts: DetectLabelConflictsUseCase,
    ):
        self._github_service = github_service
        self._detect_conflicts = detect_conflicts

    def execute(self, request: ApplyLabelStrategyRequest) -> ApplyLabelStrategyResponse:
        try:
            # Detect conflicts
            conflict_result = self._detect_conflicts.execute(
                LabelConflictDetectionRequest(
                    existing_labels=request.existing_labels,
                    labels_to_restore=request.labels_to_restore,
                )
            )

            # Delete conflicting labels to allow overwrite
            if conflict_result.has_conflicts:
                for conflicting_name in conflict_result.conflicting_names:
                    self._github_service.delete_label(
                        request.repository_name, conflicting_name
                    )

            return ApplyLabelStrategyResponse(
                success=True, filtered_labels=request.labels_to_restore
            )
        except Exception as e:
            return ApplyLabelStrategyResponse(
                success=False,
                error_message=f"Failed to overwrite conflicting labels: {str(e)}",
            )
