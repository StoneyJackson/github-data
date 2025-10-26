# Restore Operation Decomposition Implementation Plan

**Project:** GitHub Data  
**Plan Date:** September 17, 2025  
**Based On:** Use Case Breakdown Analysis  
**Target:** Decompose monolithic restore operation into focused use cases

## Overview

This plan details the step-by-step implementation to refactor the current monolithic 700+ line `restore_repository_data_with_services()` function into a collection of focused, testable use cases following Clean Architecture principles.

## Current State Analysis

### Existing Implementation Structure
```
restore_repository_data_with_services()  # 700+ lines with 7 parameters
├── _validate_data_files_exist()
├── _restore_labels()                     # 120+ lines with 5 strategies
│   ├── _handle_fail_if_existing()
│   ├── _handle_fail_if_conflict()
│   ├── _handle_delete_all()
│   ├── _handle_overwrite()
│   └── _handle_skip()
├── _restore_issues()
├── _restore_comments()
├── _restore_pull_requests()              # Optional
├── _restore_pr_comments()                # Optional 
└── _restore_sub_issues()                 # Optional with complex hierarchy
    └── _organize_sub_issues_by_depth()   # Complex algorithm (60+ lines)
```

### Problems Addressed
1. **Monolithic orchestrator** - Single 700+ line function with multiple responsibilities
2. **Complex parameter passing** - 7 parameters with optional behavior flags
3. **Strategy pattern violation** - Label conflict strategies embedded in main function
4. **Tight coupling** - Sequential dependencies with shared state
5. **Limited error recovery** - Cannot resume from specific failure points
6. **All-or-nothing approach** - Cannot restore specific data types independently

## Implementation Architecture

### Use Case Hierarchy
```
RestoreRepositoryUseCase (Orchestrator)
├── Validation Use Cases
│   ├── ValidateRestoreDataUseCase
│   └── ValidateRepositoryAccessUseCase
├── Data Loading Use Cases
│   ├── LoadLabelsUseCase
│   ├── LoadIssuesUseCase
│   ├── LoadCommentsUseCase
│   ├── LoadPullRequestsUseCase
│   ├── LoadPRCommentsUseCase
│   └── LoadSubIssuesUseCase
├── Restoration Use Cases
│   ├── RestoreLabelsUseCase
│   ├── RestoreIssuesUseCase
│   ├── RestoreCommentsUseCase
│   ├── RestorePullRequestsUseCase
│   ├── RestorePRCommentsUseCase
│   └── RestoreSubIssuesUseCase
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

## Implementation Phases

### Phase 1: Foundation Infrastructure

#### Step 1.1: Extend Use Case Base Interface
**File:** `src/use_cases/requests.py` (extend existing)
```python
@dataclass
class RestoreRepositoryRequest:
    repository_name: str
    input_path: str
    data_types: List[str] = None  # None means all required types
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
class LabelConflictDetectionRequest:
    existing_labels: List[Label]
    labels_to_restore: List[Label]

@dataclass
class LabelConflictDetectionResponse:
    has_conflicts: bool
    conflicting_names: List[str]
    conflict_details: Dict[str, str]  # name -> conflict type

@dataclass
class SubIssueHierarchyRequest:
    sub_issues: List[SubIssue]
    issue_number_mapping: Dict[int, int]

@dataclass
class SubIssueHierarchyResponse:
    sub_issues_by_depth: Dict[int, List[SubIssue]]
    max_depth: int
    circular_dependencies: List[str]
```

#### Step 1.2: Create Directory Structure
```
src/use_cases/
├── validation/              # Data and access validation
│   ├── __init__.py
│   ├── validate_restore_data.py
│   └── validate_repository_access.py
├── loading/                 # Data loading from files
│   ├── __init__.py
│   ├── load_labels.py
│   ├── load_issues.py
│   ├── load_comments.py
│   ├── load_pull_requests.py
│   ├── load_pr_comments.py
│   └── load_sub_issues.py
├── restoration/             # Data restoration to GitHub
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
from typing import Dict, List, Set

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

