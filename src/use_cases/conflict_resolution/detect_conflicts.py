from ..requests import LabelConflictDetectionRequest, LabelConflictDetectionResponse
from .. import UseCase
from ...models import Label


class DetectLabelConflictsUseCase(
    UseCase[LabelConflictDetectionRequest, LabelConflictDetectionResponse]
):
    def execute(
        self, request: LabelConflictDetectionRequest
    ) -> LabelConflictDetectionResponse:
        existing_by_name = {label.name: label for label in request.existing_labels}
        conflicting_names = []
        conflict_details = {}

        for label_to_restore in request.labels_to_restore:
            if label_to_restore.name in existing_by_name:
                existing_label = existing_by_name[label_to_restore.name]

                # Check for actual conflicts (different properties)
                if (
                    label_to_restore.color != existing_label.color
                    or label_to_restore.description != existing_label.description
                ):
                    conflicting_names.append(label_to_restore.name)
                    conflict_details[label_to_restore.name] = self._describe_conflict(
                        existing_label, label_to_restore
                    )

        return LabelConflictDetectionResponse(
            has_conflicts=len(conflicting_names) > 0,
            conflicting_names=conflicting_names,
            conflict_details=conflict_details,
        )

    def _describe_conflict(self, existing: Label, to_restore: Label) -> str:
        conflicts = []
        if existing.color != to_restore.color:
            conflicts.append(f"color: {existing.color} vs {to_restore.color}")
        if existing.description != to_restore.description:
            conflicts.append(
                f"description: '{existing.description}' vs '{to_restore.description}'"
            )
        return "; ".join(conflicts)
