"""Restore use cases for pull requests entity."""

from __future__ import annotations

from typing import List, Any
from pathlib import Path
from ...shared.jobs.base_job import BaseEntityJob, JobResult
from .models import PullRequest
from .queries import PullRequestQueries
from .save_use_cases import PullRequestConverter


class RestorePullRequestsJob(BaseEntityJob[PullRequest]):
    """Job for restoring repository pull requests."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.queries = PullRequestQueries()
        self.converter = PullRequestConverter()

    def execute(self) -> JobResult[List[PullRequest]]:
        """Execute pull request restoration operation."""
        try:
            # Load PRs from storage
            storage_path = Path("pull_requests.json")
            stored_prs = self.storage_service.load_data(storage_path, PullRequest)

            restored_prs = []

            # Process each stored PR
            for stored_pr in stored_prs:
                # Create new pull request
                self.github_service.create_pull_request(
                    self.repository,
                    stored_pr.title,
                    stored_pr.body or "",
                    stored_pr.head_ref,
                    stored_pr.base_ref,
                )
                restored_prs.append(stored_pr)

            return JobResult(success=True, data=restored_prs)

        except Exception as e:
            return JobResult(success=False, error=str(e))


class RestorePullRequestsUseCase:
    """Use case for restoring repository pull requests."""

    def __init__(self, restore_job: RestorePullRequestsJob) -> None:
        self.restore_job = restore_job

    def execute(self) -> JobResult[List[PullRequest]]:
        """Execute the restore pull requests use case."""
        return self.restore_job.execute()
