# Restore Operation Decomposition Implementation Plan

**Project:** GitHub Data  
**Plan Date:** September 18, 2025  
**Based On:** Save Operation Decomposition and Job-Based Parallel Processing Plans  
**Target:** Decompose monolithic restore operation into focused use cases with job-based parallelism

## Overview

This plan details the step-by-step implementation to refactor the current monolithic 700+ line `restore_repository_data_with_services()` function into a collection of focused, testable use cases following Clean Architecture principles and implementing job-based parallel processing for optimal performance.

## Current State Analysis

### Existing Implementation Structure
```
restore_repository_data_with_services()  # 700+ lines with 7 parameters
├── _validate_data_files_exist()          # File existence validation
├── _restore_labels()                     # 120+ lines with 5 conflict strategies
│   ├── _handle_fail_if_existing()
│   ├── _handle_fail_if_conflict()
│   ├── _handle_delete_all()
│   ├── _handle_overwrite()
│   └── _handle_skip()
├── _restore_issues()                     # Issue restoration with number mapping
├── _restore_comments()                   # Comment restoration with issue mapping
├── _restore_pull_requests()              # Optional PR restoration
├── _restore_pr_comments()                # Optional PR comment restoration
└── _restore_sub_issues()                 # Complex hierarchy restoration
    └── _organize_sub_issues_by_depth()   # 60+ lines depth calculation
```

### Problems Addressed
1. **Monolithic orchestrator** - Single 700+ line function with multiple responsibilities
2. **Sequential execution** - No parallelization opportunities utilized
3. **Complex parameter passing** - 7 parameters with optional behavior flags
4. **Strategy pattern violation** - Label conflict strategies embedded in main function
5. **Tight coupling** - Sequential dependencies with shared state
6. **Limited error recovery** - Cannot resume from specific failure points
7. **All-or-nothing approach** - Cannot restore specific data types independently

## Implementation Architecture

### Use Case Hierarchy
```
RestoreRepositoryUseCase (Job-Based Orchestrator)
├── Validation Use Cases
│   ├── ValidateRestoreDataUseCase
│   └── ValidateRepositoryAccessUseCase (reuse from save)
├── Data Loading Use Cases
│   ├── LoadLabelsUseCase
│   ├── LoadIssuesUseCase
│   ├── LoadCommentsUseCase
│   ├── LoadPullRequestsUseCase
│   ├── LoadPRCommentsUseCase
│   └── LoadSubIssuesUseCase
├── Restoration Jobs (Independent Execution)
│   ├── RestoreLabelsJob
│   ├── RestoreIssuesJob
│   ├── RestoreCommentsJob (depends on RestoreIssuesJob)
│   ├── RestorePullRequestsJob
│   ├── RestorePRCommentsJob (depends on RestorePullRequestsJob)
│   └── RestoreSubIssuesJob (depends on RestoreIssuesJob)
├── Label Conflict Strategy Use Cases
│   ├── DetectLabelConflictsUseCase
│   ├── FailIfExistingStrategyUseCase
│   ├── FailIfConflictStrategyUseCase
│   ├── DeleteAllStrategyUseCase
│   ├── OverwriteStrategyUseCase
│   └── SkipStrategyUseCase
└── Sub-Issue Management Use Cases
    ├── ValidateSubIssueDataUseCase
    ├── DetectCircularDependenciesUseCase
    ├── CalculateHierarchyDepthUseCase
    ├── OrganizeByDepthUseCase
    └── CreateSubIssueRelationshipUseCase
```

### Job-Based Parallelism Design

#### Job Dependency Graph
```
Independent Jobs (Parallel):
- RestoreLabelsJob
- RestorePullRequestsJob

Sequential Dependencies:
- RestoreIssuesJob → RestoreCommentsJob
- RestoreIssuesJob → RestoreSubIssuesJob  
- RestorePullRequestsJob → RestorePRCommentsJob
```

#### Execution Flow
1. **Phase 1**: Validation (sequential)
2. **Phase 2**: Data Loading (parallel - all types)
3. **Phase 3**: Independent Restoration (parallel)
   - RestoreLabelsJob
   - RestorePullRequestsJob
4. **Phase 4**: Dependent Restoration (parallel within constraints)
   - RestoreIssuesJob (must complete first)
   - RestoreCommentsJob (after issues)
   - RestoreSubIssuesJob (after issues)
   - RestorePRCommentsJob (after PRs)

## Implementation Phases

### Phase 1: Foundation Infrastructure

#### Step 1.1: Extend Request/Response Objects
**File:** `src/use_cases/requests.py` (extend existing)
```python
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
    dependencies: Dict[str, Any] = None
    include_original_metadata: bool = True
    conflict_strategy: str = "fail-if-existing"
```

