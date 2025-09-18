from typing import List, Optional, Set
from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod

from ..requests import (
    SaveRepositoryRequest,
    OperationResult,
    CollectLabelsRequest,
    CollectIssuesRequest,
    CollectCommentsRequest,
    CollectPullRequestsRequest,
    CollectPRCommentsRequest,
    CollectSubIssuesRequest,
    SaveLabelsRequest,
    SaveIssuesRequest,
    SaveCommentsRequest,
    SavePullRequestsRequest,
    SavePRCommentsRequest,
    SaveSubIssuesRequest,
    ValidateRepositoryAccessRequest,
    AssociateSubIssuesRequest,
)
from ...models import Issue
from .. import UseCase
from ..collection.collect_labels import CollectLabelsUseCase
from ..collection.collect_issues import CollectIssuesUseCase
from ..collection.collect_comments import CollectCommentsUseCase
from ..collection.collect_pull_requests import CollectPullRequestsUseCase
from ..collection.collect_pr_comments import CollectPRCommentsUseCase
from ..collection.collect_sub_issues import CollectSubIssuesUseCase
from ..persistence.save_labels import SaveLabelsUseCase
from ..persistence.save_issues import SaveIssuesUseCase
from ..persistence.save_comments import SaveCommentsUseCase
from ..persistence.save_pull_requests import SavePullRequestsUseCase
from ..persistence.save_pr_comments import SavePRCommentsUseCase
from ..persistence.save_sub_issues import SaveSubIssuesUseCase
from ..processing.validate_repository_access import ValidateRepositoryAccessUseCase
from ..processing.associate_sub_issues import AssociateSubIssuesUseCase


class DataTypeJob(ABC):
    """Abstract base class for data type jobs that handle a complete workflow."""

    def __init__(self, repo_name: str, output_path: str):
        self.repo_name = repo_name
        self.output_path = output_path

    @abstractmethod
    def execute(self) -> OperationResult:
        """Execute the complete job workflow for this data type."""
        pass


class JobDependency:
    """Wrapper for jobs with their dependencies."""

    def __init__(
        self, job: DataTypeJob, depends_on: Optional[List[DataTypeJob]] = None
    ):
        self.job = job
        self.depends_on = depends_on or []


class JobOrchestrator:
    """Orchestrates execution of jobs with dependency resolution."""

    def execute_jobs(
        self, job_dependencies: List[JobDependency]
    ) -> List[OperationResult]:
        """Execute jobs in parallel while respecting dependencies."""
        results = []
        completed_jobs: Set[DataTypeJob] = set()

        with ThreadPoolExecutor(max_workers=6) as executor:
            # Track running futures
            running_futures = {}

            while len(completed_jobs) < len(job_dependencies):
                # Find jobs that can be started (all dependencies completed)
                ready_jobs = []
                for dep in job_dependencies:
                    if dep.job not in completed_jobs and dep.job not in running_futures:
                        if all(dep_job in completed_jobs for dep_job in dep.depends_on):
                            ready_jobs.append(dep.job)

                # Start ready jobs
                for job in ready_jobs:
                    future = executor.submit(job.execute)
                    running_futures[job] = future

                # If no jobs are running and no jobs are ready, we have a deadlock
                if not running_futures and not ready_jobs:
                    remaining_jobs = [
                        dep.job
                        for dep in job_dependencies
                        if dep.job not in completed_jobs
                    ]
                    for job in remaining_jobs:
                        error_result = OperationResult(
                            success=False,
                            data_type=job.__class__.__name__.replace("Job", "").lower(),
                            error_message=(
                                "Job could not be executed due to "
                                "unresolved dependencies"
                            ),
                        )
                        results.append(error_result)
                    break

                # Wait for at least one job to complete
                if running_futures:
                    from concurrent.futures import wait, FIRST_COMPLETED

                    done, pending = wait(
                        running_futures.values(), return_when=FIRST_COMPLETED
                    )

                # Check for completed jobs
                completed_futures = []
                for job, future in running_futures.items():
                    if future.done():
                        try:
                            result = future.result()
                            results.append(result)
                        except Exception as e:
                            # Create error result for failed job
                            error_result = OperationResult(
                                success=False,
                                data_type=job.__class__.__name__.replace(
                                    "Job", ""
                                ).lower(),
                                error_message=f"Job execution failed: {str(e)}",
                            )
                            results.append(error_result)

                        completed_jobs.add(job)
                        completed_futures.append(job)

                # Remove completed futures
                for job in completed_futures:
                    del running_futures[job]

        return results


class LabelJob(DataTypeJob):
    """Job for collecting and saving labels."""

    def __init__(
        self,
        repo_name: str,
        output_path: str,
        collect_labels: "CollectLabelsUseCase",
        save_labels: "SaveLabelsUseCase",
    ):
        super().__init__(repo_name, output_path)
        self._collect_labels = collect_labels
        self._save_labels = save_labels

    def execute(self) -> OperationResult:
        try:
            # Collect labels
            collect_result = self._collect_labels.execute(
                CollectLabelsRequest(self.repo_name)
            )

            # Save labels
            save_result = self._save_labels.execute(
                SaveLabelsRequest(collect_result.labels, self.output_path)
            )

            return save_result
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="labels",
                error_message=f"Label job failed: {str(e)}",
            )


