"""Restore use cases for comments entity."""

from __future__ import annotations

from typing import List, Any
from pathlib import Path
from ...shared.jobs.base_job import BaseEntityJob, JobResult
from .models import Comment
from .queries import CommentQueries
from .save_use_cases import CommentConverter


class RestoreCommentsJob(BaseEntityJob[Comment]):
    """Job for restoring repository comments."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.queries = CommentQueries()
        self.converter = CommentConverter()

    def execute(self) -> JobResult[List[Comment]]:
        """Execute comment restoration operation."""
        try:
            # Load comments from storage
            storage_path = Path("comments.json")
            stored_comments = self.storage_service.load_data(storage_path, Comment)

            restored_comments = []

            # Process each stored comment
            for stored_comment in stored_comments:
                # Create new comment on the appropriate issue
                self.github_service.create_issue_comment(
                    self.repository, stored_comment.issue_number, stored_comment.body
                )
                restored_comments.append(stored_comment)

            return JobResult(success=True, data=restored_comments)

        except Exception as e:
            return JobResult(success=False, error=str(e))


class RestoreCommentsUseCase:
    """Use case for restoring repository comments."""

    def __init__(self, restore_job: RestoreCommentsJob) -> None:
        self.restore_job = restore_job

    def execute(self) -> JobResult[List[Comment]]:
        """Execute the restore comments use case."""
        return self.restore_job.execute()