#### Step 1.2: Create Directory Structure
```
src/use_cases/
├── validation/              # Data and access validation
│   ├── __init__.py
│   ├── validate_restore_data.py
│   └── validate_repository_access.py (existing)
├── loading/                 # Data loading from files
│   ├── __init__.py
│   ├── load_labels.py
│   ├── load_issues.py
│   ├── load_comments.py
│   ├── load_pull_requests.py
│   ├── load_pr_comments.py
│   └── load_sub_issues.py
├── restoration/             # Individual data type restoration
│   ├── __init__.py
│   ├── restore_labels.py
│   ├── restore_issues.py
│   ├── restore_comments.py
│   ├── restore_pull_requests.py
│   ├── restore_pr_comments.py
│   └── restore_sub_issues.py
├── conflict_resolution/     # Label conflict strategies
│   ├── __init__.py
│   ├── detect_conflicts.py
│   ├── fail_if_existing_strategy.py
│   ├── fail_if_conflict_strategy.py
│   ├── delete_all_strategy.py
│   ├── overwrite_strategy.py
│   └── skip_strategy.py
├── sub_issue_management/    # Sub-issue hierarchy handling
│   ├── __init__.py
│   ├── validate_sub_issue_data.py
│   ├── detect_circular_dependencies.py
│   ├── calculate_hierarchy_depth.py
│   ├── organize_by_depth.py
│   └── create_relationship.py
├── jobs/                    # Job-based restoration workflows
│   ├── __init__.py
│   ├── restore_labels_job.py
│   ├── restore_issues_job.py
│   ├── restore_comments_job.py
│   ├── restore_pull_requests_job.py
│   ├── restore_pr_comments_job.py
│   └── restore_sub_issues_job.py
└── orchestration/
    └── restore_repository.py
```

### Phase 2: Validation Use Cases Implementation

#### Step 2.1: Implement ValidateRestoreDataUseCase
**File:** `src/use_cases/validation/validate_restore_data.py`
```python
from pathlib import Path
from typing import List

from ..requests import ValidateRestoreDataRequest, OperationResult
from .. import UseCase

class ValidateRestoreDataUseCase(UseCase[ValidateRestoreDataRequest, OperationResult]):
    def execute(self, request: ValidateRestoreDataRequest) -> OperationResult:
        try:
            input_dir = Path(request.input_path)
            required_files = self._determine_required_files(request)
            missing_files = []
            
            for filename in required_files:
                file_path = input_dir / filename
                if not file_path.exists():
                    missing_files.append(str(file_path))
            
            if missing_files:
                return OperationResult(
                    success=False,
                    data_type="validation",
                    error_message=f"Required files not found: {', '.join(missing_files)}"
                )
            
            return OperationResult(
                success=True,
                data_type="validation",
                items_processed=len(required_files)
            )
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="validation", 
                error_message=f"Validation failed: {str(e)}"
            )

    def _determine_required_files(self, request: ValidateRestoreDataRequest) -> List[str]:
        required = ["labels.json", "issues.json", "comments.json"]
        
        if request.include_prs:
            required.extend(["pull_requests.json", "pr_comments.json"])
        
        if request.include_sub_issues:
            required.append("sub_issues.json")
        
        return required
```

### Phase 3: Data Loading Use Cases Implementation

#### Step 3.1: Implement LoadLabelsUseCase
**File:** `src/use_cases/loading/load_labels.py`
```python
import time
from pathlib import Path
from typing import List

from ..requests import LoadLabelsRequest, LoadLabelsResponse
from .. import UseCase
from ...storage.protocols import StorageService
from ...models import Label

class LoadLabelsUseCase(UseCase[LoadLabelsRequest, LoadLabelsResponse]):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: LoadLabelsRequest) -> LoadLabelsResponse:
        start_time = time.time()
        
        try:
            labels_file = Path(request.input_path) / "labels.json"
            labels = self._storage_service.load_data(labels_file, Label)
            
            execution_time = time.time() - start_time
            
            return LoadLabelsResponse(
                labels=labels,
                items_loaded=len(labels),
                execution_time_seconds=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"Failed to load labels: {str(e)}") from e
```

#### Step 3.2: Implement Remaining Loading Use Cases
Follow same pattern for:
- `LoadIssuesUseCase` 
- `LoadCommentsUseCase`
- `LoadPullRequestsUseCase` 
- `LoadPRCommentsUseCase`
- `LoadSubIssuesUseCase`

### Phase 4: Conflict Resolution Strategy Use Cases

#### Step 4.1: Implement DetectLabelConflictsUseCase
**File:** `src/use_cases/conflict_resolution/detect_conflicts.py`
```python
from typing import Dict, List

from ..requests import LabelConflictDetectionRequest, LabelConflictDetectionResponse
from .. import UseCase
from ...models import Label

class DetectLabelConflictsUseCase(UseCase[LabelConflictDetectionRequest, LabelConflictDetectionResponse]):
    def execute(self, request: LabelConflictDetectionRequest) -> LabelConflictDetectionResponse:
        existing_by_name = {label.name: label for label in request.existing_labels}
        conflicting_names = []
        conflict_details = {}
        
        for label_to_restore in request.labels_to_restore:
            if label_to_restore.name in existing_by_name:
                existing_label = existing_by_name[label_to_restore.name]
                
                # Check for actual conflicts (different properties)
                if (label_to_restore.color != existing_label.color or 
                    label_to_restore.description != existing_label.description):
                    conflicting_names.append(label_to_restore.name)
                    conflict_details[label_to_restore.name] = self._describe_conflict(
                        existing_label, label_to_restore
                    )
        
        return LabelConflictDetectionResponse(
            has_conflicts=len(conflicting_names) > 0,
            conflicting_names=conflicting_names,
            conflict_details=conflict_details
        )

    def _describe_conflict(self, existing: Label, to_restore: Label) -> str:
        conflicts = []
        if existing.color != to_restore.color:
            conflicts.append(f"color: {existing.color} vs {to_restore.color}")
        if existing.description != to_restore.description:
            conflicts.append(f"description: '{existing.description}' vs '{to_restore.description}'")
        return "; ".join(conflicts)
```

