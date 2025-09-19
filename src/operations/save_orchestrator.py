"""Save operation orchestrator using entity-specific use cases."""

from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

from ..entities.labels import SaveLabelsUseCase, SaveLabelsJob
from ..entities.issues import SaveIssuesUseCase, SaveIssuesJob
from ..entities.comments import SaveCommentsUseCase, SaveCommentsJob
from ..entities.pull_requests import SavePullRequestsUseCase, SavePullRequestsJob
from ..github.protocols import RepositoryService
from ..storage.protocols import StorageService


class SaveOrchestrator:
    """Orchestrates entity-specific save operations."""

    def __init__(
        self,
        github_service: RepositoryService,
        storage_service: StorageService,
        repository: str,
    ):
        self.github_service = github_service
        self.storage_service = storage_service
        self.repository = repository

    def execute_full_save(self) -> Dict[str, Any]:
        """Execute complete repository save operation."""
        results: Dict[str, Any] = {}

        # Create entity-specific use cases
        labels_job = SaveLabelsJob(
            self.github_service, self.storage_service, self.repository
        )
        labels_use_case = SaveLabelsUseCase(labels_job)

        issues_job = SaveIssuesJob(
            self.github_service, self.storage_service, self.repository
        )
        issues_use_case = SaveIssuesUseCase(issues_job)

        comments_job = SaveCommentsJob(
            self.github_service, self.storage_service, self.repository
        )
        comments_use_case = SaveCommentsUseCase(comments_job)

        prs_job = SavePullRequestsJob(
            self.github_service, self.storage_service, self.repository
        )
        prs_use_case = SavePullRequestsUseCase(prs_job)

        # Execute in dependency order
        # 1. Save labels first (no dependencies)
        results["labels"] = labels_use_case.execute()

        # 2. Save issues (depends on labels)
        results["issues"] = issues_use_case.execute()

        # 3. Save comments and PRs in parallel (both depend on issues/labels)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_comments = executor.submit(comments_use_case.execute)
            future_prs = executor.submit(prs_use_case.execute)

            results["comments"] = future_comments.result()
            results["pull_requests"] = future_prs.result()

        return results

    def execute_selective_save(self, entities: List[str]) -> Dict[str, Any]:
        """Execute selective entity save operation."""
        results = {}

        # Mapping of entity names to use case factories
        entity_factories: Dict[str, Any] = {
            "labels": lambda: SaveLabelsUseCase(
                SaveLabelsJob(
                    self.github_service, self.storage_service, self.repository
                )
            ),
            "issues": lambda: SaveIssuesUseCase(
                SaveIssuesJob(
                    self.github_service, self.storage_service, self.repository
                )
            ),
            "comments": lambda: SaveCommentsUseCase(
                SaveCommentsJob(
                    self.github_service, self.storage_service, self.repository
                )
            ),
            "pull_requests": lambda: SavePullRequestsUseCase(
                SavePullRequestsJob(
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
