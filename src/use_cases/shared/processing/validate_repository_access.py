from ...requests import ValidateRepositoryAccessRequest, OperationResult
from ... import UseCase
from ....github.protocols import RepositoryService


class ValidateRepositoryAccessUseCase(
    UseCase[ValidateRepositoryAccessRequest, OperationResult]
):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: ValidateRepositoryAccessRequest) -> OperationResult:
        try:
            # Attempt to fetch basic repository info to validate access
            # For now, we'll try to get labels as a lightweight way to test access
            self._github_service.get_repository_labels(request.repository_name)

            return OperationResult(
                success=True, data_type="repository_validation", items_processed=1
            )
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="repository_validation",
                error_message=f"Cannot access repository "
                f"{request.repository_name}: {str(e)}",
            )