class IssueJob(DataTypeJob):
    """Job for collecting and saving issues."""

    def __init__(
        self,
        repo_name: str,
        output_path: str,
        collect_issues: "CollectIssuesUseCase",
        save_issues: "SaveIssuesUseCase",
    ):
        super().__init__(repo_name, output_path)
        self._collect_issues = collect_issues
        self._save_issues = save_issues
        self.collected_issues: Optional[List[Issue]] = (
            None  # Store for SubIssueJob dependency
        )

    def execute(self) -> OperationResult:
        try:
            # Collect issues
            collect_result = self._collect_issues.execute(
                CollectIssuesRequest(self.repo_name)
            )
            self.collected_issues = collect_result.issues

            # Save issues
            save_result = self._save_issues.execute(
                SaveIssuesRequest(collect_result.issues, self.output_path)
            )

            return save_result
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="issues",
                error_message=f"Issue job failed: {str(e)}",
            )


class CommentJob(DataTypeJob):
    """Job for collecting and saving comments."""

    def __init__(
        self,
        repo_name: str,
        output_path: str,
        collect_comments: "CollectCommentsUseCase",
        save_comments: "SaveCommentsUseCase",
    ):
        super().__init__(repo_name, output_path)
        self._collect_comments = collect_comments
        self._save_comments = save_comments

    def execute(self) -> OperationResult:
        try:
            # Collect comments
            collect_result = self._collect_comments.execute(
                CollectCommentsRequest(self.repo_name, [])
            )

            # Save comments
            save_result = self._save_comments.execute(
                SaveCommentsRequest(collect_result.comments, self.output_path)
            )

            return save_result
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="comments",
                error_message=f"Comment job failed: {str(e)}",
            )


class PullRequestJob(DataTypeJob):
    """Job for collecting and saving pull requests."""

    def __init__(
        self,
        repo_name: str,
        output_path: str,
        collect_pull_requests: "CollectPullRequestsUseCase",
        save_pull_requests: "SavePullRequestsUseCase",
    ):
        super().__init__(repo_name, output_path)
        self._collect_pull_requests = collect_pull_requests
        self._save_pull_requests = save_pull_requests

    def execute(self) -> OperationResult:
        try:
            # Collect pull requests
            collect_result = self._collect_pull_requests.execute(
                CollectPullRequestsRequest(self.repo_name)
            )

            # Save pull requests
            save_result = self._save_pull_requests.execute(
                SavePullRequestsRequest(collect_result.pull_requests, self.output_path)
            )

            return save_result
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="pull_requests",
                error_message=f"Pull request job failed: {str(e)}",
            )


class PRCommentJob(DataTypeJob):
    """Job for collecting and saving PR comments."""

    def __init__(
        self,
        repo_name: str,
        output_path: str,
        collect_pr_comments: "CollectPRCommentsUseCase",
        save_pr_comments: "SavePRCommentsUseCase",
    ):
        super().__init__(repo_name, output_path)
        self._collect_pr_comments = collect_pr_comments
        self._save_pr_comments = save_pr_comments

    def execute(self) -> OperationResult:
        try:
            # Collect PR comments
            collect_result = self._collect_pr_comments.execute(
                CollectPRCommentsRequest(self.repo_name, [])
            )

            # Save PR comments
            save_result = self._save_pr_comments.execute(
                SavePRCommentsRequest(collect_result.pr_comments, self.output_path)
            )

            return save_result
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="pr_comments",
                error_message=f"PR comment job failed: {str(e)}",
            )


class SubIssueJob(DataTypeJob):
    """Job for collecting, associating, and saving sub-issues."""

    def __init__(
        self,
        repo_name: str,
        output_path: str,
        collect_sub_issues: "CollectSubIssuesUseCase",
        associate_sub_issues: "AssociateSubIssuesUseCase",
        save_sub_issues: "SaveSubIssuesUseCase",
        save_issues: "SaveIssuesUseCase",
        issue_job: IssueJob,
    ):
        super().__init__(repo_name, output_path)
        self._collect_sub_issues = collect_sub_issues
        self._associate_sub_issues = associate_sub_issues
        self._save_sub_issues = save_sub_issues
        self._save_issues = save_issues
        self._issue_job = issue_job

    def execute(self) -> OperationResult:
        try:
            # Collect sub-issues
            collect_result = self._collect_sub_issues.execute(
                CollectSubIssuesRequest(self.repo_name, [])
            )

            # Associate with issues if issue job has completed
            if self._issue_job and self._issue_job.collected_issues is not None:
                association_response = self._associate_sub_issues.execute(
                    AssociateSubIssuesRequest(
                        issues=self._issue_job.collected_issues,
                        sub_issues=collect_result.sub_issues,
                    )
                )
                # Update the issue job's collected issues with associations
                self._issue_job.collected_issues = association_response.updated_issues

                # Also save the updated issues with sub-issue associations
                self._save_issues.execute(
                    SaveIssuesRequest(
                        association_response.updated_issues, self.output_path
                    )
                )

            # Save sub-issues
            save_result = self._save_sub_issues.execute(
                SaveSubIssuesRequest(collect_result.sub_issues, self.output_path)
            )

            return save_result
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="sub_issues",
                error_message=f"Sub-issue job failed: {str(e)}",
            )


