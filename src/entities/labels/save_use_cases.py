"""Save use cases for labels entity."""

from __future__ import annotations

from typing import List, Any
from pathlib import Path
from ...shared.jobs.base_job import BaseEntityJob, JobResult
from ...shared.converters.base_converters import BaseConverter

# Note: avoiding circular import with github.converters
from .models import Label
from .queries import LabelQueries


class LabelConverter(BaseConverter[Label]):
    """Converter for label API responses."""

    def from_graphql(self, data: dict) -> Label:
        """Convert GraphQL label data to Label model."""
        return Label(
            id=data["id"],
            name=data["name"],
            color=data["color"],
            description=data.get("description"),
            url=data["url"],
        )

    def from_rest(self, data: dict) -> Label:
        """Convert REST API label data to Label model."""
        return Label(
            name=data["name"],
            color=data["color"],
            description=data.get("description"),
            url=data["url"],
            id=data["id"],
        )

    def to_api_format(self, label: Label) -> dict:
        """Convert Label model to API request format."""
        return {
            "name": label.name,
            "color": label.color,
            "description": label.description,
        }


class SaveLabelsJob(BaseEntityJob[Label]):
    """Job for saving repository labels."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.queries = LabelQueries()
        self.converter = LabelConverter()

    def execute(self) -> JobResult[List[Label]]:
        """Execute label saving operation."""
        try:
            # Get labels from GitHub service
            raw_labels = self.github_service.get_repository_labels(self.repository)

            # Convert to Label models
            labels = [self.converter.from_rest(label_data) for label_data in raw_labels]

            # Save to storage
            storage_path = Path("labels.json")  # This would be configurable
            self.storage_service.save_data(labels, storage_path)

            return JobResult(success=True, data=labels)

        except Exception as e:
            return JobResult(success=False, error=str(e))


class SaveLabelsUseCase:
    """Use case for saving repository labels."""

    def __init__(self, save_job: SaveLabelsJob) -> None:
        self.save_job = save_job

    def execute(self) -> JobResult[List[Label]]:
        """Execute the save labels use case."""
        return self.save_job.execute()
