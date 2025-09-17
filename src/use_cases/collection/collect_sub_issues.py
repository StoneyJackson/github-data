from datetime import datetime

from ..requests import CollectSubIssuesRequest, CollectSubIssuesResponse
from .. import UseCase
from ...github.protocols import RepositoryService
from ...github import converters


class CollectSubIssuesUseCase(
    UseCase[CollectSubIssuesRequest, CollectSubIssuesResponse]
):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: CollectSubIssuesRequest) -> CollectSubIssuesResponse:
        raw_sub_issues = self._github_service.get_repository_sub_issues(
            request.repository_name
        )
        sub_issues = [
            converters.convert_to_sub_issue(sub_issue_dict)
            for sub_issue_dict in raw_sub_issues
        ]

        return CollectSubIssuesResponse(
            sub_issues=sub_issues,
            collection_timestamp=datetime.now(),
            items_collected=len(sub_issues),
        )
