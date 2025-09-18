from ...requests import ApplyLabelStrategyRequest, ApplyLabelStrategyResponse
from ... import UseCase


class FailIfExistingStrategyUseCase(
    UseCase[ApplyLabelStrategyRequest, ApplyLabelStrategyResponse]
):
    def execute(self, request: ApplyLabelStrategyRequest) -> ApplyLabelStrategyResponse:
        if request.existing_labels:
            return ApplyLabelStrategyResponse(
                success=False,
                error_message=(
                    f"Repository has {len(request.existing_labels)} existing labels. "
                    f"Change strategy to allow restoration with existing labels."
                ),
            )

        return ApplyLabelStrategyResponse(
            success=True, filtered_labels=request.labels_to_restore
        )
