# Save Operation Decomposition Implementation Plan

**Project:** GitHub Data  
**Plan Date:** September 17, 2025  
**Based On:** Use Case Breakdown Analysis  
**Target:** Decompose monolithic save operation into focused use cases

## Overview

This plan details the step-by-step implementation to refactor the current monolithic `save_repository_data_with_services()` function into a collection of focused, testable use cases following Clean Architecture principles.

## Current State Analysis

### Existing Implementation Structure
```
save_repository_data_with_services()
├── _collect_repository_data()
│   ├── _fetch_repository_labels()
│   ├── _fetch_repository_issues()
│   ├── _fetch_all_issue_comments()
│   ├── _fetch_repository_pull_requests()
│   ├── _fetch_all_pr_comments()
│   └── _fetch_repository_sub_issues()
├── _associate_sub_issues_with_parents()
└── _save_data_to_files()
    ├── _save_labels_to_file()
    ├── _save_issues_to_file()
    ├── _save_comments_to_file()
    ├── _save_pull_requests_to_file()
    ├── _save_pr_comments_to_file()
    └── _save_sub_issues_to_file()
```

### Problems Addressed
1. **Monolithic data collection** - All 6 data types collected sequentially
2. **All-or-nothing approach** - Single failure stops entire operation
3. **Poor testability** - Cannot test individual data type operations
4. **Mixed concerns** - Collection, association, and persistence mixed
5. **No selective operations** - Cannot save specific data types

## Implementation Architecture

### Use Case Hierarchy
```
SaveRepositoryUseCase (Orchestrator)
├── Collection Use Cases
│   ├── CollectLabelsUseCase
│   ├── CollectIssuesUseCase
│   ├── CollectCommentsUseCase
│   ├── CollectPullRequestsUseCase
│   ├── CollectPRCommentsUseCase
│   └── CollectSubIssuesUseCase
├── Processing Use Cases
│   ├── ValidateRepositoryAccessUseCase
│   └── AssociateSubIssuesUseCase
└── Persistence Use Cases
    ├── SaveLabelsUseCase
    ├── SaveIssuesUseCase
    ├── SaveCommentsUseCase
    ├── SavePullRequestsUseCase
    ├── SavePRCommentsUseCase
    └── SaveSubIssuesUseCase
```

## Implementation Phases

### Phase 1: Foundation Infrastructure

#### Step 1.1: Create Use Case Base Interface
**File:** `src/use_cases/__init__.py`
```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')
R = TypeVar('R')

class UseCase(ABC, Generic[T, R]):
    @abstractmethod
    def execute(self, request: T) -> R:
        pass
```

#### Step 1.2: Create Request/Response Objects
**File:** `src/use_cases/requests.py`
```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from ..models import Label, Issue, Comment, PullRequest, PullRequestComment, SubIssue

@dataclass
class SaveRepositoryRequest:
    repository_name: str
    output_path: str
    data_types: List[str] = None  # None means all types
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
class SaveLabelsRequest:
    labels: List[Label]
    output_path: str

@dataclass
class OperationResult:
    success: bool
    data_type: str
    items_processed: int = 0
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None
```

#### Step 1.3: Create Directory Structure
```
src/use_cases/
├── __init__.py              # Base UseCase interface
├── requests.py              # Request/Response objects
├── collection/              # Data collection use cases
│   ├── __init__.py
│   ├── collect_labels.py
│   ├── collect_issues.py
│   ├── collect_comments.py
│   ├── collect_pull_requests.py
│   ├── collect_pr_comments.py
│   └── collect_sub_issues.py
├── processing/              # Data processing use cases
│   ├── __init__.py
│   ├── validate_repository_access.py
│   └── associate_sub_issues.py
├── persistence/             # Data persistence use cases
│   ├── __init__.py
│   ├── save_labels.py
│   ├── save_issues.py
│   ├── save_comments.py
│   ├── save_pull_requests.py
│   ├── save_pr_comments.py
│   └── save_sub_issues.py
└── orchestration/           # Orchestrator use cases
    ├── __init__.py
    └── save_repository.py
```

