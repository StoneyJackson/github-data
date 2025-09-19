"""Restore use cases for labels entity."""

from __future__ import annotations

from typing import List, Any
from pathlib import Path
from ...shared.jobs.base_job import BaseEntityJob, JobResult
from .models import Label
from .queries import LabelQueries
from .save_use_cases import LabelConverter


class RestoreLabelsJob(BaseEntityJob[Label]):
    """Job for restoring repository labels."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.queries = LabelQueries()
        self.converter = LabelConverter()

    def execute(self) -> JobResult[List[Label]]:
        """Execute label restoration operation."""
        try:
            # Load labels from storage
            storage_path = Path("labels.json")  # This would be configurable
            stored_labels = self.storage_service.load_data(storage_path, Label)

            # Get existing labels from repository
            existing_raw_labels = self.github_service.get_repository_labels(
                self.repository
            )
            existing_labels = {
                label_data["name"]: self.converter.from_rest(label_data)
                for label_data in existing_raw_labels
            }

            restored_labels = []

            # Process each stored label
            for stored_label in stored_labels:
                if stored_label.name in existing_labels:
                    # Update existing label if different
                    existing = existing_labels[stored_label.name]
                    if (
                        existing.color != stored_label.color
                        or existing.description != stored_label.description
                    ):

                        self.github_service.update_label(
                            self.repository,
                            stored_label.name,
                            stored_label.name,
                            stored_label.color,
                            stored_label.description or "",
                        )
                        restored_labels.append(stored_label)
                else:
                    # Create new label
                    self.github_service.create_label(
                        self.repository,
                        stored_label.name,
                        stored_label.color,
                        stored_label.description or "",
                    )
                    restored_labels.append(stored_label)

            return JobResult(success=True, data=restored_labels)

        except Exception as e:
            return JobResult(success=False, error=str(e))


class RestoreLabelsUseCase:
    """Use case for restoring repository labels."""

    def __init__(self, restore_job: RestoreLabelsJob) -> None:
        self.restore_job = restore_job

    def execute(self) -> JobResult[List[Label]]:
        """Execute the restore labels use case."""
        return self.restore_job.execute()
