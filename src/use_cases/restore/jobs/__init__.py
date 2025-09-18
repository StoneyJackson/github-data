from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ...requests import OperationResult


class RestoreJob(ABC):
    def __init__(self, job_id: str, dependencies: Optional[List[str]] = None):
        self.job_id = job_id
        self.dependencies = dependencies or []
        self.completed = False
        self.result: Optional[OperationResult] = None

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Execute the job with given context (shared data from dependencies)."""
        pass

    @property
    def can_start(self) -> bool:
        """Check if all dependencies are satisfied."""
        return not self.dependencies  # Override in subclasses for dependency checking


class JobOrchestrator:
    def __init__(self) -> None:
        self.jobs: Dict[str, RestoreJob] = {}
        self.shared_context: Dict[str, Any] = {}

    def add_job(self, job: RestoreJob) -> None:
        self.jobs[job.job_id] = job

    def execute_jobs(self) -> List[OperationResult]:
        """Execute jobs in dependency order with parallelization."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading

        results = []
        completed_jobs = set()
        lock = threading.Lock()

        def can_execute_job(job: RestoreJob) -> bool:
            with lock:
                return all(dep in completed_jobs for dep in job.dependencies)

        def execute_job(job: RestoreJob) -> OperationResult:
            result = job.execute(self.shared_context)
            with lock:
                job.completed = True
                job.result = result
                completed_jobs.add(job.job_id)
                if result.success:
                    self.shared_context[job.job_id] = result
                    # Note: Job may have stored additional data in shared_context
                    # during execution
                    # This data is preserved alongside the job result
            return result

        # Continue until all jobs are completed
        with ThreadPoolExecutor(max_workers=4) as executor:
            while len(completed_jobs) < len(self.jobs):
                # Find jobs that can be executed
                ready_jobs = [
                    job
                    for job in self.jobs.values()
                    if not job.completed and can_execute_job(job)
                ]

                if not ready_jobs:
                    # Check for circular dependencies or other issues
                    remaining = [
                        j.job_id for j in self.jobs.values() if not j.completed
                    ]
                    raise RuntimeError(f"No jobs can proceed. Remaining: {remaining}")

                # Submit ready jobs for execution
                future_to_job = {
                    executor.submit(execute_job, job): job for job in ready_jobs
                }

                # Wait for all submitted jobs to complete
                for future in as_completed(future_to_job):
                    result = future.result()
                    results.append(result)

        return results