from ..requests import ApplyLabelStrategyRequest, OperationResult  
from .. import UseCase
from ...models import Label

class FailIfExistingStrategyUseCase(UseCase[ApplyLabelStrategyRequest, OperationResult]):
    def execute(self, request: ApplyLabelStrategyRequest) -> OperationResult:
        if request.existing_labels:
            return OperationResult(
                success=False,
                data_type="label_strategy",
                error_message=(
                    f"Repository has {len(request.existing_labels)} existing labels. "
                    f"Change strategy to allow restoration with existing labels."
                )
            )
        
        return OperationResult(
            success=True,
            data_type="label_strategy",
            items_processed=0
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
from typing import List

from ..requests import RestoreLabelsRequest, OperationResult
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
        conflict_detector: DetectLabelConflictsUseCase,
        fail_if_existing: FailIfExistingStrategyUseCase,
        fail_if_conflict: FailIfConflictStrategyUseCase,
        delete_all: DeleteAllStrategyUseCase,
        overwrite: OverwriteStrategyUseCase,
        skip: SkipStrategyUseCase
    ):
        self._github_service = github_service
        self._conflict_detector = conflict_detector
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
            raw_existing = self._github_service.get_repository_labels(request.repository_name)
            existing_labels = [Label.from_dict(label_dict) for label_dict in raw_existing]
            
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
                return strategy_result
            
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
Focus on extracting the complex issue creation logic with number mapping:

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
```

### Phase 6: Sub-Issue Management Use Cases

#### Step 6.1: Implement ValidateSubIssueDataUseCase
**File:** `src/use_cases/sub_issue_management/validate_sub_issue_data.py`
```python
from typing import Dict

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

#### Step 6.2: Implement DetectCircularDependenciesUseCase
Extract and improve the circular dependency detection algorithm:

```python
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

#### Step 6.3: Implement Remaining Sub-Issue Use Cases
- `CalculateHierarchyDepthUseCase` - Extract depth calculation algorithm
- `OrganizeByDepthUseCase` - Extract dependency ordering logic  
- `CreateSubIssueRelationshipUseCase` - Individual relationship creation

### Phase 7: Orchestrator Implementation

#### Step 7.1: Implement RestoreRepositoryUseCase
**File:** `src/use_cases/orchestration/restore_repository.py`
```python
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

from ..requests import RestoreRepositoryRequest, OperationResult
from .. import UseCase
from ..validation import ValidateRestoreDataUseCase
from ..loading import (
    LoadLabelsUseCase, LoadIssuesUseCase, LoadCommentsUseCase,
    LoadPullRequestsUseCase, LoadPRCommentsUseCase, LoadSubIssuesUseCase
)
from ..restoration import (
    RestoreLabelsUseCase, RestoreIssuesUseCase, RestoreCommentsUseCase,
    RestorePullRequestsUseCase, RestorePRCommentsUseCase, RestoreSubIssuesUseCase
)

