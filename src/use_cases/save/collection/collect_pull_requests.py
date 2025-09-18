from datetime import datetime

from ...requests import CollectPullRequestsRequest, CollectPullRequestsResponse
from ... import UseCase
from ....github.protocols import RepositoryService
from ....github import converters


class CollectPullRequestsUseCase(
    UseCase[CollectPullRequestsRequest, CollectPullRequestsResponse]
):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(
        self, request: CollectPullRequestsRequest
    ) -> CollectPullRequestsResponse:
        raw_prs = self._github_service.get_repository_pull_requests(
            request.repository_name
        )
        pull_requests = [
            converters.convert_to_pull_request(pr_dict) for pr_dict in raw_prs
        ]

        return CollectPullRequestsResponse(
            pull_requests=pull_requests,
            collection_timestamp=datetime.now(),
            items_collected=len(pull_requests),
        )