#### Step 4.2: Implement Strategy Use Cases
**File:** `src/use_cases/conflict_resolution/fail_if_existing_strategy.py`
```python
from typing import List

from ..requests import ApplyLabelStrategyRequest, ApplyLabelStrategyResponse
from .. import UseCase
from ...models import Label

class FailIfExistingStrategyUseCase(UseCase[ApplyLabelStrategyRequest, ApplyLabelStrategyResponse]):
    def execute(self, request: ApplyLabelStrategyRequest) -> ApplyLabelStrategyResponse:
        if request.existing_labels:
            return ApplyLabelStrategyResponse(
                success=False,
                error_message=(
                    f"Repository has {len(request.existing_labels)} existing labels. "
                    f"Change strategy to allow restoration with existing labels."
                )
            )
        
        return ApplyLabelStrategyResponse(
            success=True,
            filtered_labels=request.labels_to_restore
        )
```

Implement similar pattern for:
- `FailIfConflictStrategyUseCase`
- `DeleteAllStrategyUseCase`  
- `OverwriteStrategyUseCase`
- `SkipStrategyUseCase`

### Phase 5: Restoration Use Cases Implementation

#### Step 5.1: Implement RestoreLabelsUseCase
**File:** `src/use_cases/restoration/restore_labels.py`
```python
import time
from typing import List, Dict

from ..requests import RestoreLabelsRequest, OperationResult, ApplyLabelStrategyRequest
from .. import UseCase
from ...github.protocols import RepositoryService
from ...models import Label
from ..conflict_resolution import (
    DetectLabelConflictsUseCase,
    FailIfExistingStrategyUseCase,
    FailIfConflictStrategyUseCase,
    DeleteAllStrategyUseCase,
    OverwriteStrategyUseCase,
    SkipStrategyUseCase
)

class RestoreLabelsUseCase(UseCase[RestoreLabelsRequest, OperationResult]):
    def __init__(
        self,
        github_service: RepositoryService,
        fail_if_existing: FailIfExistingStrategyUseCase,
        fail_if_conflict: FailIfConflictStrategyUseCase,
        delete_all: DeleteAllStrategyUseCase,
        overwrite: OverwriteStrategyUseCase,
        skip: SkipStrategyUseCase
    ):
        self._github_service = github_service
        self._strategies = {
            "fail-if-existing": fail_if_existing,
            "fail-if-conflict": fail_if_conflict,
            "delete-all": delete_all,
            "overwrite": overwrite,
            "skip": skip
        }

    def execute(self, request: RestoreLabelsRequest) -> OperationResult:
        start_time = time.time()
        
        try:
            # Get existing labels
            from ...github import converters
            raw_existing = self._github_service.get_repository_labels(request.repository_name)
            existing_labels = [converters.convert_to_label(label_dict) for label_dict in raw_existing]
            
            # Apply conflict resolution strategy
            strategy = self._strategies.get(request.conflict_strategy)
            if not strategy:
                raise ValueError(f"Unknown strategy: {request.conflict_strategy}")
            
            strategy_result = strategy.execute(ApplyLabelStrategyRequest(
                repository_name=request.repository_name,
                existing_labels=existing_labels,
                labels_to_restore=request.labels,
                conflict_strategy=request.conflict_strategy
            ))
            
            if not strategy_result.success:
                execution_time = time.time() - start_time
                return OperationResult(
                    success=False,
                    data_type="labels",
                    error_message=strategy_result.error_message,
                    execution_time_seconds=execution_time
                )
            
            # Create labels (strategy may have modified the list)
            labels_to_create = strategy_result.filtered_labels or request.labels
            created_count = 0
            
            for label in labels_to_create:
                self._github_service.create_label(
                    request.repository_name,
                    label.name,
                    label.color,
                    label.description or ""
                )
                created_count += 1
            
            execution_time = time.time() - start_time
            
            return OperationResult(
                success=True,
                data_type="labels",
                items_processed=created_count,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return OperationResult(
                success=False,
                data_type="labels",
                error_message=str(e),
                execution_time_seconds=execution_time
            )
```

#### Step 5.2: Implement RestoreIssuesUseCase
```python
class RestoreIssuesUseCase(UseCase[RestoreIssuesRequest, RestoreIssuesResponse]):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: RestoreIssuesRequest) -> RestoreIssuesResponse:
        start_time = time.time()
        issue_number_mapping = {}
        
        try:
            for issue in request.issues:
                # Prepare issue body with metadata if requested
                issue_body = self._prepare_issue_body(issue, request.include_original_metadata)
                label_names = [label.name for label in issue.labels]
                
                # Create issue
                created_issue = self._github_service.create_issue(
                    request.repository_name, 
                    issue.title, 
                    issue_body, 
                    label_names
                )
                issue_number_mapping[issue.number] = created_issue["number"]
                
                # Handle closed state
                if issue.state == "closed":
                    self._close_issue_if_needed(
                        request.repository_name, 
                        created_issue["number"], 
                        issue.state_reason
                    )
            
            execution_time = time.time() - start_time
            
            return RestoreIssuesResponse(
                issue_number_mapping=issue_number_mapping,
                issues_created=len(issue_number_mapping),
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            raise RuntimeError(f"Failed to restore issues: {str(e)}") from e

    def _prepare_issue_body(self, issue: Issue, include_metadata: bool) -> str:
        if include_metadata:
            from ...github.metadata import add_issue_metadata_footer
            return add_issue_metadata_footer(issue)
        return issue.body or ""

    def _close_issue_if_needed(self, repo_name: str, issue_number: int, state_reason: str) -> None:
        try:
            self._github_service.close_issue(repo_name, issue_number, state_reason)
        except Exception as e:
            print(f"Warning: Failed to close issue #{issue_number}: {e}")
```

