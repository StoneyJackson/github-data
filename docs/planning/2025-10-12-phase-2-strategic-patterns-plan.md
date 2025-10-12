# Phase 2 Refactoring Implementation Plan

**Date:** 2025-10-12  
**Focus:** Strategic Patterns - Medium Complexity, High Impact  
**Duration:** Week 2  
**Based on:** [Code Duplication Analysis](2025-10-12-operations-code-duplication-analysis.md) and [Phase 1 Results](2025-10-12-phase-1-completion-report.md)

## Phase 2 Overview

Phase 2 targets the next highest-impact refactoring opportunities, building on Phase 1's successful template method foundation. This phase focuses on more complex abstractions that require careful design to maintain entity-specific flexibility while eliminating strategic code duplication.

### Selected Refactorings

1. **Generic Selective Filtering Mixin** - 90 line reduction
2. **Parent-Child Entity Coupling Framework** - 80 line reduction  
3. **Conflict Strategy Factory Pattern** - 100 line reduction

### Why These Next?

- **Strategic Impact**: 270 lines eliminated (45% of remaining duplication)
- **Architectural Value**: Establishes patterns for complex entity relationships
- **Developer Experience**: Significantly simplifies new strategy implementation
- **Phase 1 Foundation**: Leverages proven template method patterns

## Refactoring 1: Generic Selective Filtering Mixin

### Current State Analysis

**Location**: `IssuesSaveStrategy.process_data()` and `PullRequestsSaveStrategy.process_data()`  
**Files Affected**:
- `src/operations/save/strategies/issues_strategy.py:44-82`
- `src/operations/save/strategies/pull_requests_strategy.py:46-88`

**Duplication Pattern**:
```python
# Nearly identical pattern in both strategies
def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
    if isinstance(self._include_{entity}, bool):
        if self._include_{entity}:
            return entities  # Include all
        else:
            return []  # Skip all
    else:
        # Selective filtering: 30+ lines of identical logic
        filtered_entities = []
        for entity in entities:
            if self._should_include_{entity}(entity, self._include_{entity}):
                filtered_entities.append(entity)

        # Logging and validation: 15+ lines identical
        found_numbers = {entity.number for entity in filtered_entities}
        missing_numbers = self._include_{entity} - found_numbers
        if missing_numbers:
            print(f"Warning: {Entity} not found in repository: {sorted(missing_numbers)}")

        print(f"Selected {len(filtered_entities)} {entity} from {len(entities)} total")
        return filtered_entities
```

### Implementation Steps

#### Step 1: Design Generic Selective Filtering Mixin
```python
# In src/operations/save/mixins/selective_filtering.py
from abc import ABC, abstractmethod
from typing import List, Any, Union, Set, Dict

class SelectiveFilteringMixin(ABC):
    """Mixin providing generic selective filtering capabilities."""
    
    def __init__(self, include_spec: Union[bool, Set[int]], *args, **kwargs):
        """Initialize with filtering specification."""
        super().__init__(*args, **kwargs)
        self._include_spec = include_spec
    
    def apply_selective_filtering(
        self, entities: List[Any], context: Dict[str, Any]
    ) -> List[Any]:
        """Apply selective filtering based on include specification."""
        if isinstance(self._include_spec, bool):
            return self._handle_boolean_filtering(entities)
        else:
            return self._handle_selective_filtering(entities)
    
    def _handle_boolean_filtering(self, entities: List[Any]) -> List[Any]:
        """Handle boolean include/exclude all logic."""
        return entities if self._include_spec else []
    
    def _handle_selective_filtering(self, entities: List[Any]) -> List[Any]:
        """Handle selective filtering by entity numbers."""
        entity_name = self.get_entity_name()
        
        # Filter entities
        filtered_entities = []
        for entity in entities:
            if self._should_include_entity(entity, self._include_spec):
                filtered_entities.append(entity)
        
        # Report results
        self._report_filtering_results(
            filtered_entities, entities, self._include_spec, entity_name
        )
        
        return filtered_entities
    
    def _should_include_entity(self, entity: Any, include_spec: Set[int]) -> bool:
        """Determine if entity should be included based on specification."""
        return hasattr(entity, "number") and entity.number in include_spec
    
    def _report_filtering_results(
        self, 
        filtered_entities: List[Any], 
        all_entities: List[Any], 
        include_spec: Set[int], 
        entity_name: str
    ) -> None:
        """Report filtering results with missing number warnings."""
        found_numbers = {entity.number for entity in filtered_entities}
        missing_numbers = include_spec - found_numbers
        
        if missing_numbers:
            entity_display = entity_name.replace('_', ' ').title()
            print(
                f"Warning: {entity_display} not found in repository: "
                f"{sorted(missing_numbers)}"
            )
        
        print(
            f"Selected {len(filtered_entities)} {entity_name} from "
            f"{len(all_entities)} total"
        )
    
    @abstractmethod
    def get_entity_name(self) -> str:
        """Return the entity name for logging and reporting."""
        pass
```

