# Explicit Dependency Contracts Implementation Plan

**GitHub Data Project**  
**Plan Date:** September 17, 2025  
**Priority:** 2 (Major Violation - Should Fix)  
**Effort:** Medium  
**Status:** Pending Implementation

## Problem Statement

The GitHub Data project currently lacks explicit interfaces/protocols for dependency inversion, making testing more difficult and reducing architectural clarity. While dependency direction is excellent (pointing inward), concrete implementations are directly referenced rather than abstract contracts.

## Current State Analysis

### Major Dependencies Requiring Contracts

1. **GitHubService** (src/github/service.py)
   - Used by: operations/save.py, operations/restore.py
   - Methods: 25+ repository operations (labels, issues, comments, PRs, sub-issues)
   - Current coupling: Direct instantiation via create_github_service()

2. **Storage Operations** (src/storage/json_storage.py)
   - Used by: operations/save.py, operations/restore.py
   - Methods: save_json_data(), load_json_data()
   - Current coupling: Direct function imports

3. **Rate Limiter** (src/github/rate_limiter.py)
   - Used by: GitHubService
   - Methods: execute_with_retry()
   - Current coupling: Direct instantiation

4. **API Boundary** (src/github/boundary.py)
   - Used by: GitHubService
   - Methods: 20+ GitHub API operations
   - Current coupling: Direct instantiation

## Implementation Plan

### Phase 1: Core Service Interfaces (Week 1)

#### 1.1 Create Repository Service Protocol
```python
# File: src/github/protocols.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class RepositoryService(ABC):
    """Abstract interface for repository data operations."""
    
    @abstractmethod
    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all labels from repository."""
        pass
    
    @abstractmethod
    def get_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issues from repository."""
        pass
    
    # ... all other repository methods
```

#### 1.2 Create Storage Service Protocol
```python
# File: src/storage/protocols.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Type, TypeVar, Union, Sequence
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class StorageService(ABC):
    """Abstract interface for data persistence operations."""
    
    @abstractmethod
    def save_data(self, data: Union[Sequence[BaseModel], BaseModel], file_path: Path) -> None:
        """Save model data to storage."""
        pass
    
    @abstractmethod
    def load_data(self, file_path: Path, model_class: Type[T]) -> List[T]:
        """Load data from storage into model instances."""
        pass
```

#### 1.3 Update GitHubService to Implement Protocol
```python
# File: src/github/service.py
from .protocols import RepositoryService

class GitHubService(RepositoryService):
    # Existing implementation already compatible
    # No changes needed to method signatures
```

### Phase 2: Storage Service Abstraction (Week 1)

#### 2.1 Create JSON Storage Service Class
```python
# File: src/storage/json_storage_service.py
from .protocols import StorageService
from .json_storage import save_json_data, load_json_data

class JsonStorageService(StorageService):
    """JSON file storage implementation."""
    
    def save_data(self, data: Union[Sequence[BaseModel], BaseModel], file_path: Path) -> None:
        return save_json_data(data, file_path)
    
    def load_data(self, file_path: Path, model_class: Type[T]) -> List[T]:
        return load_json_data(file_path, model_class)
```

#### 2.2 Create Storage Factory
```python
# File: src/storage/__init__.py
from .protocols import StorageService
from .json_storage_service import JsonStorageService

def create_storage_service(storage_type: str = "json") -> StorageService:
    """Factory function for storage services."""
    if storage_type == "json":
        return JsonStorageService()
    raise ValueError(f"Unknown storage type: {storage_type}")
```

### Phase 3: Operations Layer Refactoring (Week 2)

#### 3.1 Update Save Operations
```python
# File: src/operations/save.py
from ..github.protocols import RepositoryService
from ..storage.protocols import StorageService

def save_repository_data(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    data_path: str
) -> None:
    """Save GitHub repository data using injected services."""
    # Existing logic remains the same
    # Services are now injected dependencies
```

#### 3.2 Update Restore Operations
```python
# File: src/operations/restore.py
from ..github.protocols import RepositoryService
from ..storage.protocols import StorageService

def restore_repository_data(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    data_path: str,
    # ... other parameters
) -> None:
    """Restore GitHub repository data using injected services."""
    # Existing logic remains the same
    # Services are now injected dependencies
```

#### 3.3 Update Main Entry Point
```python
# File: src/main.py
from .github import create_github_service
from .storage import create_storage_service

def main():
    # Create services using factories
    github_service = create_github_service(token)
    storage_service = create_storage_service("json")
    
    # Inject dependencies into operations
    if args.action == "save":
        save_repository_data(github_service, storage_service, ...)
    elif args.action == "restore":
        restore_repository_data(github_service, storage_service, ...)
```