### Phase 6: Job-Based Restoration Implementation

#### Step 6.1: Create Job Base Interface
**File:** `src/use_cases/jobs/__init__.py`
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..requests import OperationResult

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
    def __init__(self):
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
            return result
        
        # Continue until all jobs are completed
        with ThreadPoolExecutor(max_workers=4) as executor:
            while len(completed_jobs) < len(self.jobs):
                # Find jobs that can be executed
                ready_jobs = [
                    job for job in self.jobs.values() 
                    if not job.completed and can_execute_job(job)
                ]
                
                if not ready_jobs:
                    # Check for circular dependencies or other issues
                    remaining = [j.job_id for j in self.jobs.values() if not j.completed]
                    raise RuntimeError(f"No jobs can proceed. Remaining: {remaining}")
                
                # Submit ready jobs for execution
                future_to_job = {
                    executor.submit(execute_job, job): job 
                    for job in ready_jobs
                }
                
                # Wait for at least one job to complete
                for future in as_completed(future_to_job):
                    result = future.result()
                    results.append(result)
                    break
        
        return results
```

#### Step 6.2: Implement RestoreLabelsJob
**File:** `src/use_cases/jobs/restore_labels_job.py`
```python
from typing import Any, Dict
from ..requests import OperationResult, RestoreLabelsRequest, LoadLabelsRequest
from ..loading import LoadLabelsUseCase
from ..restoration import RestoreLabelsUseCase
from . import RestoreJob

class RestoreLabelsJob(RestoreJob):
    def __init__(
        self, 
        repository_name: str,
        input_path: str,
        conflict_strategy: str,
        load_labels: LoadLabelsUseCase,
        restore_labels: RestoreLabelsUseCase
    ):
        super().__init__("restore_labels")
        self.repository_name = repository_name
        self.input_path = input_path
        self.conflict_strategy = conflict_strategy
        self._load_labels = load_labels
        self._restore_labels = restore_labels

    def execute(self, context: Dict[str, Any]) -> OperationResult:
        try:
            # Load labels from file
            load_response = self._load_labels.execute(
                LoadLabelsRequest(input_path=self.input_path)
            )
            
            # Restore labels
            result = self._restore_labels.execute(RestoreLabelsRequest(
                repository_name=self.repository_name,
                labels=load_response.labels,
                conflict_strategy=self.conflict_strategy
            ))
            
            return result
            
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="labels",
                error_message=f"Label restoration job failed: {str(e)}"
            )
```

#### Step 6.3: Implement RestoreIssuesJob
**File:** `src/use_cases/jobs/restore_issues_job.py`
```python
from typing import Any, Dict
from ..requests import OperationResult, RestoreIssuesRequest, LoadIssuesRequest
from ..loading import LoadIssuesUseCase
from ..restoration import RestoreIssuesUseCase
from . import RestoreJob

class RestoreIssuesJob(RestoreJob):
    def __init__(
        self, 
        repository_name: str,
        input_path: str,
        include_original_metadata: bool,
        load_issues: LoadIssuesUseCase,
        restore_issues: RestoreIssuesUseCase
    ):
        super().__init__("restore_issues")
        self.repository_name = repository_name
        self.input_path = input_path
        self.include_original_metadata = include_original_metadata
        self._load_issues = load_issues
        self._restore_issues = restore_issues

    def execute(self, context: Dict[str, Any]) -> OperationResult:
        try:
            # Load issues from file
            load_response = self._load_issues.execute(
                LoadIssuesRequest(input_path=self.input_path)
            )
            
            # Restore issues
            restore_response = self._restore_issues.execute(RestoreIssuesRequest(
                repository_name=self.repository_name,
                issues=load_response.issues,
                include_original_metadata=self.include_original_metadata
            ))
            
            # Store issue number mapping in context for dependent jobs
            context["issue_number_mapping"] = restore_response.issue_number_mapping
            
            return OperationResult(
                success=True,
                data_type="issues",
                items_processed=restore_response.issues_created,
                execution_time_seconds=restore_response.execution_time_seconds
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="issues",
                error_message=f"Issue restoration job failed: {str(e)}"
            )
```

#### Step 6.4: Implement RestoreCommentsJob
**File:** `src/use_cases/jobs/restore_comments_job.py`
```python
from typing import Any, Dict
from ..requests import OperationResult, RestoreCommentsRequest, LoadCommentsRequest
from ..loading import LoadCommentsUseCase
from ..restoration import RestoreCommentsUseCase
from . import RestoreJob

