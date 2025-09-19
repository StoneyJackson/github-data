"""Save use cases for comments entity."""

from __future__ import annotations

from typing import List, Any
from pathlib import Path
from datetime import datetime
from ...shared.jobs.base_job import BaseEntityJob, JobResult
from ...shared.converters.base_converters import BaseConverter

# Note: avoiding circular import with github.converters
from .models import Comment
from .queries import CommentQueries


class CommentConverter(BaseConverter[Comment]):
    """Converter for comment API responses."""

    def from_graphql(self, data: dict) -> Comment:
        """Convert GraphQL comment data to Comment model."""
        # For now, use the same logic as REST API
        # TODO: Implement GraphQL-specific field mapping
        return self.from_rest(data)

    def from_rest(self, data: dict) -> Comment:
        """Convert REST API comment data to Comment model."""
        from ..users.models import GitHubUser

        user = GitHubUser(
            login=data["user"]["login"],
            id=data["user"]["id"],
            avatar_url=data["user"]["avatar_url"],
            html_url=data["user"]["html_url"],
        )

        return Comment(
            id=data["id"],
            body=data["body"],
            user=user,
            created_at=self._parse_datetime(data["created_at"]) or datetime.now(),
            updated_at=self._parse_datetime(data["updated_at"]) or datetime.now(),
            html_url=data["html_url"],
            issue_url=data["issue_url"],
        )

    def to_api_format(self, comment: Comment) -> dict:
        """Convert Comment model to API request format."""
        return {"body": comment.body}


class SaveCommentsJob(BaseEntityJob[Comment]):
    """Job for saving repository comments."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.queries = CommentQueries()
        self.converter = CommentConverter()

    def execute(self) -> JobResult[List[Comment]]:
        """Execute comment saving operation."""
        try:
            # Get comments from GitHub service
            raw_comments = self.github_service.get_all_issue_comments(self.repository)

            # Convert to Comment models
            comments = [
                self.converter.from_rest(comment_data) for comment_data in raw_comments
            ]

            # Save to storage
            storage_path = Path("comments.json")
            self.storage_service.save_data(comments, storage_path)

            return JobResult(success=True, data=comments)

        except Exception as e:
            return JobResult(success=False, error=str(e))


class SaveCommentsUseCase:
    """Use case for saving repository comments."""

    def __init__(self, save_job: SaveCommentsJob) -> None:
        self.save_job = save_job

    def execute(self) -> JobResult[List[Comment]]:
        """Execute the save comments use case."""
        return self.save_job.execute()
