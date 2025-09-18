from typing import List, Any

from ...requests import (
    RestoreRepositoryRequest,
    OperationResult,
    ValidateRestoreDataRequest,
)
from ... import UseCase
from ..validation.validate_restore_data import ValidateRestoreDataUseCase
from ...shared.processing.validate_repository_access import (
    ValidateRepositoryAccessUseCase,
)
from ..jobs import JobOrchestrator
from ..jobs.restore_labels_job import RestoreLabelsJob
from ..jobs.restore_issues_job import RestoreIssuesJob
from ..jobs.restore_comments_job import RestoreCommentsJob
from ..jobs.restore_pull_requests_job import RestorePullRequestsJob
from ..jobs.restore_sub_issues_job import RestoreSubIssuesJob


class RestoreRepositoryUseCase(
    UseCase[RestoreRepositoryRequest, List[OperationResult]]
):
    def __init__(
        self,
        validate_data: ValidateRestoreDataUseCase,
        validate_access: ValidateRepositoryAccessUseCase,
        job_factory: "RestoreJobFactory",
    ):
        self._validate_data = validate_data
        self._validate_access = validate_access
        self._job_factory = job_factory

    def execute(self, request: RestoreRepositoryRequest) -> List[OperationResult]:
        results = []

        # Phase 1: Validation
        validation_result = self._validate_data.execute(
            ValidateRestoreDataRequest(
                input_path=request.input_path,
                include_prs=request.include_prs,
                include_sub_issues=request.include_sub_issues,
            )
        )
        results.append(validation_result)

        if not validation_result.success:
            return results

        from ...requests import ValidateRepositoryAccessRequest

        access_validation_result = self._validate_access.execute(
            ValidateRepositoryAccessRequest(repository_name=request.repository_name)
        )
        results.append(access_validation_result)

        if not access_validation_result.success:
            return results

        # Phase 2: Job-Based Restoration
        restoration_results = self._execute_restoration_jobs(request)
        results.extend(restoration_results)

        return results

    def _execute_restoration_jobs(
        self, request: RestoreRepositoryRequest
    ) -> List[OperationResult]:
        """Execute restoration using job-based parallelism."""
        orchestrator = JobOrchestrator()

        # Determine which jobs to run
        data_types = request.data_types or self._get_default_data_types(request)

        # Add independent jobs
        if "labels" in data_types:
            orchestrator.add_job(
                self._job_factory.create_restore_labels_job(
                    request.repository_name,
                    request.input_path,
                    request.label_conflict_strategy,
                )
            )

        if "pull_requests" in data_types and request.include_prs:
            orchestrator.add_job(
                self._job_factory.create_restore_pull_requests_job(
                    request.repository_name,
                    request.input_path,
                    request.include_original_metadata,
                )
            )

        # Add dependent jobs
        if "issues" in data_types:
            orchestrator.add_job(
                self._job_factory.create_restore_issues_job(
                    request.repository_name,
                    request.input_path,
                    request.include_original_metadata,
                )
            )

        if "comments" in data_types:
            orchestrator.add_job(
                self._job_factory.create_restore_comments_job(
                    request.repository_name,
                    request.input_path,
                    request.include_original_metadata,
                )
            )

        if "sub_issues" in data_types and request.include_sub_issues:
            orchestrator.add_job(
                self._job_factory.create_restore_sub_issues_job(
                    request.repository_name, request.input_path
                )
            )

        # Execute all jobs with dependency resolution
        return orchestrator.execute_jobs()

    def _get_default_data_types(self, request: RestoreRepositoryRequest) -> List[str]:
        """Get default data types based on request flags."""
        types = ["labels", "issues", "comments"]

        if request.include_prs:
            types.extend(["pull_requests", "pr_comments"])

        if request.include_sub_issues:
            types.append("sub_issues")

        return types


class RestoreJobFactory:
    """Factory for creating restoration jobs with proper dependency injection."""

    def __init__(self, **use_cases: Any) -> None:
        # Store all required use cases for job creation
        self._use_cases = use_cases

    def create_restore_labels_job(
        self, repo_name: str, input_path: str, conflict_strategy: str
    ) -> RestoreLabelsJob:
        return RestoreLabelsJob(
            repository_name=repo_name,
            input_path=input_path,
            conflict_strategy=conflict_strategy,
            load_labels=self._use_cases["load_labels"],
            restore_labels=self._use_cases["restore_labels"],
        )

    def create_restore_issues_job(
        self, repo_name: str, input_path: str, include_metadata: bool
    ) -> RestoreIssuesJob:
        return RestoreIssuesJob(
            repository_name=repo_name,
            input_path=input_path,
            include_original_metadata=include_metadata,
            load_issues=self._use_cases["load_issues"],
            restore_issues=self._use_cases["restore_issues"],
        )

    def create_restore_comments_job(
        self, repo_name: str, input_path: str, include_metadata: bool
    ) -> RestoreCommentsJob:
        return RestoreCommentsJob(
            repository_name=repo_name,
            input_path=input_path,
            include_original_metadata=include_metadata,
            load_comments=self._use_cases["load_comments"],
            restore_comments=self._use_cases["restore_comments"],
        )

    def create_restore_pull_requests_job(
        self, repo_name: str, input_path: str, include_metadata: bool
    ) -> RestorePullRequestsJob:
        return RestorePullRequestsJob(
            repository_name=repo_name,
            input_path=input_path,
            include_original_metadata=include_metadata,
            load_pull_requests=self._use_cases["load_pull_requests"],
            restore_pull_requests=self._use_cases["restore_pull_requests"],
        )

    def create_restore_sub_issues_job(
        self, repo_name: str, input_path: str
    ) -> RestoreSubIssuesJob:
        return RestoreSubIssuesJob(
            repository_name=repo_name,
            input_path=input_path,
            load_sub_issues=self._use_cases["load_sub_issues"],
            validate_sub_issues=self._use_cases["validate_sub_issues"],
            detect_circular_deps=self._use_cases["detect_circular_deps"],
            organize_by_depth=self._use_cases["organize_by_depth"],
            restore_sub_issues=self._use_cases["restore_sub_issues"],
        )
