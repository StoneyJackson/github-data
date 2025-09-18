from datetime import datetime

from ...requests import CollectLabelsRequest, CollectLabelsResponse
from ... import UseCase
from ....github.protocols import RepositoryService
from ....github import converters


class CollectLabelsUseCase(UseCase[CollectLabelsRequest, CollectLabelsResponse]):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: CollectLabelsRequest) -> CollectLabelsResponse:
        raw_labels = self._github_service.get_repository_labels(request.repository_name)
        labels = [converters.convert_to_label(label_dict) for label_dict in raw_labels]

        return CollectLabelsResponse(
            labels=labels,
            collection_timestamp=datetime.now(),
            items_collected=len(labels),
        )