class RestoreCommentsJob(RestoreJob):
    def __init__(
        self, 
        repository_name: str,
        input_path: str,
        include_original_metadata: bool,
        load_comments: LoadCommentsUseCase,
        restore_comments: RestoreCommentsUseCase
    ):
        super().__init__("restore_comments", dependencies=["restore_issues"])
        self.repository_name = repository_name
        self.input_path = input_path
        self.include_original_metadata = include_original_metadata
        self._load_comments = load_comments
        self._restore_comments = restore_comments

    def execute(self, context: Dict[str, Any]) -> OperationResult:
        try:
            # Get issue number mapping from dependency
            issue_number_mapping = context.get("issue_number_mapping", {})
            if not issue_number_mapping:
                return OperationResult(
                    success=False,
                    data_type="comments",
                    error_message="Issue number mapping not available from RestoreIssuesJob"
                )
            
            # Load comments from file
            load_response = self._load_comments.execute(
                LoadCommentsRequest(input_path=self.input_path)
            )
            
            # Restore comments
            result = self._restore_comments.execute(RestoreCommentsRequest(
                repository_name=self.repository_name,
                comments=load_response.comments,
                issue_number_mapping=issue_number_mapping,
                include_original_metadata=self.include_original_metadata
            ))
            
            return result
            
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="comments",
                error_message=f"Comment restoration job failed: {str(e)}"
            )
```

### Phase 7: Sub-Issue Management Use Cases

#### Step 7.1: Implement ValidateSubIssueDataUseCase
**File:** `src/use_cases/sub_issue_management/validate_sub_issue_data.py`
```python
from typing import Dict, List

from ..requests import ValidateSubIssueDataRequest, OperationResult
from .. import UseCase

class ValidateSubIssueDataUseCase(UseCase[ValidateSubIssueDataRequest, OperationResult]):
    def execute(self, request: ValidateSubIssueDataRequest) -> OperationResult:
        try:
            missing_parents = []
            missing_children = []
            
            for sub_issue in request.sub_issues:
                if sub_issue.parent_issue_number not in request.issue_number_mapping:
                    missing_parents.append(sub_issue.parent_issue_number)
                
                if sub_issue.sub_issue_number not in request.issue_number_mapping:
                    missing_children.append(sub_issue.sub_issue_number)
            
            if missing_parents or missing_children:
                error_parts = []
                if missing_parents:
                    error_parts.append(f"Missing parent issues: {missing_parents}")
                if missing_children:
                    error_parts.append(f"Missing child issues: {missing_children}")
                
                return OperationResult(
                    success=False,
                    data_type="sub_issue_validation",
                    error_message="; ".join(error_parts)
                )
            
            return OperationResult(
                success=True,
                data_type="sub_issue_validation",
                items_processed=len(request.sub_issues)
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="sub_issue_validation",
                error_message=f"Sub-issue validation failed: {str(e)}"
            )
```

#### Step 7.2: Implement DetectCircularDependenciesUseCase
**File:** `src/use_cases/sub_issue_management/detect_circular_dependencies.py`
```python
from typing import Dict, List, Set

from ..requests import SubIssueHierarchyRequest, CircularDependencyResponse
from .. import UseCase

class DetectCircularDependenciesUseCase(UseCase[SubIssueHierarchyRequest, CircularDependencyResponse]):
    def execute(self, request: SubIssueHierarchyRequest) -> CircularDependencyResponse:
        parents_by_child = {}
        circular_dependencies = []
        
        # Build parent-child mapping
        for sub_issue in request.sub_issues:
            parent_id = sub_issue.parent_issue_number
            child_id = sub_issue.sub_issue_number
            
            if parent_id in request.issue_number_mapping and child_id in request.issue_number_mapping:
                parents_by_child[child_id] = parent_id
        
        # Detect cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: int) -> bool:
            if node in rec_stack:
                return True
            if node in visited:
                return False
                
            visited.add(node)
            rec_stack.add(node)
            
            if node in parents_by_child:
                parent = parents_by_child[node]
                if has_cycle(parent):
                    circular_dependencies.append(f"#{node} -> #{parent}")
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check all nodes for cycles
        for child_id in parents_by_child.keys():
            if child_id not in visited:
                has_cycle(child_id)
        
        return CircularDependencyResponse(
            has_circular_dependencies=len(circular_dependencies) > 0,
            circular_dependency_chains=circular_dependencies
        )
```

#### Step 7.3: Implement RestoreSubIssuesJob
**File:** `src/use_cases/jobs/restore_sub_issues_job.py`
```python
from typing import Any, Dict
from ..requests import OperationResult, LoadSubIssuesRequest, ValidateSubIssueDataRequest
from ..loading import LoadSubIssuesUseCase
from ..sub_issue_management import (
    ValidateSubIssueDataUseCase,
    DetectCircularDependenciesUseCase,
    OrganizeByDepthUseCase
)
from ..restoration import RestoreSubIssuesUseCase
from . import RestoreJob

