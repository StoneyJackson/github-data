from datetime import datetime

from ...requests import CollectCommentsRequest, CollectCommentsResponse
from ... import UseCase
from ....github.protocols import RepositoryService
from ....github import converters


class CollectCommentsUseCase(UseCase[CollectCommentsRequest, CollectCommentsResponse]):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: CollectCommentsRequest) -> CollectCommentsResponse:
        raw_comments = self._github_service.get_all_issue_comments(
            request.repository_name
        )
        comments = [
            converters.convert_to_comment(comment_dict) for comment_dict in raw_comments
        ]

        return CollectCommentsResponse(
            comments=comments,
            collection_timestamp=datetime.now(),
            items_collected=len(comments),
        )
