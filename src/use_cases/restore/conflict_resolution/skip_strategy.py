from ...requests import (
    ApplyLabelStrategyRequest,
    ApplyLabelStrategyResponse,
    LabelConflictDetectionRequest,
)
from ... import UseCase
from .detect_conflicts import DetectLabelConflictsUseCase


class SkipStrategyUseCase(
    UseCase[ApplyLabelStrategyRequest, ApplyLabelStrategyResponse]
):
    def __init__(self, detect_conflicts: DetectLabelConflictsUseCase):
        self._detect_conflicts = detect_conflicts

    def execute(self, request: ApplyLabelStrategyRequest) -> ApplyLabelStrategyResponse:
        # Detect conflicts
        self._detect_conflicts.execute(
            LabelConflictDetectionRequest(
                existing_labels=request.existing_labels,
                labels_to_restore=request.labels_to_restore,
            )
        )

        # Filter out conflicting labels
        filtered_labels = []
        existing_names = {label.name for label in request.existing_labels}

        for label in request.labels_to_restore:
            if label.name not in existing_names:
                filtered_labels.append(label)

        return ApplyLabelStrategyResponse(success=True, filtered_labels=filtered_labels)
