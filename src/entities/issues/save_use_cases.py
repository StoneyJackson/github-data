"""Save use cases for issues entity."""

from __future__ import annotations

import re
from typing import List, Tuple, Any
from pathlib import Path
from datetime import datetime
from ...shared.jobs.base_job import BaseEntityJob, JobResult
from ...shared.converters.base_converters import BaseConverter

# Note: avoiding circular import with github.converters
from ..users.models import GitHubUser
from ..labels.models import Label
from ..sub_issues.models import SubIssue
from .models import Issue
from .queries import IssueQueries


class IssueConverter(BaseConverter[Issue]):
    """Converter for issue API responses."""

    def from_graphql(self, data: dict) -> Issue:
        """Convert GraphQL issue data to Issue model."""
        # Convert author
        author_data = data.get("author", {})
        author = GitHubUser(
            login=author_data.get("login", ""),
            id=author_data.get("id", ""),
            avatar_url=author_data.get("avatarUrl", ""),
            html_url=author_data.get("url", ""),
        )

        # Convert assignees
        assignees = []
        for assignee_data in data.get("assignees", {}).get("nodes", []):
            assignees.append(
                GitHubUser(
                    login=assignee_data.get("login", ""),
                    id=assignee_data.get("id", ""),
                    avatar_url=assignee_data.get("avatarUrl", ""),
                    html_url=assignee_data.get("url", ""),
                )
            )

        # Convert labels
        labels = []
        for label_data in data.get("labels", {}).get("nodes", []):
            labels.append(
                Label(
                    id=label_data.get("id", ""),
                    name=label_data.get("name", ""),
                    color=label_data.get("color", ""),
                    description=label_data.get("description"),
                    url=label_data.get("url", ""),
                )
            )

        # Convert closed_by
        closed_by = None
        if data.get("closedBy"):
            closed_by_data = data["closedBy"]
            closed_by = GitHubUser(
                login=closed_by_data.get("login", ""),
                id=closed_by_data.get("id", ""),
                avatar_url=closed_by_data.get("avatarUrl", ""),
                html_url=closed_by_data.get("url", ""),
            )

        return Issue(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            body=data.get("body"),
            state=data["state"],
            user=author,
            assignees=assignees,
            labels=labels,
            created_at=self._parse_datetime(data["createdAt"]) or datetime.now(),
            updated_at=self._parse_datetime(data["updatedAt"]) or datetime.now(),
            closed_at=self._parse_datetime(data.get("closedAt")),
            closed_by=closed_by,
            state_reason=data.get("stateReason"),
            html_url=data["url"],
            comments=data.get("comments", {}).get("totalCount", 0),
        )

    def from_rest(self, data: dict) -> Issue:
        """Convert REST API issue data to Issue model."""
        # Convert user data
        user = GitHubUser(
            login=data["user"]["login"],
            id=data["user"]["id"],
            avatar_url=data["user"]["avatar_url"],
            html_url=data["user"]["html_url"],
        )

        # Convert assignees
        assignees = [
            GitHubUser(
                login=assignee["login"],
                id=assignee["id"],
                avatar_url=assignee["avatar_url"],
                html_url=assignee["html_url"],
            )
            for assignee in data.get("assignees", [])
        ]

        # Convert labels
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

        # Convert closed_by if present
        closed_by = None
        if data.get("closed_by"):
            closed_by = GitHubUser(
                login=data["closed_by"]["login"],
                id=data["closed_by"]["id"],
                avatar_url=data["closed_by"]["avatar_url"],
                html_url=data["closed_by"]["html_url"],
            )

        return Issue(
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
            closed_by=closed_by,
            state_reason=data.get("state_reason"),
            html_url=data["html_url"],
            comments=data.get("comments", 0),
        )

    def to_api_format(self, issue: Issue) -> dict:
        """Convert Issue model to API request format."""
        result = {
            "title": issue.title,
            "body": issue.body,
            "state": issue.state.lower(),
        }

        if issue.assignees:
            result["assignees"] = [
                user.login for user in issue.assignees
            ]  # type: ignore[assignment]

        if issue.labels:
            result["labels"] = [
                label.name for label in issue.labels
            ]  # type: ignore[assignment]

        return result


class SubIssueExtractor:
    """Utility for extracting sub-issue relationships from issue bodies."""

    SUB_ISSUE_PATTERNS = [
        r"- \[ \] #(\d+)",  # GitHub task list format
        r"Sub-issues?:\s*#(\d+)",  # Explicit sub-issue declaration
        r"Related:\s*#(\d+)",  # Related issues
        r"Depends on:\s*#(\d+)",  # Dependency declaration
    ]

    def extract_sub_issues(self, issue: Issue) -> List[SubIssue]:
        """Extract sub-issue relationships from issue body."""
        if not issue.body:
            return []

        sub_issues = []
        position = 0

        for pattern in self.SUB_ISSUE_PATTERNS:
            matches = re.finditer(pattern, issue.body, re.IGNORECASE)
            for match in matches:
                sub_issue_number = int(match.group(1))
                sub_issues.append(
                    SubIssue(
                        sub_issue_id=f"sub_{sub_issue_number}",
                        sub_issue_number=sub_issue_number,
                        parent_issue_id=issue.id,
                        parent_issue_number=issue.number,
                        position=position,
                    )
                )
                position += 1

        return sub_issues


class SaveIssuesJob(BaseEntityJob[Issue]):
    """Job for saving repository issues."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.queries = IssueQueries()
        self.converter = IssueConverter()
        self.sub_issue_extractor = SubIssueExtractor()

    def execute(  # type: ignore[override]
        self,
    ) -> JobResult[Tuple[List[Issue], List[SubIssue]]]:
        """Execute issue saving operation."""
        try:
            # Get issues from GitHub service
            raw_issues = self.github_service.get_repository_issues(self.repository)

            # Convert to Issue models
            issues = [self.converter.from_rest(issue_data) for issue_data in raw_issues]

            # Extract sub-issue relationships
            all_sub_issues = []
            for issue in issues:
                sub_issues = self.sub_issue_extractor.extract_sub_issues(issue)
                all_sub_issues.extend(sub_issues)

            # Save to storage
            issues_path = Path("issues.json")
            sub_issues_path = Path("sub_issues.json")
            self.storage_service.save_data(issues, issues_path)
            self.storage_service.save_data(all_sub_issues, sub_issues_path)

            return JobResult(success=True, data=(issues, all_sub_issues))

        except Exception as e:
            return JobResult(success=False, error=str(e))


class SaveIssuesUseCase:
    """Use case for saving repository issues."""

    def __init__(self, save_job: SaveIssuesJob) -> None:
        self.save_job = save_job

    def execute(self) -> JobResult[Tuple[List[Issue], List[SubIssue]]]:
        """Execute the save issues use case."""
        return self.save_job.execute()
