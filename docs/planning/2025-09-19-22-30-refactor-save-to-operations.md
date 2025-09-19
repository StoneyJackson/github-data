# Refactor Plan: Move src/use_cases/save to src/operations/save

**Date:** 2025-09-19-22-30  
**Objective:** Refactor the save functionality from `src/use_cases/save` to `src/operations/save` following the same architecture pattern as `operations/restore`. **No backward compatibility required - clean migration.**

## Current Architecture Analysis

### Current use_cases/save Structure

```
src/use_cases/save/
├── __init__.py                           # Empty save operation use cases comment
├── collection/                           # Data collection from GitHub API
│   ├── __init__.py
│   ├── collect_labels.py                # CollectLabelsUseCase
│   ├── collect_issues.py                # CollectIssuesUseCase  
│   ├── collect_comments.py              # CollectCommentsUseCase
│   ├── collect_pull_requests.py         # CollectPullRequestsUseCase
│   ├── collect_pr_comments.py           # CollectPRCommentsUseCase
│   └── collect_sub_issues.py            # CollectSubIssuesUseCase
├── persistence/                          # Data persistence to JSON files
│   ├── __init__.py
│   ├── save_labels.py                   # SaveLabelsUseCase
│   ├── save_issues.py                   # SaveIssuesUseCase
│   ├── save_comments.py                 # SaveCommentsUseCase
│   ├── save_pull_requests.py            # SavePullRequestsUseCase
│   ├── save_pr_comments.py              # SavePRCommentsUseCase
│   └── save_sub_issues.py               # SaveSubIssuesUseCase
├── processing/                           # Data processing and transformation
│   ├── __init__.py
│   └── associate_sub_issues.py          # AssociateSubIssuesUseCase
└── orchestration/                        # Job orchestration and execution
    ├── __init__.py
    └── save_repository.py               # SaveRepositoryUseCase + Job classes
```

### Target operations/restore Structure (Reference)

```
src/operations/restore/
├── __init__.py                          # Exports restore_repository_data_with_strategy_pattern
├── restore.py                           # Main restore function with strategy registration
├── orchestrator.py                     # StrategyBasedRestoreOrchestrator
└── strategy.py                          # RestoreEntityStrategy + RestoreConflictStrategy base classes
```

### Key Differences to Address

1. **Architecture Pattern:**
   - Current save: UseCase-based architecture with job orchestration
   - Target restore: Strategy pattern with dependency resolution
   - Current save has 4 distinct layers (collection, processing, persistence, orchestration)
   - Target restore has unified strategy-based approach

2. **Orchestration Approach:**
   - Current save: Custom job orchestration with ThreadPoolExecutor and dependency tracking
   - Target restore: Strategy-based orchestrator with entity dependencies

3. **Entity Handling:**
   - Current save: Separate UseCase classes for each step (collect → process → save)
   - Target restore: Single strategy per entity type handling full workflow

## Refactoring Plan

### Phase 1: Create New Operations Structure (Direct Migration)

#### Step 1.1: Create base strategy interfaces
**File:** `src/operations/save/strategy.py`

```python
"""Base strategy interfaces for entity save operations."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class SaveEntityStrategy(ABC):
    """Base strategy for entity save operations."""

    @abstractmethod
    def get_entity_name(self) -> str:
        """Return the entity type name (e.g., 'labels', 'issues')."""
        pass

    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        pass

    @abstractmethod
    def collect_data(
        self, github_service: "RepositoryService", repo_name: str
    ) -> List[Any]:
        """Collect entity data from GitHub API."""
        pass

    @abstractmethod
    def process_data(
        self, entities: List[Any], context: Dict[str, Any]
    ) -> List[Any]:
        """Process and transform entity data."""
        pass

    @abstractmethod
    def save_data(
        self,
        entities: List[Any],
        output_path: str,
        storage_service: "StorageService",
    ) -> Dict[str, Any]:
        """Save entity data to storage."""
        pass
```

#### Step 1.2: Create strategy-based orchestrator
**File:** `src/operations/save/orchestrator.py`

Copy and adapt the dependency resolution logic from `restore/orchestrator.py`:

