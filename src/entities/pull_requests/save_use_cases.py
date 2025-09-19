"""Save use cases for pull requests entity."""

from __future__ import annotations

from typing import List, Any
from pathlib import Path
from datetime import datetime
from ...shared.jobs.base_job import BaseEntityJob, JobResult
from ...shared.converters.base_converters import BaseConverter

# Note: avoiding circular import with github.converters
from .models import PullRequest
from .queries import PullRequestQueries


class PullRequestConverter(BaseConverter[PullRequest]):
    """Converter for pull request API responses."""

    def from_graphql(self, data: dict) -> PullRequest:
        """Convert GraphQL PR data to PullRequest model."""
        # For now, use the same logic as REST API
        # TODO: Implement GraphQL-specific field mapping
        return self.from_rest(data)

    def from_rest(self, data: dict) -> PullRequest:
        """Convert REST API PR data to PullRequest model."""
        from ..users.models import GitHubUser
        from ..labels.models import Label

        user = GitHubUser(
            login=data["user"]["login"],
            id=data["user"]["id"],
            avatar_url=data["user"]["avatar_url"],
            html_url=data["user"]["html_url"],
        )

        assignees = [
            GitHubUser(
                login=assignee["login"],
                id=assignee["id"],
                avatar_url=assignee["avatar_url"],
                html_url=assignee["html_url"],
            )
            for assignee in data.get("assignees", [])
        ]

        labels = [
            Label(
                name=label["name"],
                color=label["color"],
                description=label.get("description"),
                url=label["url"],
                id=label["id"],
            )
            for label in data.get("labels", [])
        ]

        return PullRequest(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            body=data.get("body"),
            state=data["state"],
            user=user,
            assignees=assignees,
            labels=labels,
            created_at=self._parse_datetime(data["created_at"]) or datetime.now(),
            updated_at=self._parse_datetime(data["updated_at"]) or datetime.now(),
            closed_at=self._parse_datetime(data.get("closed_at")),
            merged_at=self._parse_datetime(data.get("merged_at")),
            merge_commit_sha=data.get("merge_commit_sha"),
            base_ref=data.get("base_ref", ""),
            head_ref=data.get("head_ref", ""),
            html_url=data["html_url"],
            comments=data.get("comments", 0),
        )

    def to_api_format(self, pr: PullRequest) -> dict:
        """Convert PullRequest model to API request format."""
        return {
            "title": pr.title,
            "body": pr.body,
            "head": pr.head_ref,
            "base": pr.base_ref,
            "state": pr.state.lower(),
        }


class SavePullRequestsJob(BaseEntityJob[PullRequest]):
    """Job for saving repository pull requests."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.queries = PullRequestQueries()
        self.converter = PullRequestConverter()

    def execute(self) -> JobResult[List[PullRequest]]:
        """Execute pull request saving operation."""
        try:
            # Get PRs from GitHub service
            raw_prs = self.github_service.get_repository_pull_requests(self.repository)

            # Convert to PullRequest models
            pull_requests = [self.converter.from_rest(pr_data) for pr_data in raw_prs]

            # Save to storage
            storage_path = Path("pull_requests.json")
            self.storage_service.save_data(pull_requests, storage_path)

            return JobResult(success=True, data=pull_requests)

        except Exception as e:
            return JobResult(success=False, error=str(e))


class SavePullRequestsUseCase:
    """Use case for saving repository pull requests."""

    def __init__(self, save_job: SavePullRequestsJob) -> None:
        self.save_job = save_job

    def execute(self) -> JobResult[List[PullRequest]]:
        """Execute the save pull requests use case."""
        return self.save_job.execute()
