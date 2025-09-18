import time
from pathlib import Path

from ..requests import LoadLabelsRequest, LoadLabelsResponse
from .. import UseCase
from ...storage.protocols import StorageService
from ...models import Label


class LoadLabelsUseCase(UseCase[LoadLabelsRequest, LoadLabelsResponse]):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: LoadLabelsRequest) -> LoadLabelsResponse:
        start_time = time.time()

        try:
            labels_file = Path(request.input_path) / "labels.json"
            labels = self._storage_service.load_data(labels_file, Label)

            execution_time = time.time() - start_time

            return LoadLabelsResponse(
                labels=labels,
                items_loaded=len(labels),
                execution_time_seconds=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            # Re-raise JSON decode errors as-is for test compatibility
            import json

            if isinstance(e, json.JSONDecodeError):
                raise
            raise RuntimeError(f"Failed to load labels: {str(e)}") from e