#### Step 2: Update Issues Strategy
```python
# In src/operations/save/strategies/issues_strategy.py
from ..mixins.selective_filtering import SelectiveFilteringMixin

class IssuesSaveStrategy(SelectiveFilteringMixin, SaveEntityStrategy):
    """Strategy for saving repository issues with selective filtering support."""

    def __init__(self, include_issues: Union[bool, Set[int]] = True):
        """Initialize issues save strategy."""
        super().__init__(include_spec=include_issues)

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform issues data with selective filtering."""
        return self.apply_selective_filtering(entities, context)
    
    # Remove _should_include_issue method - now inherited
```

#### Step 3: Update Pull Requests Strategy
```python
# In src/operations/save/strategies/pull_requests_strategy.py  
from ..mixins.selective_filtering import SelectiveFilteringMixin

class PullRequestsSaveStrategy(SelectiveFilteringMixin, SaveEntityStrategy):
    """Strategy for saving repository pull requests with selective filtering support."""

    def __init__(self, include_pull_requests: Union[bool, Set[int]] = True):
        """Initialize pull requests save strategy."""
        super().__init__(include_spec=include_pull_requests)

    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform pull requests data with selective filtering."""
        return self.apply_selective_filtering(entities, context)
    
    # Remove _should_include_pull_request method - now inherited
```

#### Step 4: Testing and Validation
- [ ] Verify selective filtering works for both boolean and set specifications
- [ ] Test warning messages for missing entity numbers
- [ ] Validate logging output format consistency
- [ ] Ensure no regression in existing selective save functionality

## Refactoring 2: Parent-Child Entity Coupling Framework

### Current State Analysis

**Location**: Comment filtering logic in save strategies  
**Files Affected**:
- `src/operations/save/strategies/comments_strategy.py:63-124`
- `src/operations/save/strategies/pr_comments_strategy.py:48-104`

**Duplication Pattern**:
- URL-based matching logic for coupling comments to parent entities
- Similar identifier extraction and matching algorithms
- Consistent filtering and reporting patterns

### Implementation Steps

#### Step 1: Design Entity Coupling Framework
```python
# In src/operations/save/mixins/entity_coupling.py
from abc import ABC, abstractmethod
from typing import List, Any, Dict, Set, Callable

class EntityCouplingMixin(ABC):
    """Mixin providing parent-child entity coupling capabilities."""
    
    def filter_children_by_parents(
        self, 
        children: List[Any], 
        parents: List[Any], 
        parent_context_key: str
    ) -> List[Any]:
        """Filter child entities based on saved parent entities."""
        if not parents:
            return self._handle_no_parents(children)
        
        parent_identifiers = self._extract_parent_identifiers(parents)
        if not parent_identifiers:
            print(f"No valid parent identifiers found, skipping all {self.get_entity_name()}")
            return []
        
        # Filter children
        filtered_children = []
        for child in children:
            if self._child_matches_parent(child, parent_identifiers):
                filtered_children.append(child)
        
        # Report results
        self._report_coupling_results(filtered_children, children, parents)
        return filtered_children
    
    def _extract_parent_identifiers(self, parents: List[Any]) -> Set[str]:
        """Extract all possible identifiers from parent entities."""
        identifiers = set()
        
        for parent in parents:
            # Add entity number
            if hasattr(parent, "number"):
                identifiers.add(str(parent.number))
            
            # Add URL patterns
            if hasattr(parent, "html_url"):
                identifiers.add(parent.html_url)
                # Extract number and create API URL patterns
                try:
                    number = parent.html_url.split("/")[-1]
                    api_pattern = f"/{self.get_parent_api_path()}/{number}"
                    identifiers.add(api_pattern)
                except (IndexError, ValueError):
                    pass
        
        return identifiers
    
    def _child_matches_parent(self, child: Any, parent_identifiers: Set[str]) -> bool:
        """Check if child entity matches any parent identifier."""
        child_url = self._get_child_parent_url(child)
        if not child_url:
            return False
        
        # Direct match
        if child_url in parent_identifiers:
            return True
        
        # Partial URL matches
        for identifier in parent_identifiers:
            if identifier in child_url:
                return True
        
        # Extract and match number from URL
        try:
            number = child_url.split("/")[-1]
            if number in parent_identifiers:
                return True
        except (IndexError, ValueError):
            pass
        
        return False
    
    def _handle_no_parents(self, children: List[Any]) -> List[Any]:
        """Handle case when no parent entities are available."""
        if not hasattr(self, "_selective_mode") or not self._selective_mode:
            return children  # Backward compatibility
        else:
            print(f"No parents were saved, skipping all {self.get_entity_name()}")
            return []
    
    def _report_coupling_results(
        self, filtered_children: List[Any], all_children: List[Any], parents: List[Any]
    ) -> None:
        """Report coupling results."""
        parent_name = self.get_parent_entity_name()
        child_name = self.get_entity_name()
        
        print(
            f"Selected {len(filtered_children)} {child_name} from {len(all_children)} total "
            f"(coupling to {len(parents)} saved {parent_name})"
        )
    
    @abstractmethod
    def get_parent_entity_name(self) -> str:
        """Return the parent entity name for logging."""
        pass
    
    @abstractmethod
    def get_parent_api_path(self) -> str:
        """Return the API path segment for parent entities (e.g., 'issues', 'pulls')."""
        pass
    
    @abstractmethod
    def _get_child_parent_url(self, child: Any) -> str:
        """Extract the parent URL from child entity."""
        pass
```