### Phase 2: Collection Use Cases Implementation

#### Step 2.1: Implement CollectLabelsUseCase
**File:** `src/use_cases/collection/collect_labels.py`
```python
import time
from datetime import datetime
from typing import List

from ..requests import CollectLabelsRequest, CollectLabelsResponse
from .. import UseCase
from ...github.protocols import RepositoryService
from ...github import converters
from ...models import Label

class CollectLabelsUseCase(UseCase[CollectLabelsRequest, CollectLabelsResponse]):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: CollectLabelsRequest) -> CollectLabelsResponse:
        start_time = time.time()
        
        raw_labels = self._github_service.get_repository_labels(request.repository_name)
        labels = [converters.convert_to_label(label_dict) for label_dict in raw_labels]
        
        return CollectLabelsResponse(
            labels=labels,
            collection_timestamp=datetime.now(),
            items_collected=len(labels)
        )
```

#### Step 2.2: Implement Remaining Collection Use Cases
- `CollectIssuesUseCase` - Extract from `_fetch_repository_issues()`
- `CollectCommentsUseCase` - Extract from `_fetch_all_issue_comments()`
- `CollectPullRequestsUseCase` - Extract from `_fetch_repository_pull_requests()`
- `CollectPRCommentsUseCase` - Extract from `_fetch_all_pr_comments()`
- `CollectSubIssuesUseCase` - Extract from `_fetch_repository_sub_issues()`

**Pattern for each use case:**
1. Accept repository name in request
2. Use injected GitHub service for API calls
3. Convert raw API data to domain models
4. Return response with data, timestamp, and count
5. Include error handling with meaningful messages

### Phase 3: Persistence Use Cases Implementation

#### Step 3.1: Implement SaveLabelsUseCase
**File:** `src/use_cases/persistence/save_labels.py`
```python
import time
from pathlib import Path

from ..requests import SaveLabelsRequest, OperationResult
from .. import UseCase
from ...storage.protocols import StorageService

class SaveLabelsUseCase(UseCase[SaveLabelsRequest, OperationResult]):
    def __init__(self, storage_service: StorageService):
        self._storage_service = storage_service

    def execute(self, request: SaveLabelsRequest) -> OperationResult:
        start_time = time.time()
        
        try:
            output_dir = Path(request.output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            labels_file = output_dir / "labels.json"
            self._storage_service.save_data(request.labels, labels_file)
            
            execution_time = time.time() - start_time
            
            return OperationResult(
                success=True,
                data_type="labels",
                items_processed=len(request.labels),
                execution_time_seconds=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return OperationResult(
                success=False,
                data_type="labels",
                items_processed=0,
                error_message=str(e),
                execution_time_seconds=execution_time
            )
```

#### Step 3.2: Implement Remaining Persistence Use Cases
Follow same pattern for:
- `SaveIssuesUseCase`
- `SaveCommentsUseCase` 
- `SavePullRequestsUseCase`
- `SavePRCommentsUseCase`
- `SaveSubIssuesUseCase`

### Phase 4: Processing Use Cases Implementation

#### Step 4.1: Implement ValidateRepositoryAccessUseCase
**File:** `src/use_cases/processing/validate_repository_access.py`
```python
from ..requests import ValidateRepositoryAccessRequest, OperationResult
from .. import UseCase
from ...github.protocols import RepositoryService

class ValidateRepositoryAccessUseCase(UseCase[ValidateRepositoryAccessRequest, OperationResult]):
    def __init__(self, github_service: RepositoryService):
        self._github_service = github_service

    def execute(self, request: ValidateRepositoryAccessRequest) -> OperationResult:
        try:
            # Attempt to fetch basic repository info to validate access
            self._github_service.get_repository_info(request.repository_name)
            
            return OperationResult(
                success=True,
                data_type="repository_validation",
                items_processed=1
            )
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="repository_validation",
                error_message=f"Cannot access repository {request.repository_name}: {str(e)}"
            )
```