```python
"""Strategy-based save orchestrator."""

from typing import List, Dict, Any, TYPE_CHECKING
from .strategy import SaveEntityStrategy

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService


class StrategyBasedSaveOrchestrator:
    """Orchestrator that executes save operations using registered strategies."""

    def __init__(
        self, github_service: "RepositoryService", storage_service: "StorageService"
    ) -> None:
        self._github_service = github_service
        self._storage_service = storage_service
        self._strategies: Dict[str, SaveEntityStrategy] = {}
        self._context: Dict[str, Any] = {}

    def register_strategy(self, strategy: SaveEntityStrategy) -> None:
        """Register an entity save strategy."""
        self._strategies[strategy.get_entity_name()] = strategy

    def execute_save(
        self, repo_name: str, output_path: str, requested_entities: List[str]
    ) -> List[Dict[str, Any]]:
        """Execute save operation using registered strategies."""
        results = []

        # Resolve dependency order - copy logic from restore orchestrator
        execution_order = self._resolve_execution_order(requested_entities)

        # Execute strategies in dependency order
        for entity_name in execution_order:
            if entity_name in self._strategies:
                result = self._execute_strategy(entity_name, repo_name, output_path)
                results.append(result)

        return results

    def _resolve_execution_order(self, requested_entities: List[str]) -> List[str]:
        """Resolve execution order based on dependencies - copied from restore."""
        resolved = []
        remaining = set(requested_entities)

        while remaining:
            ready = []
            for entity in remaining:
                if entity in self._strategies:
                    deps = self._strategies[entity].get_dependencies()
                    if all(dep in resolved or dep not in requested_entities for dep in deps):
                        ready.append(entity)

            if not ready:
                raise ValueError(f"Circular dependency detected in: {remaining}")

            for entity in ready:
                resolved.append(entity)
                remaining.remove(entity)

        return resolved

    def _execute_strategy(
        self, entity_name: str, repo_name: str, output_path: str
    ) -> Dict[str, Any]:
        """Execute a single entity save strategy."""
        strategy = self._strategies[entity_name]

        try:
            # Collect data
            entities = strategy.collect_data(self._github_service, repo_name)
            print(f"Collected {len(entities)} {entity_name}")

            # Process data
            processed_entities = strategy.process_data(entities, self._context)

            # Save data
            result = strategy.save_data(
                processed_entities, output_path, self._storage_service
            )

            return {
                "entity_name": entity_name,
                "success": True,
                "entities_processed": len(entities),
                "entities_saved": len(processed_entities),
                **result,
            }

        except Exception as e:
            return {
                "entity_name": entity_name,
                "success": False,
                "error": str(e),
                "entities_processed": 0,
                "entities_saved": 0,
            }
```

#### Step 1.3: Create main save function
**File:** `src/operations/save/save.py`

```python
"""
Save actions for GitHub repository data.

Implements the save functionality that collects GitHub data and
saves it to JSON files for backup purposes.
"""

from typing import List
from src.github.protocols import RepositoryService
from src.storage.protocols import StorageService


def save_repository_data_with_strategy_pattern(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    output_path: str,
    include_prs: bool = True,
    include_sub_issues: bool = True,
    data_types: List[str] = None,
) -> None:
    """Save using strategy pattern approach."""

    # Create orchestrator
    from .orchestrator import StrategyBasedSaveOrchestrator

    orchestrator = StrategyBasedSaveOrchestrator(github_service, storage_service)

    # Register strategies directly in operations (not entities)
    from .strategies.labels_strategy import LabelsSaveStrategy
    from .strategies.issues_strategy import IssuesSaveStrategy
    from .strategies.comments_strategy import CommentsSaveStrategy

    # Register entity strategies
    orchestrator.register_strategy(LabelsSaveStrategy())
    orchestrator.register_strategy(IssuesSaveStrategy())
    orchestrator.register_strategy(CommentsSaveStrategy())

    # Add PR strategies if requested
    if include_prs:
        from .strategies.pull_requests_strategy import PullRequestsSaveStrategy
        from .strategies.pr_comments_strategy import PullRequestCommentsSaveStrategy

        orchestrator.register_strategy(PullRequestsSaveStrategy())
        orchestrator.register_strategy(PullRequestCommentsSaveStrategy())

    # Add sub-issues strategy if requested
    if include_sub_issues:
        from .strategies.sub_issues_strategy import SubIssuesSaveStrategy

        orchestrator.register_strategy(SubIssuesSaveStrategy())

    # Determine entities to save
    if data_types is None:
        requested_entities = ["labels", "issues", "comments"]
        if include_prs:
            requested_entities.extend(["pull_requests", "pr_comments"])
        if include_sub_issues:
            requested_entities.append("sub_issues")
    else:
        requested_entities = data_types

    # Execute save operation
    results = orchestrator.execute_save(repo_name, output_path, requested_entities)

    # Handle errors
    failed_operations = [r for r in results if not r["success"]]
    if failed_operations:
        error_messages = [r["error"] for r in failed_operations if r.get("error")]
        raise Exception(f"Save operation failed: {'; '.join(error_messages)}")
```