class SaveRepositoryUseCase(UseCase[SaveRepositoryRequest, List[OperationResult]]):
    def __init__(
        self,
        validate_access: ValidateRepositoryAccessUseCase,
        collect_labels: CollectLabelsUseCase,
        collect_issues: CollectIssuesUseCase,
        collect_comments: CollectCommentsUseCase,
        collect_pull_requests: CollectPullRequestsUseCase,
        collect_pr_comments: CollectPRCommentsUseCase,
        collect_sub_issues: CollectSubIssuesUseCase,
        associate_sub_issues: AssociateSubIssuesUseCase,
        save_labels: SaveLabelsUseCase,
        save_issues: SaveIssuesUseCase,
        save_comments: SaveCommentsUseCase,
        save_pull_requests: SavePullRequestsUseCase,
        save_pr_comments: SavePRCommentsUseCase,
        save_sub_issues: SaveSubIssuesUseCase,
    ):
        self._validate_access = validate_access
        self._collect_labels = collect_labels
        self._collect_issues = collect_issues
        self._collect_comments = collect_comments
        self._collect_pull_requests = collect_pull_requests
        self._collect_pr_comments = collect_pr_comments
        self._collect_sub_issues = collect_sub_issues
        self._associate_sub_issues = associate_sub_issues
        self._save_labels = save_labels
        self._save_issues = save_issues
        self._save_comments = save_comments
        self._save_pull_requests = save_pull_requests
        self._save_pr_comments = save_pr_comments
        self._save_sub_issues = save_sub_issues

    def execute(self, request: SaveRepositoryRequest) -> List[OperationResult]:
        results = []

        # Step 1: Validate repository access
        validation_result = self._validate_access.execute(
            ValidateRepositoryAccessRequest(request.repository_name)
        )
        results.append(validation_result)

        if not validation_result.success:
            return results

        # Step 2: Determine which data types to process
        data_types = request.data_types or [
            "labels",
            "issues",
            "comments",
            "pull_requests",
            "pr_comments",
            "sub_issues",
        ]

        # Step 3: Create jobs and dependencies
        job_dependencies = self._create_jobs(
            request.repository_name, request.output_path, data_types
        )

        # Step 4: Execute jobs using orchestrator
        orchestrator = JobOrchestrator()
        job_results = orchestrator.execute_jobs(job_dependencies)
        results.extend(job_results)

        return results

    def _create_jobs(
        self, repo_name: str, output_path: str, data_types: List[str]
    ) -> List[JobDependency]:
        """Create job dependencies based on requested data types."""
        job_dependencies = []
        issue_job = None

        # Create jobs for each data type
        if "labels" in data_types:
            label_job = LabelJob(
                repo_name, output_path, self._collect_labels, self._save_labels
            )
            job_dependencies.append(JobDependency(label_job))

        if "issues" in data_types:
            issue_job = IssueJob(
                repo_name, output_path, self._collect_issues, self._save_issues
            )
            job_dependencies.append(JobDependency(issue_job))

        if "comments" in data_types:
            comment_job = CommentJob(
                repo_name, output_path, self._collect_comments, self._save_comments
            )
            job_dependencies.append(JobDependency(comment_job))

        if "pull_requests" in data_types:
            pr_job = PullRequestJob(
                repo_name,
                output_path,
                self._collect_pull_requests,
                self._save_pull_requests,
            )
            job_dependencies.append(JobDependency(pr_job))

        if "pr_comments" in data_types:
            pr_comment_job = PRCommentJob(
                repo_name,
                output_path,
                self._collect_pr_comments,
                self._save_pr_comments,
            )
            job_dependencies.append(JobDependency(pr_comment_job))

        if "sub_issues" in data_types:
            # SubIssueJob depends on IssueJob if both are present
            depends_on: List[DataTypeJob] = (
                [issue_job] if issue_job and "issues" in data_types else []
            )
            # SubIssueJob requires IssueJob, so we create it with issue_job or None
            # For now, we'll use a conditional to ensure issue_job is not None
            if issue_job is not None:
                sub_issue_job = SubIssueJob(
                    repo_name,
                    output_path,
                    self._collect_sub_issues,
                    self._associate_sub_issues,
                    self._save_sub_issues,
                    self._save_issues,
                    issue_job,
                )
                job_dependencies.append(JobDependency(sub_issue_job, depends_on))

        return job_dependencies