class RestoreSubIssuesJob(RestoreJob):
    def __init__(
        self, 
        repository_name: str,
        input_path: str,
        load_sub_issues: LoadSubIssuesUseCase,
        validate_sub_issues: ValidateSubIssueDataUseCase,
        detect_circular_deps: DetectCircularDependenciesUseCase,
        organize_by_depth: OrganizeByDepthUseCase,
        restore_sub_issues: RestoreSubIssuesUseCase
    ):
        super().__init__("restore_sub_issues", dependencies=["restore_issues"])
        self.repository_name = repository_name
        self.input_path = input_path
        self._load_sub_issues = load_sub_issues
        self._validate_sub_issues = validate_sub_issues
        self._detect_circular_deps = detect_circular_deps
        self._organize_by_depth = organize_by_depth
        self._restore_sub_issues = restore_sub_issues

    def execute(self, context: Dict[str, Any]) -> OperationResult:
        try:
            # Get issue number mapping from dependency
            issue_number_mapping = context.get("issue_number_mapping", {})
            if not issue_number_mapping:
                return OperationResult(
                    success=False,
                    data_type="sub_issues",
                    error_message="Issue number mapping not available from RestoreIssuesJob"
                )
            
            # Load sub-issues from file
            load_response = self._load_sub_issues.execute(
                LoadSubIssuesRequest(input_path=self.input_path)
            )
            
            if not load_response.sub_issues:
                return OperationResult(
                    success=True,
                    data_type="sub_issues",
                    items_processed=0
                )
            
            # Validate sub-issue data
            validation_result = self._validate_sub_issues.execute(
                ValidateSubIssueDataRequest(
                    sub_issues=load_response.sub_issues,
                    issue_number_mapping=issue_number_mapping
                )
            )
            
            if not validation_result.success:
                return validation_result
            
            # Detect circular dependencies
            circular_deps_response = self._detect_circular_deps.execute(
                SubIssueHierarchyRequest(
                    sub_issues=load_response.sub_issues,
                    issue_number_mapping=issue_number_mapping
                )
            )
            
            if circular_deps_response.has_circular_dependencies:
                return OperationResult(
                    success=False,
                    data_type="sub_issues",
                    error_message=f"Circular dependencies detected: {circular_deps_response.circular_dependency_chains}"
                )
            
            # Organize by depth for proper ordering
            hierarchy_response = self._organize_by_depth.execute(
                SubIssueHierarchyRequest(
                    sub_issues=load_response.sub_issues,
                    issue_number_mapping=issue_number_mapping
                )
            )
            
            # Restore sub-issues in dependency order
            result = self._restore_sub_issues.execute(RestoreSubIssuesRequest(
                repository_name=self.repository_name,
                sub_issues_by_depth=hierarchy_response.sub_issues_by_depth,
                issue_number_mapping=issue_number_mapping
            ))
            
            return result
            
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="sub_issues",
                error_message=f"Sub-issue restoration job failed: {str(e)}"
            )
```

### Phase 8: Orchestrator Implementation

#### Step 8.1: Implement RestoreRepositoryUseCase
**File:** `src/use_cases/orchestration/restore_repository.py`
```python
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from ..requests import RestoreRepositoryRequest, OperationResult, ValidateRestoreDataRequest
from .. import UseCase
from ..validation import ValidateRestoreDataUseCase, ValidateRepositoryAccessUseCase
from ..jobs import (
    JobOrchestrator,
    RestoreLabelsJob,
    RestoreIssuesJob,
    RestoreCommentsJob,
    RestorePullRequestsJob,
    RestorePRCommentsJob,
    RestoreSubIssuesJob
)

class RestoreRepositoryUseCase(UseCase[RestoreRepositoryRequest, List[OperationResult]]):
    def __init__(
        self,
        validate_data: ValidateRestoreDataUseCase,
        validate_access: ValidateRepositoryAccessUseCase,
        job_factory: 'RestoreJobFactory'  # Factory to create jobs with dependencies
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
                include_sub_issues=request.include_sub_issues
            )
        )
        results.append(validation_result)
        
        if not validation_result.success:
            return results
        
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

    def _execute_restoration_jobs(self, request: RestoreRepositoryRequest) -> List[OperationResult]:
        """Execute restoration using job-based parallelism."""
        orchestrator = JobOrchestrator()
        
        # Determine which jobs to run
        data_types = request.data_types or self._get_default_data_types(request)
        
        # Add independent jobs
        if "labels" in data_types:
            orchestrator.add_job(self._job_factory.create_restore_labels_job(
                request.repository_name,
                request.input_path,
                request.label_conflict_strategy
            ))
        
        if "pull_requests" in data_types and request.include_prs:
            orchestrator.add_job(self._job_factory.create_restore_pull_requests_job(
                request.repository_name,
                request.input_path,
                request.include_original_metadata
            ))
        
        # Add dependent jobs
        if "issues" in data_types:
            orchestrator.add_job(self._job_factory.create_restore_issues_job(
                request.repository_name,
                request.input_path,
                request.include_original_metadata
            ))
        
        if "comments" in data_types:
            orchestrator.add_job(self._job_factory.create_restore_comments_job(
                request.repository_name,
                request.input_path,
                request.include_original_metadata
            ))
        
        if "pr_comments" in data_types and request.include_prs:
            orchestrator.add_job(self._job_factory.create_restore_pr_comments_job(
                request.repository_name,
                request.input_path,
                request.include_original_metadata
            ))
        
        if "sub_issues" in data_types and request.include_sub_issues:
            orchestrator.add_job(self._job_factory.create_restore_sub_issues_job(
                request.repository_name,
                request.input_path
            ))
        
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
    
    def __init__(self, **use_cases):
        # Store all required use cases for job creation
        self._use_cases = use_cases
    
    def create_restore_labels_job(self, repo_name: str, input_path: str, conflict_strategy: str) -> RestoreLabelsJob:
        return RestoreLabelsJob(
            repository_name=repo_name,
            input_path=input_path,
            conflict_strategy=conflict_strategy,
            load_labels=self._use_cases['load_labels'],
            restore_labels=self._use_cases['restore_labels']
        )
    
    def create_restore_issues_job(self, repo_name: str, input_path: str, include_metadata: bool) -> RestoreIssuesJob:
        return RestoreIssuesJob(
            repository_name=repo_name,
            input_path=input_path,
            include_original_metadata=include_metadata,
            load_issues=self._use_cases['load_issues'],
            restore_issues=self._use_cases['restore_issues']
        )
    
    # ... other job creation methods
