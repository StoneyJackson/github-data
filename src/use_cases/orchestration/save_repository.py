from typing import List, Dict, Any, Union
from concurrent.futures import ThreadPoolExecutor, Future

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

        # Step 3: Collect data (can be parallelized)
        collection_data = self._collect_data_parallel(
            request.repository_name, data_types
        )

        # Step 4: Process associations if needed
        if "sub_issues" in data_types and "issues" in data_types:
            if "issues" in collection_data and "sub_issues" in collection_data:
                association_response = self._associate_sub_issues.execute(
                    AssociateSubIssuesRequest(
                        issues=collection_data["issues"],
                        sub_issues=collection_data["sub_issues"],
                    )
                )
                # Update issues with sub-issue associations
                collection_data["issues"] = association_response.updated_issues

        # Step 5: Save data (can be parallelized)
        persistence_results = self._save_data_parallel(
            request.output_path, collection_data, data_types
        )
        results.extend(persistence_results)

        return results

    def _collect_data_parallel(
        self, repo_name: str, data_types: List[str]
    ) -> Dict[str, Any]:
        """Collect multiple data types in parallel."""
        collection_data = {}

        with ThreadPoolExecutor(max_workers=6) as executor:
            futures: Dict[str, Future[Any]] = {}

            if "labels" in data_types:
                futures["labels"] = executor.submit(
                    self._collect_labels.execute, CollectLabelsRequest(repo_name)
                )

            if "issues" in data_types:
                futures["issues"] = executor.submit(
                    self._collect_issues.execute, CollectIssuesRequest(repo_name)
                )

            if "comments" in data_types:
                futures["comments"] = executor.submit(
                    self._collect_comments.execute,
                    CollectCommentsRequest(
                        repo_name, []
                    ),  # Empty list since we get all comments
                )

            if "pull_requests" in data_types:
                futures["pull_requests"] = executor.submit(
                    self._collect_pull_requests.execute,
                    CollectPullRequestsRequest(repo_name),
                )

            if "pr_comments" in data_types:
                futures["pr_comments"] = executor.submit(
                    self._collect_pr_comments.execute,
                    CollectPRCommentsRequest(
                        repo_name, []
                    ),  # Empty list since we get all comments
                )

            if "sub_issues" in data_types:
                futures["sub_issues"] = executor.submit(
                    self._collect_sub_issues.execute,
                    CollectSubIssuesRequest(
                        repo_name, []
                    ),  # Empty list since we get all sub-issues
                )

            # Collect results
            for data_type, future in futures.items():
                try:
                    response = future.result()
                    if data_type == "labels":
                        collection_data[data_type] = response.labels
                    elif data_type == "issues":
                        collection_data[data_type] = response.issues
                    elif data_type == "comments":
                        collection_data[data_type] = response.comments
                    elif data_type == "pull_requests":
                        collection_data[data_type] = response.pull_requests
                    elif data_type == "pr_comments":
                        collection_data[data_type] = response.pr_comments
                    elif data_type == "sub_issues":
                        collection_data[data_type] = response.sub_issues
                except Exception:
                    # If collection fails for any data type, set to empty list
                    collection_data[data_type] = []

        return collection_data

    def _save_data_parallel(
        self, output_path: str, collection_data: Dict[str, Any], data_types: List[str]
    ) -> List[OperationResult]:
        """Save multiple data types in parallel."""
        results = []

        with ThreadPoolExecutor(max_workers=6) as executor:
            futures: Dict[str, Future[OperationResult]] = {}

            if "labels" in data_types and "labels" in collection_data:
                futures["labels"] = executor.submit(
                    self._save_labels.execute,
                    SaveLabelsRequest(collection_data["labels"], output_path),
                )

            if "issues" in data_types and "issues" in collection_data:
                futures["issues"] = executor.submit(
                    self._save_issues.execute,
                    SaveIssuesRequest(collection_data["issues"], output_path),
                )

            if "comments" in data_types and "comments" in collection_data:
                futures["comments"] = executor.submit(
                    self._save_comments.execute,
                    SaveCommentsRequest(collection_data["comments"], output_path),
                )

            if "pull_requests" in data_types and "pull_requests" in collection_data:
                futures["pull_requests"] = executor.submit(
                    self._save_pull_requests.execute,
                    SavePullRequestsRequest(
                        collection_data["pull_requests"], output_path
                    ),
                )

            if "pr_comments" in data_types and "pr_comments" in collection_data:
                futures["pr_comments"] = executor.submit(
                    self._save_pr_comments.execute,
                    SavePRCommentsRequest(collection_data["pr_comments"], output_path),
                )

            if "sub_issues" in data_types and "sub_issues" in collection_data:
                futures["sub_issues"] = executor.submit(
                    self._save_sub_issues.execute,
                    SaveSubIssuesRequest(collection_data["sub_issues"], output_path),
                )

            # Collect results
            for data_type, future in futures.items():
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(
                        OperationResult(
                            success=False,
                            data_type=data_type,
                            error_message=f"Save operation failed: {str(e)}",
                        )
                    )

        return results