#### Step 4.2: Implement AssociateSubIssuesUseCase
Extract logic from `_associate_sub_issues_with_parents()` into standalone use case.

### Phase 5: Orchestrator Implementation

#### Step 5.1: Implement SaveRepositoryUseCase
**File:** `src/use_cases/orchestration/save_repository.py`
```python
from typing import List, Dict
from pathlib import Path
import concurrent.futures
from threading import ThreadPoolExecutor

from ..requests import SaveRepositoryRequest, OperationResult
from .. import UseCase
from ..collection import (
    CollectLabelsUseCase, CollectIssuesUseCase, CollectCommentsUseCase,
    CollectPullRequestsUseCase, CollectPRCommentsUseCase, CollectSubIssuesUseCase
)
from ..persistence import (
    SaveLabelsUseCase, SaveIssuesUseCase, SaveCommentsUseCase,
    SavePullRequestsUseCase, SavePRCommentsUseCase, SaveSubIssuesUseCase
)
from ..processing import ValidateRepositoryAccessUseCase, AssociateSubIssuesUseCase

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
        # ... assign all dependencies

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
        data_types = request.data_types or ["labels", "issues", "comments", "pull_requests", "pr_comments", "sub_issues"]
        
        # Step 3: Collect data (can be parallelized)
        collection_results = self._collect_data_parallel(request.repository_name, data_types)
        results.extend(collection_results)
        
        # Step 4: Process associations if needed
        if "sub_issues" in data_types and "issues" in data_types:
            # Handle sub-issue associations
            pass
        
        # Step 5: Save data (can be parallelized)
        persistence_results = self._save_data_parallel(request.output_path, collection_results)
        results.extend(persistence_results)
        
        return results

    def _collect_data_parallel(self, repo_name: str, data_types: List[str]) -> List[OperationResult]:
        """Collect multiple data types in parallel."""
        # Implementation with ThreadPoolExecutor for parallel collection
        pass

    def _save_data_parallel(self, output_path: str, collection_data: Dict) -> List[OperationResult]:
        """Save multiple data types in parallel."""
        # Implementation with ThreadPoolExecutor for parallel persistence
        pass
```

### Phase 6: Integration and Migration

#### Step 6.1: Update Main Entry Point
**File:** `src/operations/save.py`
```python
# Keep existing function as wrapper for backward compatibility
def save_repository_data_with_services(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    data_path: str,
) -> None:
    """Save GitHub repository data using injected services."""
    # Create use case instances
    save_use_case = _create_save_repository_use_case(github_service, storage_service)
    
    # Execute with new use case
    request = SaveRepositoryRequest(
        repository_name=repo_name,
        output_path=data_path
    )
    
    results = save_use_case.execute(request)
    
    # Handle errors (maintain existing behavior)
    failed_operations = [r for r in results if not r.success]
    if failed_operations:
        error_messages = [r.error_message for r in failed_operations if r.error_message]
        raise Exception(f"Save operation failed: {'; '.join(error_messages)}")

def _create_save_repository_use_case(
    github_service: RepositoryService, 
    storage_service: StorageService
) -> SaveRepositoryUseCase:
    """Factory function to create configured SaveRepositoryUseCase."""
    # Create all use case instances with proper dependency injection
    # Return configured orchestrator
    pass
```

#### Step 6.2: Update CLI Interface
Update CLI to support selective data type saving:
```bash
python -m github_data save owner/repo --data-types labels,issues
python -m github_data save owner/repo --exclude pull_requests,pr_comments
```

## Testing Strategy

### Unit Testing Approach