### Phase 4: Testing Infrastructure (Week 2)

#### 4.1 Create Mock Services for Testing
```python
# File: tests/mocks/mock_github_service.py
from src.github.protocols import RepositoryService

class MockGitHubService(RepositoryService):
    """Mock GitHub service for testing."""
    
    def __init__(self, mock_data: Dict[str, Any]):
        self.mock_data = mock_data
    
    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        return self.mock_data.get("labels", [])
    
    # ... implement all abstract methods with mock data
```

#### 4.2 Create Mock Storage Service
```python
# File: tests/mocks/mock_storage_service.py
from src.storage.protocols import StorageService

class MockStorageService(StorageService):
    """In-memory storage service for testing."""
    
    def __init__(self):
        self.stored_data = {}
    
    def save_data(self, data, file_path):
        self.stored_data[str(file_path)] = data
    
    def load_data(self, file_path, model_class):
        # Return mock data as model instances
        pass
```

#### 4.3 Update Test Suite
```python
# File: tests/test_operations.py
from tests.mocks.mock_github_service import MockGitHubService
from tests.mocks.mock_storage_service import MockStorageService

def test_save_repository_data():
    # Arrange
    github_service = MockGitHubService(mock_data)
    storage_service = MockStorageService()
    
    # Act
    save_repository_data(github_service, storage_service, "repo", "path")
    
    # Assert
    assert storage_service.data_was_saved()
```

### Phase 5: Secondary Interface Abstractions (Week 3)

#### 5.1 Rate Limiter Protocol
```python
# File: src/github/protocols.py
class RateLimitHandler(ABC):
    """Abstract interface for rate limiting operations."""
    
    @abstractmethod
    def execute_with_retry(self, operation, github_client):
        """Execute operation with rate limiting and retry logic."""
        pass
```

#### 5.2 API Boundary Protocol  
```python
# File: src/github/protocols.py
class GitHubApiBoundary(ABC):
    """Abstract interface for GitHub API boundary operations."""
    
    @abstractmethod
    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get labels from GitHub API."""
        pass
    
    # ... all boundary methods
```

## Testing Strategy

### Unit Testing Benefits
- **Isolated Testing**: Each component can be tested independently
- **Fast Execution**: No network calls or file I/O in unit tests
- **Predictable Results**: Mock services provide controlled test data
- **Edge Case Coverage**: Easy to simulate error conditions

### Integration Testing Approach
- **Real Service Testing**: Continue using actual GitHub API for integration tests
- **Contract Testing**: Ensure mocks conform to real service behavior
- **End-to-End Validation**: Full workflow tests with real dependencies

## Migration Path

### Backward Compatibility
1. **Phase 1-2**: Keep existing functions as wrappers
2. **Phase 3**: Deprecate old function signatures
3. **Phase 4**: Remove deprecated functions in next major version

### Gradual Adoption
```python
# Backward compatible wrapper
def save_repository_data_legacy(github_token: str, repo_name: str, data_path: str) -> None:
    """Legacy function - deprecated, use dependency injection version."""
    github_service = create_github_service(github_token)
    storage_service = create_storage_service()
    save_repository_data(github_service, storage_service, repo_name, data_path)
```

## Benefits

### Architecture
- **Explicit Contracts**: Clear interfaces define expected behavior
- **Dependency Inversion**: High-level modules depend on abstractions
- **Framework Independence**: Business logic isolated from implementation details
- **Testability**: Easy mocking and stubbing for unit tests

### Development
- **Faster Tests**: Unit tests run without external dependencies
- **Better IDE Support**: Type hints and autocomplete for interfaces
- **Easier Debugging**: Clear separation between layers
- **Future Flexibility**: Easy to swap implementations

## Implementation Timeline

**Week 1**: Core protocols and GitHubService implementation  
**Week 2**: Operations refactoring and storage abstraction  
**Week 3**: Secondary abstractions and testing infrastructure  
**Week 4**: Documentation and cleanup

## Success Criteria

1. **All major dependencies have explicit interfaces**
2. **Unit tests can run without external dependencies**
3. **No concrete implementations imported in operations layer**
4. **Existing functionality remains unchanged**
5. **Test suite passes with both real and mock services**

## Next Steps

1. Create `src/github/protocols.py` with RepositoryService protocol
2. Create `src/storage/protocols.py` with StorageService protocol  
3. Update GitHubService to implement RepositoryService
4. Create JsonStorageService class
5. Update operations layer to use dependency injection

This plan transforms the identified "Major Violation" into a strength, improving testability and architectural clarity while maintaining all existing functionality.