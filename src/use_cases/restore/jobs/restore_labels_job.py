from typing import Any, Dict
from ...requests import OperationResult, RestoreLabelsRequest, LoadLabelsRequest
from ..loading.load_labels import LoadLabelsUseCase
from ..restoration.restore_labels import RestoreLabelsUseCase
from . import RestoreJob


class RestoreLabelsJob(RestoreJob):
    def __init__(
        self,
        repository_name: str,
        input_path: str,
        conflict_strategy: str,
        load_labels: LoadLabelsUseCase,
        restore_labels: RestoreLabelsUseCase,
    ):
        super().__init__("restore_labels")
        self.repository_name = repository_name
        self.input_path = input_path
        self.conflict_strategy = conflict_strategy
        self._load_labels = load_labels
        self._restore_labels = restore_labels

    def execute(self, context: Dict[str, Any]) -> OperationResult:
        try:
            # Load labels from file
            load_response = self._load_labels.execute(
                LoadLabelsRequest(input_path=self.input_path)
            )

            # Restore labels
            result = self._restore_labels.execute(
                RestoreLabelsRequest(
                    repository_name=self.repository_name,
                    labels=load_response.labels,
                    conflict_strategy=self.conflict_strategy,
                )
            )

            return result

        except Exception as e:
            # Re-raise JSON decode errors as-is for test compatibility
            import json

            if isinstance(e, json.JSONDecodeError):
                raise
            return OperationResult(
                success=False,
                data_type="labels",
                error_message=f"Label restoration job failed: {str(e)}",
            )