```

### Phase 9: Integration and Migration

#### Step 9.1: Update Main Entry Point
**File:** `src/operations/restore.py`
```python
def restore_repository_data_with_services(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    data_path: str,
    label_conflict_strategy: str = "fail-if-existing",
    include_original_metadata: bool = True,
    include_prs: bool = False,
    include_sub_issues: bool = False,
) -> None:
    """Restore labels, issues, comments, PRs and sub-issues using injected services."""
    # Create orchestrator use case
    restore_use_case = _create_restore_repository_use_case(github_service, storage_service)
    
    # Execute with new use case architecture
    request = RestoreRepositoryRequest(
        repository_name=repo_name,
        input_path=data_path,
        label_conflict_strategy=label_conflict_strategy,
        include_original_metadata=include_original_metadata,
        include_prs=include_prs,
        include_sub_issues=include_sub_issues
    )
    
    results = restore_use_case.execute(request)
    
    # Handle errors (maintain existing behavior)
    failed_operations = [r for r in results if not r.success]
    if failed_operations:
        # Aggregate error messages maintaining backward compatibility
        error_messages = [r.error_message for r in failed_operations if r.error_message]
        raise Exception(f"Restore operation failed: {'; '.join(error_messages)}")

def _create_restore_repository_use_case(
    github_service: RepositoryService, 
    storage_service: StorageService
) -> RestoreRepositoryUseCase:
    """Factory function to create configured RestoreRepositoryUseCase."""
    # Create all use case dependencies and job factory
    # Return configured orchestrator
    pass
```

#### Step 9.2: Update CLI Interface
Add selective restore capabilities:
```bash
python -m github_data restore owner/repo --data-types labels,issues
python -m github_data restore owner/repo --exclude pull_requests
python -m github_data restore owner/repo --resume-from issues  # Future enhancement
```

## Testing Strategy

### Unit Testing Approach

#### Individual Use Case Tests
```python
# tests/test_use_cases/test_restoration/test_restore_labels.py
class TestRestoreLabelsUseCase:
    def test_successful_restoration(self, mock_github_service):
        # Test successful label restoration
        pass
        
    def test_conflict_strategy_application(self, mock_github_service):
        # Test different conflict strategies
        pass
        
    def test_api_error_handling(self, mock_github_service):
        # Test GitHub API error scenarios  
        pass

# tests/test_use_cases/test_sub_issue_management/test_detect_circular_dependencies.py
class TestDetectCircularDependenciesUseCase:
    def test_no_circular_dependencies(self):
        # Test valid hierarchy
        pass
        
    def test_simple_circular_dependency(self):
        # Test A -> B -> A cycle
        pass
        
    def test_complex_circular_dependency(self):
        # Test A -> B -> C -> A cycle
        pass
```

#### Job-Based Testing
```python
# tests/test_use_cases/test_jobs/test_restore_labels_job.py
class TestRestoreLabelsJob:
    def test_successful_execution(self, mock_use_cases):
        # Test successful job execution
        pass
        
    def test_dependency_satisfaction(self, mock_use_cases):
        # Test dependency checking
        pass
        
    def test_error_handling(self, mock_use_cases):
        # Test job error scenarios
        pass

# tests/test_use_cases/test_jobs/test_job_orchestrator.py
class TestJobOrchestrator:
    def test_parallel_execution(self):
        # Test independent jobs run in parallel
        pass
        
    def test_dependency_ordering(self):
        # Test dependent jobs wait for dependencies
        pass
        
    def test_error_propagation(self):
        # Test error handling in job dependencies
        pass
```

#### Strategy Pattern Tests
```python
# tests/test_use_cases/test_conflict_resolution/test_strategies.py
class TestLabelConflictStrategies:
    def test_fail_if_existing_with_no_labels(self):
        # Test strategy with empty repository
        pass
        
    def test_fail_if_existing_with_existing_labels(self):
        # Test strategy failure case
        pass
        
    def test_overwrite_strategy_updates_existing(self):
        # Test overwrite behavior  
        pass
        
    def test_skip_strategy_filters_conflicts(self):
        # Test skip logic
        pass
```

#### Integration Tests
```python
# tests/test_use_cases/test_orchestration/test_restore_repository.py
class TestRestoreRepositoryUseCase:
    def test_complete_restore_workflow(self, mock_services):
        # Test full restore operation
        pass
        
    def test_selective_data_type_restore(self, mock_services):
        # Test restoring only specific data types
        pass
        
    def test_job_based_parallelism(self, mock_services):
        # Test concurrent job execution
        pass
        
    def test_resume_from_failure(self, mock_services):
        # Test resuming from specific failure points (future)
        pass
