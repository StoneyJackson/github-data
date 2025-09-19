"""Restore operation orchestrator using entity-specific use cases."""

from typing import Dict, Any, List

from ..entities.labels import RestoreLabelsUseCase, RestoreLabelsJob
from ..entities.issues import RestoreIssuesUseCase, RestoreIssuesJob
from ..entities.comments import RestoreCommentsUseCase, RestoreCommentsJob
from ..entities.pull_requests import RestorePullRequestsUseCase, RestorePullRequestsJob
from ..github.protocols import RepositoryService
from ..storage.protocols import StorageService


class RestoreOrchestrator:
    """Orchestrates entity-specific restore operations."""

    def __init__(
        self,
        github_service: RepositoryService,
        storage_service: StorageService,
        repository: str,
    ):
        self.github_service = github_service
        self.storage_service = storage_service
        self.repository = repository

    def execute_full_restore(self) -> Dict[str, Any]:
        """Execute complete repository restore operation."""
        results: Dict[str, Any] = {}

        # Create entity-specific use cases
        labels_job = RestoreLabelsJob(
            self.github_service, self.storage_service, self.repository
        )
        labels_use_case = RestoreLabelsUseCase(labels_job)

        issues_job = RestoreIssuesJob(
            self.github_service, self.storage_service, self.repository
        )
        issues_use_case = RestoreIssuesUseCase(issues_job)

        comments_job = RestoreCommentsJob(
            self.github_service, self.storage_service, self.repository
        )
        comments_use_case = RestoreCommentsUseCase(comments_job)

        prs_job = RestorePullRequestsJob(
            self.github_service, self.storage_service, self.repository
        )
        prs_use_case = RestorePullRequestsUseCase(prs_job)

        # Execute in dependency order
        # 1. Restore labels first (no dependencies)
        results["labels"] = labels_use_case.execute()

        # 2. Restore issues (depends on labels)
        results["issues"] = issues_use_case.execute()

        # 3. Restore comments and PRs (depend on issues being created first)
        # Note: Comments need issues to exist, PRs are independent
        results["comments"] = comments_use_case.execute()
        results["pull_requests"] = prs_use_case.execute()

        return results

    def execute_selective_restore(self, entities: List[str]) -> Dict[str, Any]:
        """Execute selective entity restore operation."""
        results = {}

        # Mapping of entity names to use case factories
        entity_factories: Dict[str, Any] = {
            "labels": lambda: RestoreLabelsUseCase(
                RestoreLabelsJob(
                    self.github_service, self.storage_service, self.repository
                )
            ),
            "issues": lambda: RestoreIssuesUseCase(
                RestoreIssuesJob(
                    self.github_service, self.storage_service, self.repository
                )
            ),
            "comments": lambda: RestoreCommentsUseCase(
                RestoreCommentsJob(
                    self.github_service, self.storage_service, self.repository
                )
            ),
            "pull_requests": lambda: RestorePullRequestsUseCase(
                RestorePullRequestsJob(
                    self.github_service, self.storage_service, self.repository
                )
            ),
        }

        # Execute requested entities
        for entity in entities:
            if entity in entity_factories:
                use_case = entity_factories[entity]()
                results[entity] = use_case.execute()

        return results