#### Step 2: Update Comments Strategy
```python
# In src/operations/save/strategies/comments_strategy.py
from ..mixins.entity_coupling import EntityCouplingMixin

class CommentsSaveStrategy(EntityCouplingMixin, SaveEntityStrategy):
    """Strategy for saving repository comments with issue coupling."""
    
    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform comments data with issue coupling."""
        saved_issues = context.get("issues", [])
        return self.filter_children_by_parents(entities, saved_issues, "issues")
    
    def get_parent_entity_name(self) -> str:
        """Return parent entity name."""
        return "issues"
    
    def get_parent_api_path(self) -> str:
        """Return parent API path."""
        return "issues"
    
    def _get_child_parent_url(self, child: Any) -> str:
        """Extract issue URL from comment."""
        return getattr(child, "issue_url", "")
    
    # Remove _filter_comments_by_issues and related methods
```

#### Step 3: Update PR Comments Strategy
```python
# In src/operations/save/strategies/pr_comments_strategy.py
from ..mixins.entity_coupling import EntityCouplingMixin

class PullRequestCommentsSaveStrategy(EntityCouplingMixin, SaveEntityStrategy):
    """Strategy for saving repository pull request comments."""
    
    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process and transform PR comments data with pull request coupling."""
        saved_prs = context.get("pull_requests", [])
        return self.filter_children_by_parents(entities, saved_prs, "pull_requests")
    
    def get_parent_entity_name(self) -> str:
        """Return parent entity name."""
        return "pull_requests"
    
    def get_parent_api_path(self) -> str:
        """Return parent API path."""
        return "pulls"
    
    def _get_child_parent_url(self, child: Any) -> str:
        """Extract pull request URL from comment."""
        return getattr(child, "pull_request_url", "")
    
    # Remove _filter_pr_comments_by_prs and related methods
```

## Refactoring 3: Conflict Strategy Factory Pattern

### Current State Analysis

**Location**: Multiple conflict strategy classes in restore operations  
**Files Affected**:
- `src/operations/restore/strategies/labels_strategy.py:104-246`

**Duplication Pattern**:
- Similar exception handling patterns
- Consistent error result formatting
- Repeated logging and validation logic

### Implementation Steps