```

### Performance Testing
- Job-based execution benchmarks vs sequential
- Memory usage monitoring for large datasets
- Sub-issue hierarchy calculation performance
- Error recovery and retry timing
- Parallel job coordination overhead

## Migration Timeline

### Week 1: Foundation and Validation
- [ ] Extend use case infrastructure for restore operations
- [ ] Implement validation use cases
- [ ] Create comprehensive unit tests
- [ ] Set up directory structure

### Week 2: Data Loading Use Cases
- [ ] Implement all 6 loading use cases
- [ ] Add error handling for file system issues
- [ ] Create performance benchmarks
- [ ] Add comprehensive unit tests

### Week 3: Conflict Resolution Strategies  
- [ ] Implement all 5 strategy use cases
- [ ] Extract conflict detection logic
- [ ] Add comprehensive strategy tests
- [ ] Document strategy extensibility

### Week 4: Core Restoration Use Cases
- [ ] Implement labels, issues, comments restoration
- [ ] Add number mapping logic
- [ ] Implement metadata handling
- [ ] Create restoration integration tests

### Week 5: Sub-Issue Management
- [ ] Implement hierarchy validation use cases
- [ ] Extract circular dependency detection
- [ ] Implement depth calculation and ordering
- [ ] Add comprehensive hierarchy tests

### Week 6: Job-Based Architecture
- [ ] Implement job base interface and orchestrator
- [ ] Create all restoration jobs
- [ ] Add dependency resolution logic
- [ ] Test parallel execution and dependency handling

### Week 7: Advanced Restoration (PRs and Sub-Issues)
- [ ] Implement PR restoration jobs
- [ ] Implement sub-issue restoration jobs
- [ ] Add branch validation for PRs
- [ ] Test complex restoration scenarios

### Week 8: Orchestrator Implementation
- [ ] Implement RestoreRepositoryUseCase with job orchestration
- [ ] Add job factory for dependency injection
- [ ] Implement error aggregation and reporting
- [ ] Add selective restoration logic

### Week 9: Integration and Migration
- [ ] Update main entry point with backward compatibility
- [ ] Add CLI selective restore capabilities  
- [ ] Run full integration test suite
- [ ] Performance regression testing

## Success Metrics

### Code Quality Metrics
- **Function Size**: Main orchestrator reduced from 700+ lines to 80-120 lines
- **Job Separation**: Clean separation of 6 restoration jobs with dependency management
- **Strategy Implementation**: Clean separation of 5 conflict resolution strategies
- **Circular Dependencies**: Robust detection and handling of hierarchy issues
- **Test Coverage**: 95%+ coverage for all use cases and jobs
- **Cyclomatic Complexity**: Reduced from 15+ to 3-5 per function

### Performance Metrics  
- **Parallel Execution**: 40-60% reduction in total execution time for mixed workloads
- **Selective Restoration**: Support for individual data type restoration
- **Job Coordination**: Efficient dependency resolution with minimal overhead
- **Error Isolation**: Failures contained to specific jobs without affecting others

### Maintainability Metrics
- **Job Extensibility**: New restoration jobs added without modifying orchestrator
- **Strategy Extensibility**: New conflict strategies added without code modification
- **New Data Type Support**: 70% faster implementation of new data types
- **Bug Fix Isolation**: Issues contained to single use cases or jobs
- **Testing Speed**: Individual use case tests run in <50ms each

### Operational Metrics
- **Resume Operations**: Foundation for users to restart from specific failure points (future)
- **Selective Operations**: Restore only needed data types
- **Error Reporting**: Detailed error reporting per job and operation
- **Progress Tracking**: Real-time job completion status

## Risk Mitigation

### Backward Compatibility
- Keep existing function signatures unchanged
- Maintain identical error messages and behavior
- Preserve output formats and progress reporting
- Ensure CLI compatibility

### Complex State Management
- Thread-safe shared context for job coordination
- Proper cleanup of partial operations
- Transaction-like behavior for critical sections
- Comprehensive rollback capabilities (future enhancement)

### Performance Regression
- Benchmark current implementation performance
- Monitor job coordination overhead
- Test memory usage with large datasets
- Implement performance regression tests

### Migration Complexity
- Implement feature flags for gradual rollout
- Maintain both implementations during transition
- Create comprehensive migration tests
- Document rollback procedures

## Future Enhancements

### Phase 2 Extensions
1. **Resume/Retry Mechanisms**: Smart restart from failure points with job state persistence
2. **Configuration Management**: YAML/JSON-driven restore configuration
3. **Advanced Validation**: Schema validation and data integrity checks
4. **Progress Reporting**: Real-time job progress with ETA calculations
5. **Dry-Run Mode**: Preview restoration without making changes

### Advanced Features
- **Incremental Restore**: Only restore changes since last backup
- **Multi-Repository Restore**: Batch restore across multiple repositories
- **Cloud Integration**: Direct restore from cloud storage (S3, GCS)
- **Webhook Integration**: Notifications for restore completion/failure
- **Audit Logging**: Comprehensive logging of all restore operations
- **Smart Conflict Resolution**: ML-based conflict resolution suggestions

## Comparison with Save Operation

### Shared Components
- Use case base infrastructure
- OperationResult and request/response patterns
- Job orchestration architecture
- Error handling and reporting

### Restore-Specific Complexities
- **Conflict Resolution**: Complex label conflict strategies
- **Number Mapping**: Issue/PR number mapping across operations
- **Dependency Ordering**: Strict ordering requirements for hierarchy restoration
- **Data Validation**: Input file validation and integrity checking
- **State Management**: Complex shared state between dependent jobs

### Performance Advantages
- **Independent Job Execution**: Labels and PRs can be restored in parallel
- **Early Completion**: Fast jobs complete without waiting for slow ones
- **Selective Operations**: Users can restore specific data types only
- **Resource Optimization**: Better CPU and I/O utilization

This implementation plan provides a comprehensive roadmap for decomposing the monolithic restore operation into focused, testable, and maintainable use cases with job-based parallel processing while significantly improving error handling, performance, and operational capabilities.