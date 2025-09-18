from ...requests import (
    ApplyLabelStrategyRequest,
    ApplyLabelStrategyResponse,
    LabelConflictDetectionRequest,
)
from ... import UseCase
from .detect_conflicts import DetectLabelConflictsUseCase


class FailIfConflictStrategyUseCase(
    UseCase[ApplyLabelStrategyRequest, ApplyLabelStrategyResponse]
):
    def __init__(self, detect_conflicts: DetectLabelConflictsUseCase):
        self._detect_conflicts = detect_conflicts

    def execute(self, request: ApplyLabelStrategyRequest) -> ApplyLabelStrategyResponse:
        # Detect conflicts
        conflict_result = self._detect_conflicts.execute(
            LabelConflictDetectionRequest(
                existing_labels=request.existing_labels,
                labels_to_restore=request.labels_to_restore,
            )
        )

        if conflict_result.has_conflicts:
            conflicts_desc = ", ".join(
                [
                    f"{name}: {details}"
                    for name, details in conflict_result.conflict_details.items()
                ]
            )
            return ApplyLabelStrategyResponse(
                success=False,
                error_message=f"Label conflicts detected: {conflicts_desc}",
            )

        return ApplyLabelStrategyResponse(
            success=True, filtered_labels=request.labels_to_restore
        )
