from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models import Label, Issue, Comment, PullRequest, PullRequestComment, SubIssue


@dataclass
class SaveRepositoryRequest:
    repository_name: str
    output_path: str
    data_types: Optional[List[str]] = None  # None means all types
    include_metadata: bool = True


@dataclass
class CollectLabelsRequest:
    repository_name: str


@dataclass
class CollectLabelsResponse:
    labels: List[Label]
    collection_timestamp: datetime
    items_collected: int


@dataclass
class CollectIssuesRequest:
    repository_name: str


@dataclass
class CollectIssuesResponse:
    issues: List[Issue]
    collection_timestamp: datetime
    items_collected: int


@dataclass
class CollectCommentsRequest:
    repository_name: str
    issues: List[Issue]


@dataclass
class CollectCommentsResponse:
    comments: List[Comment]
    collection_timestamp: datetime
    items_collected: int


@dataclass
class CollectPullRequestsRequest:
    repository_name: str


@dataclass
class CollectPullRequestsResponse:
    pull_requests: List[PullRequest]
    collection_timestamp: datetime
    items_collected: int


@dataclass
class CollectPRCommentsRequest:
    repository_name: str
    pull_requests: List[PullRequest]


@dataclass
class CollectPRCommentsResponse:
    pr_comments: List[PullRequestComment]
    collection_timestamp: datetime
    items_collected: int


@dataclass
class CollectSubIssuesRequest:
    repository_name: str
    issues: List[Issue]


@dataclass
class CollectSubIssuesResponse:
    sub_issues: List[SubIssue]
    collection_timestamp: datetime
    items_collected: int


@dataclass
class SaveLabelsRequest:
    labels: List[Label]
    output_path: str


@dataclass
class SaveIssuesRequest:
    issues: List[Issue]
    output_path: str


@dataclass
class SaveCommentsRequest:
    comments: List[Comment]
    output_path: str


@dataclass
class SavePullRequestsRequest:
    pull_requests: List[PullRequest]
    output_path: str


@dataclass
class SavePRCommentsRequest:
    pr_comments: List[PullRequestComment]
    output_path: str


@dataclass
class SaveSubIssuesRequest:
    sub_issues: List[SubIssue]
    output_path: str


@dataclass
class ValidateRepositoryAccessRequest:
    repository_name: str


@dataclass
class AssociateSubIssuesRequest:
    issues: List[Issue]
    sub_issues: List[SubIssue]


@dataclass
class AssociateSubIssuesResponse:
    updated_issues: List[Issue]
    items_processed: int


@dataclass
class OperationResult:
    success: bool
    data_type: str
    items_processed: int = 0
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None


# Restore Operation Request/Response Objects


@dataclass
class RestoreRepositoryRequest:
    repository_name: str
    input_path: str
    data_types: Optional[List[str]] = None  # None means all required types
    label_conflict_strategy: str = "fail-if-existing"
    include_original_metadata: bool = True
    include_prs: bool = False
    include_sub_issues: bool = False


@dataclass
class RestoreLabelsRequest:
    repository_name: str
    labels: List[Label]
    conflict_strategy: str = "fail-if-existing"


@dataclass
class RestoreIssuesRequest:
    repository_name: str
    issues: List[Issue]
    include_original_metadata: bool = True


@dataclass
class RestoreIssuesResponse:
    issue_number_mapping: Dict[int, int]
    issues_created: int
    execution_time_seconds: float


@dataclass
class RestoreCommentsRequest:
    repository_name: str
    comments: List[Comment]
    issue_number_mapping: Dict[int, int]
    include_original_metadata: bool = True


@dataclass
class RestorePullRequestsRequest:
    repository_name: str
    pull_requests: List[PullRequest]
    include_original_metadata: bool = True


@dataclass
class RestorePRCommentsRequest:
    repository_name: str
    pr_comments: List[PullRequestComment]
    pr_number_mapping: Dict[int, int]
    include_original_metadata: bool = True


@dataclass
class RestoreSubIssuesRequest:
    repository_name: str
    sub_issues_by_depth: Dict[int, List[SubIssue]]
    issue_number_mapping: Dict[int, int]


@dataclass
class LabelConflictDetectionRequest:
    existing_labels: List[Label]
    labels_to_restore: List[Label]


@dataclass
class LabelConflictDetectionResponse:
    has_conflicts: bool
    conflicting_names: List[str]
    conflict_details: Dict[str, str]  # name -> conflict type


@dataclass
class ApplyLabelStrategyRequest:
    repository_name: str
    existing_labels: List[Label]
    labels_to_restore: List[Label]
    conflict_strategy: str


@dataclass
class ApplyLabelStrategyResponse:
    success: bool
    filtered_labels: Optional[List[Label]] = None
    error_message: Optional[str] = None


@dataclass
class LoadLabelsRequest:
    input_path: str


@dataclass
class LoadLabelsResponse:
    labels: List[Label]
    items_loaded: int
    execution_time_seconds: float


@dataclass
class LoadIssuesRequest:
    input_path: str


@dataclass
class LoadIssuesResponse:
    issues: List[Issue]
    items_loaded: int
    execution_time_seconds: float


@dataclass
class LoadCommentsRequest:
    input_path: str


@dataclass
class LoadCommentsResponse:
    comments: List[Comment]
    items_loaded: int
    execution_time_seconds: float


@dataclass
class LoadPullRequestsRequest:
    input_path: str


@dataclass
class LoadPullRequestsResponse:
    pull_requests: List[PullRequest]
    items_loaded: int
    execution_time_seconds: float


@dataclass
class LoadPRCommentsRequest:
    input_path: str


@dataclass
class LoadPRCommentsResponse:
    pr_comments: List[PullRequestComment]
    items_loaded: int
    execution_time_seconds: float


@dataclass
class LoadSubIssuesRequest:
    input_path: str


@dataclass
class LoadSubIssuesResponse:
    sub_issues: List[SubIssue]
    items_loaded: int
    execution_time_seconds: float


@dataclass
class ValidateRestoreDataRequest:
    input_path: str
    include_prs: bool = False
    include_sub_issues: bool = False


@dataclass
class SubIssueHierarchyRequest:
    sub_issues: List[SubIssue]
    issue_number_mapping: Dict[int, int]


@dataclass
class SubIssueHierarchyResponse:
    sub_issues_by_depth: Dict[int, List[SubIssue]]
    max_depth: int
    circular_dependencies: List[str]


@dataclass
class ValidateSubIssueDataRequest:
    sub_issues: List[SubIssue]
    issue_number_mapping: Dict[int, int]


@dataclass
class CircularDependencyResponse:
    has_circular_dependencies: bool
    circular_dependency_chains: List[str]


@dataclass
class RestoreJobRequest:
    repository_name: str
    input_path: str
    data_type: str
    dependencies: Optional[Dict[str, Any]] = None
    include_original_metadata: bool = True
    conflict_strategy: str = "fail-if-existing"
