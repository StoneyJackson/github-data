from ..requests import ApplyLabelStrategyRequest, ApplyLabelStrategyResponse
from .. import UseCase
from ...github.protocols import RepositoryService


class DeleteAllStrategyUseCase(
    UseCase[ApplyLabelStrategyRequest, ApplyLabelStrategyResponse]
):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: ApplyLabelStrategyRequest) -> ApplyLabelStrategyResponse:
        try:
            # Delete all existing labels
            for existing_label in request.existing_labels:
                self._github_service.delete_label(
                    request.repository_name, existing_label.name
                )

            return ApplyLabelStrategyResponse(
                success=True, filtered_labels=request.labels_to_restore
            )
        except Exception as e:
            return ApplyLabelStrategyResponse(
                success=False,
                error_message=f"Failed to delete existing labels: {str(e)}",
            )