class RestoreRepositoryUseCase(UseCase[RestoreRepositoryRequest, List[OperationResult]]):
    def __init__(self, **use_cases):
        # Inject all required use cases
        self._validate_data = use_cases['validate_data']
        self._load_labels = use_cases['load_labels']
        # ... other use cases
        
        # Thread-safe storage for shared data
        self._shared_data = threading.local()

    def execute(self, request: RestoreRepositoryRequest) -> List[OperationResult]:
        results = []
        
        # Phase 1: Validation
        validation_result = self._validate_data.execute(
            ValidateRestoreDataRequest.from_restore_request(request)
        )
        results.append(validation_result)
        
        if not validation_result.success:
            return results
        
        # Phase 2: Data Loading (can be parallelized)
        loading_results, loaded_data = self._load_data_parallel(request)
        results.extend(loading_results)
        
        if any(not result.success for result in loading_results):
            return results
        
        # Phase 3: Sequential Restoration (dependencies require order)
        restoration_results = self._restore_data_sequential(request, loaded_data)
        results.extend(restoration_results)
        
        return results

    def _load_data_parallel(self, request: RestoreRepositoryRequest) -> tuple[List[OperationResult], Dict]:
        """Load all required data files in parallel."""
        data_types = request.data_types or self._get_default_data_types(request)
        loaded_data = {}
        results = []
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {}
            
            if "labels" in data_types:
                futures["labels"] = executor.submit(
                    self._load_labels.execute,
                    LoadLabelsRequest(request.input_path)
                )
            # ... submit other loading tasks
            
            # Collect results
            for data_type, future in futures.items():
                try:
                    response = future.result(timeout=30)
                    loaded_data[data_type] = response
                    results.append(OperationResult(
                        success=True,
                        data_type=f"load_{data_type}",
                        items_processed=getattr(response, 'items_loaded', 0)
                    ))
                except Exception as e:
                    results.append(OperationResult(
                        success=False,
                        data_type=f"load_{data_type}",
                        error_message=str(e)
                    ))
        
        return results, loaded_data

    def _restore_data_sequential(self, request: RestoreRepositoryRequest, loaded_data: Dict) -> List[OperationResult]:
        """Restore data in proper dependency order."""
        results = []
        
        # Step 1: Restore labels (no dependencies)
        if "labels" in loaded_data:
            result = self._restore_labels.execute(RestoreLabelsRequest(
                repository_name=request.repository_name,
                labels=loaded_data["labels"].labels,
                conflict_strategy=request.label_conflict_strategy
            ))
            results.append(result)
            
            if not result.success:
                return results
        
        # Step 2: Restore issues (depends on labels)
        issue_number_mapping = {}
        if "issues" in loaded_data:
            result = self._restore_issues.execute(RestoreIssuesRequest(
                repository_name=request.repository_name,
                issues=loaded_data["issues"].issues,
                include_original_metadata=request.include_original_metadata
            ))
            results.append(result)
            
            if result.success:
                issue_number_mapping = result.issue_number_mapping
            else:
                return results
        
        # Step 3: Restore comments (depends on issues)
        if "comments" in loaded_data and issue_number_mapping:
            result = self._restore_comments.execute(RestoreCommentsRequest(
                repository_name=request.repository_name,
                comments=loaded_data["comments"].comments,
                issue_number_mapping=issue_number_mapping,
                include_original_metadata=request.include_original_metadata
            ))
            results.append(result)
        
        # Step 4: Restore PRs and PR comments (if requested)
        pr_number_mapping = {}
        if request.include_prs and "pull_requests" in loaded_data:
            # ... handle PR restoration
            pass
        
        # Step 5: Restore sub-issues (depends on all issues being created)
        if request.include_sub_issues and "sub_issues" in loaded_data and issue_number_mapping:
            result = self._restore_sub_issues.execute(RestoreSubIssuesRequest(
                repository_name=request.repository_name,
                sub_issues=loaded_data["sub_issues"].sub_issues,
                issue_number_mapping=issue_number_mapping
            ))
            results.append(result)
        
        return results

    def _get_default_data_types(self, request: RestoreRepositoryRequest) -> List[str]:
        """Get default data types based on request flags."""
        types = ["labels", "issues", "comments"]
        
        if request.include_prs:
            types.extend(["pull_requests", "pr_comments"])
        
        if request.include_sub_issues:
            types.append("sub_issues")
        
        return types
```

### Phase 8: Integration and Migration

#### Step 8.1: Update Main Entry Point
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
    # Create all use case dependencies
    # Return configured orchestrator
    pass
```

#### Step 8.2: Update CLI Interface
Add selective restore capabilities:
```bash
python -m github_data restore owner/repo --data-types labels,issues
python -m github_data restore owner/repo --exclude pull_requests
python -m github_data restore owner/repo --resume-from issues  # Resume from failure
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
        
    def test_resume_from_failure(self, mock_services):
        # Test resuming from specific failure points
        pass
        
    def test_parallel_loading_performance(self, mock_services):
        # Test concurrent data loading
        pass
```