#### Step 1: Design Base Conflict Strategy
```python
# In src/operations/restore/strategies/conflict_base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable

class BaseConflictStrategy(ABC):
    """Base class for conflict resolution strategies."""
    
    def execute_with_error_handling(
        self, 
        operation_name: str, 
        operation_fn: Callable[[], Any]
    ) -> Dict[str, Any]:
        """Execute operation with standardized error handling."""
        try:
            result = operation_fn()
            return self._success_result(operation_name, result)
        except Exception as e:
            return self._error_result(operation_name, e)
    
    def _success_result(self, operation_name: str, result: Any) -> Dict[str, Any]:
        """Standard success result format."""
        return {
            "success": True,
            "operation": operation_name,
            "strategy": self.__class__.__name__,
            "result": result,
        }
    
    def _error_result(self, operation_name: str, error: Exception) -> Dict[str, Any]:
        """Standard error result format."""
        return {
            "success": False,
            "operation": operation_name,
            "strategy": self.__class__.__name__,
            "error": str(error),
            "error_type": error.__class__.__name__,
        }
    
    @abstractmethod
    def resolve_conflict(self, existing_entity: Any, new_entity: Any) -> Any:
        """Resolve conflict between existing and new entity."""
        pass
```

#### Step 2: Create Conflict Strategy Factory
```python
# In src/operations/restore/strategies/conflict_factory.py
from typing import Dict, Type
from .conflict_base import BaseConflictStrategy
from .conflict_strategies import (
    SkipConflictStrategy,
    OverwriteConflictStrategy, 
    RenameConflictStrategy,
    MergeConflictStrategy
)

class ConflictStrategyFactory:
    """Factory for creating conflict resolution strategies."""
    
    _strategies: Dict[str, Type[BaseConflictStrategy]] = {
        "skip": SkipConflictStrategy,
        "overwrite": OverwriteConflictStrategy,
        "rename": RenameConflictStrategy,
        "merge": MergeConflictStrategy,
    }
    
    @classmethod
    def create_strategy(cls, strategy_name: str) -> BaseConflictStrategy:
        """Create conflict strategy by name."""
        if strategy_name not in cls._strategies:
            raise ValueError(f"Unknown conflict strategy: {strategy_name}")
        
        strategy_class = cls._strategies[strategy_name]
        return strategy_class()
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """Get list of available strategy names."""
        return list(cls._strategies.keys())
```

#### Step 3: Refactor Individual Conflict Strategies
- Extract common error handling into base class
- Standardize result formats
- Simplify concrete strategy implementations

## Implementation Timeline

### Day 1: Selective Filtering Mixin
- [ ] Create mixin framework and base classes
- [ ] Update issues strategy implementation
- [ ] Run tests and validate filtering logic

### Day 2: Complete Selective Filtering
- [ ] Update pull requests strategy implementation
- [ ] Full test suite execution and validation
- [ ] Performance testing and optimization

### Day 3: Entity Coupling Framework
- [ ] Implement coupling mixin and base classes
- [ ] Update comments strategy implementation
- [ ] Test issue-comment coupling scenarios

### Day 4: Complete Entity Coupling
- [ ] Update PR comments strategy implementation
- [ ] Full coupling validation and testing
- [ ] Integration testing with selective filtering

### Day 5: Conflict Strategy Factory
- [ ] Implement base conflict strategy and factory
- [ ] Refactor existing conflict strategies
- [ ] End-to-end testing and validation

## Success Criteria

### Quantitative Goals
- [ ] 270 lines of code eliminated (90 + 80 + 100)
- [ ] All existing tests pass
- [ ] No performance regression (< 5% variance)
- [ ] Code coverage maintained or improved

### Qualitative Goals
- [ ] Simplified strategy implementation for new entity types
- [ ] Consistent error handling and logging patterns
- [ ] Clear separation of generic vs entity-specific logic
- [ ] Enhanced maintainability and readability

## Risk Mitigation

### Identified Risks
1. **Complex Mixin Inheritance**
   - **Mitigation**: Careful multiple inheritance design with clear method resolution
   - **Testing**: Comprehensive inheritance hierarchy testing

2. **URL Matching Edge Cases**
   - **Mitigation**: Extensive test coverage for various URL patterns
   - **Validation**: Test with real GitHub data patterns

3. **Backward Compatibility**
   - **Mitigation**: Preserve all existing behavior and configuration options
   - **Testing**: Run full regression test suite

### Rollback Plan
- Maintain feature branch isolation
- Commit each refactoring step separately
- Keep detailed rollback procedures for each mixin

## Phase 3 Preparation

Phase 2 establishes the foundation for Phase 3's final optimizations:
- **Mixin patterns** proven for complex abstractions
- **Generic frameworks** ready for factory pattern improvements
- **Testing approach** validated for high-complexity changes

## Next Steps

1. Get approval for Phase 2 plan
2. Create feature branch: `feature/phase-2-strategic-patterns`
3. Begin implementation following daily timeline
4. Prepare Phase 3 plan based on Phase 2 learnings and remaining duplication analysis