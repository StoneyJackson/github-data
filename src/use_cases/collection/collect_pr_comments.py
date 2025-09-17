from datetime import datetime

from ..requests import CollectPRCommentsRequest, CollectPRCommentsResponse
from .. import UseCase
from ...github.protocols import RepositoryService
from ...github import converters


class CollectPRCommentsUseCase(
    UseCase[CollectPRCommentsRequest, CollectPRCommentsResponse]
):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: CollectPRCommentsRequest) -> CollectPRCommentsResponse:
        raw_comments = self._github_service.get_all_pull_request_comments(
            request.repository_name
        )
        pr_comments = [
            converters.convert_to_pr_comment(comment_dict)
            for comment_dict in raw_comments
        ]

        return CollectPRCommentsResponse(
            pr_comments=pr_comments,
            collection_timestamp=datetime.now(),
            items_collected=len(pr_comments),
        )