#### Individual Use Case Tests
```python
# tests/test_use_cases/test_collection/test_collect_labels.py
class TestCollectLabelsUseCase:
    def test_successful_collection(self, mock_github_service):
        # Test successful label collection
        pass
        
    def test_api_error_handling(self, mock_github_service):
        # Test API error scenarios
        pass
        
    def test_empty_repository(self, mock_github_service):
        # Test repository with no labels
        pass
```

#### Integration Tests
```python
# tests/test_use_cases/test_orchestration/test_save_repository.py
class TestSaveRepositoryUseCase:
    def test_full_save_operation(self, mock_services):
        # Test complete save workflow
        pass
        
    def test_partial_failure_handling(self, mock_services):
        # Test behavior when some operations fail
        pass
        
    def test_selective_data_type_saving(self, mock_services):
        # Test saving only specific data types
        pass
```

### Performance Testing
- Parallel collection benchmarks
- Memory usage monitoring for large repositories
- Error recovery time measurements

## Migration Timeline

### Week 1: Foundation
- [ ] Create use case base infrastructure
- [ ] Implement request/response objects
- [ ] Set up directory structure

### Week 2: Collection Use Cases
- [ ] Implement all 6 collection use cases
- [ ] Create comprehensive unit tests
- [ ] Add error handling and logging

### Week 3: Persistence Use Cases
- [ ] Implement all 6 persistence use cases
- [ ] Add file system error handling
- [ ] Create unit tests for persistence layer

### Week 4: Processing Use Cases
- [ ] Implement validation use case
- [ ] Implement sub-issue association use case
- [ ] Add integration tests

### Week 5: Orchestrator
- [ ] Implement SaveRepositoryUseCase
- [ ] Add parallel execution capabilities
- [ ] Implement error aggregation and reporting

### Week 6: Integration
- [ ] Update main entry point
- [ ] Maintain backward compatibility
- [ ] Update CLI for selective operations
- [ ] Run full integration test suite

## Success Metrics

### Code Quality Metrics
- **Function Size**: Average function size reduced from 50+ lines to 20-30 lines
- **Cyclomatic Complexity**: Reduced from 8+ to 3-4 per function
- **Test Coverage**: Achieve 95%+ test coverage for use cases
- **Single Responsibility**: Each use case handles exactly one data type or operation

### Performance Metrics
- **Parallel Collection**: 60-70% reduction in data collection time
- **Selective Operations**: Support for saving individual data types
- **Error Recovery**: Ability to resume from partial failures
- **Memory Usage**: 30-40% reduction through streaming operations

### Maintainability Metrics
- **New Feature Development**: 50% faster implementation of new data types
- **Bug Fix Isolation**: Issues contained to single use cases
- **Testing Speed**: Individual use case tests run in <100ms each

## Risk Mitigation

### Backward Compatibility
- Keep existing function signatures as wrappers
- Maintain identical error handling behavior
- Preserve file output formats and naming

### Performance Regression
- Benchmark current implementation before changes
- Monitor parallel execution overhead
- Implement performance tests in CI/CD

### Complex Migration
- Implement feature flags for gradual rollout
- Maintain both implementations during transition
- Create comprehensive integration tests

## Future Enhancements

### Phase 2 Extensions
1. **Configuration-Driven Operations**: YAML/JSON configuration for save operations
2. **Progress Reporting**: Real-time progress updates for large repositories
3. **Retry Mechanisms**: Automatic retry with exponential backoff
4. **Data Validation**: Schema validation before saving
5. **Compression**: Optional data compression for large datasets

### Advanced Features
- **Incremental Backups**: Save only changed data since last backup
- **Multi-Repository Operations**: Batch operations across multiple repositories
- **Cloud Storage Support**: Direct save to S3, Google Cloud Storage, etc.
- **Notification System**: Webhook notifications for operation completion

This implementation plan provides a comprehensive roadmap for decomposing the monolithic save operation into focused, testable, and maintainable use cases while preserving existing functionality and improving system capabilities.