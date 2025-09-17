from datetime import datetime

from ..requests import CollectIssuesRequest, CollectIssuesResponse
from .. import UseCase
from ...github.protocols import RepositoryService
from ...github import converters


class CollectIssuesUseCase(UseCase[CollectIssuesRequest, CollectIssuesResponse]):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: CollectIssuesRequest) -> CollectIssuesResponse:
        raw_issues = self._github_service.get_repository_issues(request.repository_name)
        issues = [converters.convert_to_issue(issue_dict) for issue_dict in raw_issues]

        return CollectIssuesResponse(
            issues=issues,
            collection_timestamp=datetime.now(),
            items_collected=len(issues),
        )