### Performance Testing
- Parallel loading benchmarks vs sequential
- Memory usage monitoring for large datasets
- Sub-issue hierarchy calculation performance
- Error recovery and retry timing

## Migration Timeline

### Week 1: Foundation and Validation
- [ ] Create use case infrastructure extensions
- [ ] Implement validation use cases
- [ ] Create comprehensive unit tests
- [ ] Set up directory structure

### Week 2: Data Loading Use Cases
- [ ] Implement all 6 loading use cases
- [ ] Add error handling for file system issues
- [ ] Create performance benchmarks
- [ ] Add parallel loading capabilities

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

### Week 6: Advanced Restoration (PRs and Sub-Issues)
- [ ] Implement PR restoration use cases
- [ ] Implement sub-issue relationship creation
- [ ] Add branch validation for PRs
- [ ] Test complex restoration scenarios

### Week 7: Orchestrator Implementation
- [ ] Implement RestoreRepositoryUseCase
- [ ] Add parallel loading capabilities
- [ ] Implement error aggregation and reporting
- [ ] Add selective restoration logic

### Week 8: Integration and Migration
- [ ] Update main entry point with backward compatibility
- [ ] Add CLI selective restore capabilities  
- [ ] Run full integration test suite
- [ ] Performance regression testing

## Success Metrics

### Code Quality Metrics
- **Function Size**: Main orchestrator reduced from 700+ lines to 50-80 lines
- **Strategy Implementation**: Clean separation of 5 conflict resolution strategies
- **Circular Dependencies**: Robust detection and handling of hierarchy issues
- **Test Coverage**: 95%+ coverage for all use cases
- **Cyclomatic Complexity**: Reduced from 15+ to 3-5 per function

### Performance Metrics  
- **Parallel Loading**: 40-50% reduction in data loading time
- **Selective Restoration**: Support for individual data type restoration
- **Resume Capability**: Ability to restart from any failed step
- **Error Isolation**: Failures contained to specific use cases

### Maintainability Metrics
- **Strategy Extensibility**: New conflict strategies added without code modification
- **New Data Type Support**: 70% faster implementation of new data types
- **Bug Fix Isolation**: Issues contained to single use cases
- **Testing Speed**: Individual use case tests run in <50ms each

### Operational Metrics
- **Resume Operations**: Users can restart from specific failure points
- **Selective Operations**: Restore only needed data types
- **Error Reporting**: Detailed error reporting per operation
- **Progress Tracking**: Real-time progress updates

## Risk Mitigation

### Backward Compatibility
- Keep existing function signatures unchanged
- Maintain identical error messages and behavior
- Preserve output formats and progress reporting
- Ensure CLI compatibility

### Complex State Management
- Thread-safe shared data storage
- Proper cleanup of partial operations
- Transaction-like behavior for critical sections
- Comprehensive rollback capabilities

### Performance Regression
- Benchmark current implementation performance
- Monitor parallel execution overhead
- Test memory usage with large datasets
- Implement performance regression tests

### Migration Complexity
- Implement feature flags for gradual rollout
- Maintain both implementations during transition
- Create comprehensive migration tests
- Document rollback procedures

## Future Enhancements

### Phase 2 Extensions
1. **Resume/Retry Mechanisms**: Smart restart from failure points
2. **Configuration Management**: YAML/JSON-driven restore configuration
3. **Advanced Validation**: Schema validation and data integrity checks
4. **Progress Reporting**: Real-time progress with ETA calculations
5. **Dry-Run Mode**: Preview restoration without making changes

### Advanced Features
- **Incremental Restore**: Only restore changes since last backup
- **Multi-Repository Restore**: Batch restore across multiple repositories
- **Cloud Integration**: Direct restore from cloud storage (S3, GCS)
- **Webhook Integration**: Notifications for restore completion/failure
- **Audit Logging**: Comprehensive logging of all restore operations

This implementation plan provides a comprehensive roadmap for decomposing the monolithic restore operation into focused, testable, and maintainable use cases while significantly improving error handling, performance, and operational capabilities.