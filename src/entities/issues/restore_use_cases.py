"""Restore use cases for issues entity."""

from __future__ import annotations

from typing import List, Tuple, Any
from pathlib import Path
from ...shared.jobs.base_job import BaseEntityJob, JobResult
from .models import Issue
from .queries import IssueQueries
from .save_use_cases import IssueConverter
from ..sub_issues.models import SubIssue


class RestoreIssuesJob(BaseEntityJob[Issue]):
    """Job for restoring repository issues."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.queries = IssueQueries()
        self.converter = IssueConverter()

    def execute(  # type: ignore[override]
        self,
    ) -> JobResult[Tuple[List[Issue], List[SubIssue]]]:
        """Execute issue restoration operation."""
        try:
            # Load issues from storage
            issues_path = Path("issues.json")
            sub_issues_path = Path("sub_issues.json")
            stored_issues = self.storage_service.load_data(issues_path, Issue)
            stored_sub_issues = self.storage_service.load_data(
                sub_issues_path, SubIssue
            )

            # Get existing issues from repository
            existing_raw_issues = self.github_service.get_repository_issues(
                self.repository
            )
            existing_issues = {
                issue_data["number"]: self.converter.from_rest(issue_data)
                for issue_data in existing_raw_issues
            }

            restored_issues = []

            # Process each stored issue
            for stored_issue in stored_issues:
                if stored_issue.number in existing_issues:
                    # Issue already exists - we could update it if needed
                    # For now, just skip existing issues to avoid conflicts
                    continue
                else:
                    # Create new issue
                    new_issue_data = self.github_service.create_issue(
                        self.repository,
                        stored_issue.title,
                        stored_issue.body or "",
                        [label.name for label in stored_issue.labels],
                    )

                    # If issue was closed, close it
                    if stored_issue.state.lower() == "closed":
                        self.github_service.close_issue(
                            self.repository,
                            new_issue_data["number"],
                            stored_issue.state_reason,
                        )

                    restored_issues.append(stored_issue)

            # Note: Sub-issue relationships would need to be restored separately
            # after all issues are created, since they reference issue numbers

            return JobResult(success=True, data=(restored_issues, stored_sub_issues))

        except Exception as e:
            return JobResult(success=False, error=str(e))


class RestoreIssuesUseCase:
    """Use case for restoring repository issues."""

    def __init__(self, restore_job: RestoreIssuesJob) -> None:
        self.restore_job = restore_job

    def execute(self) -> JobResult[Tuple[List[Issue], List[SubIssue]]]:
        """Execute the restore issues use case."""
        return self.restore_job.execute()