#### Step 1.4: Create module exports
**File:** `src/operations/save/__init__.py`

```python
"""Save operations module."""

from .save import save_repository_data_with_strategy_pattern

__all__ = ["save_repository_data_with_strategy_pattern"]
```

### Phase 2: Extract and Convert UseCase Logic to Strategies

#### Step 2.1: Create strategy implementations directory
Create `src/operations/save/strategies/` to house all strategy implementations.

#### Step 2.2: Convert Labels UseCase to Strategy
**File:** `src/operations/save/strategies/labels_strategy.py`

Extract logic from:
- `src/use_cases/save/collection/collect_labels.py`
- `src/use_cases/save/persistence/save_labels.py`

#### Step 2.3: Convert Issues UseCase to Strategy  
**File:** `src/operations/save/strategies/issues_strategy.py`

Extract logic from:
- `src/use_cases/save/collection/collect_issues.py`  
- `src/use_cases/save/persistence/save_issues.py`

#### Step 2.4: Convert Sub-Issues UseCase to Strategy
**File:** `src/operations/save/strategies/sub_issues_strategy.py`

Extract logic from:
- `src/use_cases/save/collection/collect_sub_issues.py`
- `src/use_cases/save/processing/associate_sub_issues.py`
- `src/use_cases/save/persistence/save_sub_issues.py`

#### Step 2.5: Convert remaining entities (Comments, PRs, PR Comments)

### Phase 3: Direct Migration

#### Step 3.1: Update main.py immediately
Replace current save operation call with new strategy-based approach.

#### Step 3.2: Update all import statements
- Find all references to `src.use_cases.save` 
- Replace with `src.operations.save`

#### Step 3.3: Move and update tests
Move tests from `tests/use_cases/save/` to `tests/operations/save/` and update to test strategy pattern.

### Phase 4: Complete Removal

#### Step 4.1: Delete old use_cases/save module
Remove entire `src/use_cases/save/` directory and all related files.

#### Step 4.2: Clean up remaining imports
Remove any remaining references to old use_cases/save module.

## Benefits of This Refactoring

1. **Architectural Consistency:** Aligns save operations with restore operations pattern
2. **Simplified Orchestration:** Removes complex job-based orchestration in favor of strategy pattern  
3. **Cleaner Dependencies:** Clear entity dependency resolution using proven restore pattern
4. **Better Testability:** Strategy pattern enables easier unit testing
5. **Reduced Complexity:** Consolidates 4-layer architecture into strategy-based approach
6. **Maintainability:** Consistent patterns across save/restore operations
7. **Code Deduplication:** Eliminates parallel orchestration logic

## Implementation Strategy

### Direct Migration Approach
- **No Backward Compatibility:** Clean break from old architecture
- **Single Implementation:** No parallel code paths to maintain
- **Immediate Benefits:** Full strategy pattern advantages from day one
- **Cleaner Codebase:** No legacy compatibility code cluttering the implementation

### Key Implementation Steps
1. **Create new structure** - Build complete strategy-based save operations
2. **Extract logic directly** - Move UseCase logic into strategy implementations  
3. **Update all references** - Change imports from use_cases to operations
4. **Delete old code** - Remove entire use_cases/save module completely
5. **Update tests** - Migrate test structure to match new architecture

### Risk Mitigation
- **Comprehensive Testing:** Run full test suite before and after migration
- **Incremental Validation:** Test each strategy implementation independently
- **Integration Testing:** Verify end-to-end save workflow functionality

## Implementation Timeline

1. **Day 1-2:** Phase 1 - Create base strategy infrastructure
2. **Day 3-4:** Phase 2 - Extract and convert UseCase logic to strategies  
3. **Day 5:** Phase 3 - Direct migration (update imports, main.py, tests)
4. **Day 6:** Phase 4 - Complete removal of old code

This aggressive timeline is possible because we're not maintaining backward compatibility.