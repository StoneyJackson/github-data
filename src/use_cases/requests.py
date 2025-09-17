from dataclasses import dataclass
from typing import List, Optional
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
