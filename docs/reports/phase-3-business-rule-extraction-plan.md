# Phase 3: Business Rule Extraction - Detailed Implementation Plan

**Phase:** 3 of 5  
**Duration:** 3-4 sprints (6-8 weeks)  
**Priority:** Critical - Removes procedural anti-patterns  
**Dependencies:** Phase 1 & 2 completion (entities + services required)

## Executive Summary

This phase systematically migrates business logic from procedural operations code to entity methods and domain services. The migration preserves all functionality while transforming the codebase from procedural to object-oriented domain modeling.

## Migration Strategy

### Core Approach
- **File-by-File Migration**: Systematic transformation of each operations file
- **Backward Compatibility**: Maintain existing interfaces during transition
- **Incremental Replacement**: Replace function implementations with entity/service calls
- **Comprehensive Testing**: Ensure no functionality regression

### Migration Priority Order
1. **`src/operations/restore.py`** (Highest complexity, most business logic)
2. **`src/operations/save.py`** (Medium complexity, validation logic)
3. **`src/conflict_strategies.py`** (Business rule logic → Domain services)
4. **`src/github/metadata.py`** (Data formatting → Entity methods)

## Sprint 1: Restore Operations Migration (Week 1-2)

### Sprint Goal
Migrate all business logic from restore operations to entity methods and domain services while maintaining the exact same CLI interface and functionality.

### Current State Analysis

#### Procedural Logic in `src/operations/restore.py`
**Lines 32-71**: File validation logic (procedural)  
**Lines 73-134**: Label conflict resolution (procedural)  
**Lines 135-220**: Issue restoration with number mapping (procedural)  
**Lines 221-280**: Comment restoration with relationship handling (procedural)  
**Lines 281-350**: Sub-issue hierarchy restoration (procedural)

### Task 1.1: File Validation Migration (4 hours)

#### Current Procedural Code (Lines 55-71)
```python
def _validate_data_files_exist(input_dir: Path, include_prs: bool = False, include_sub_issues: bool = False) -> None:
    """Validate that required data files exist."""
    required_files = ["labels.json", "issues.json", "comments.json"]
    
    if include_prs:
        required_files.extend(["pull_requests.json", "pr_comments.json"])
    
    if include_sub_issues:
        required_files.append("sub_issues.json")
    
    for filename in required_files:
        file_path = input_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Required data file not found: {file_path}")
```

#### Target Entity-Based Implementation
**File:** `src/operations/restore.py` - Update function implementation

**New Implementation:**
```python
def _validate_data_files_exist(input_dir: Path, include_prs: bool = False, include_sub_issues: bool = False) -> None:
    """Validate that required data files exist using domain service."""
    from ..domain.services.repository_services import RepositoryValidationService
    
    # Migrate to domain service
    RepositoryValidationService.validate_file_requirements(input_dir, include_prs, include_sub_issues)
```

**Add Deprecation Warning:**
```python
import warnings

def _validate_data_files_exist(input_dir: Path, include_prs: bool = False, include_sub_issues: bool = False) -> None:
    """Validate that required data files exist using domain service.
    
    DEPRECATED: This function will be removed in v2.0. Use RepositoryValidationService directly.
    """
    warnings.warn(
        "_validate_data_files_exist is deprecated. Use RepositoryValidationService.validate_file_requirements",
        DeprecationWarning,
        stacklevel=2
    )
    
    from ..domain.services.repository_services import RepositoryValidationService
    RepositoryValidationService.validate_file_requirements(input_dir, include_prs, include_sub_issues)
```

### Task 1.2: Label Conflict Resolution Migration (8 hours)

#### Current Procedural Code Analysis
**Functions to migrate:**
- `_handle_fail_if_existing()` → `LabelConflictService.detect_conflicts()`
- `_handle_fail_if_conflict()` → `LabelConflictService.detect_semantic_conflicts()`
- `_handle_delete_all()` → Entity method + service
- `_handle_overwrite()` → `LabelConflictService.resolve_conflicts_automatically()`

#### Migration Implementation
**File:** `src/operations/restore.py` - Lines 91-100

**Current Code:**
```python
# Apply conflict resolution strategy
if strategy == LabelConflictStrategy.FAIL_IF_EXISTING:
    _handle_fail_if_existing(existing_labels)
elif strategy == LabelConflictStrategy.FAIL_IF_CONFLICT:
    _handle_fail_if_conflict(existing_labels, labels_to_restore)
elif strategy == LabelConflictStrategy.DELETE_ALL:
    _handle_delete_all(client, repo_name, existing_labels)
    existing_labels = []  # No conflicts after deletion
elif strategy == LabelConflictStrategy.OVERWRITE:
    _handle_overwrite(client, repo_name, existing_labels, labels_to_restore)
    return  # Overwrite strategy handles all label creation
```

**New Implementation:**
```python
# Apply conflict resolution strategy using domain services
from ..domain.services.label_services import LabelConflictService

if strategy == LabelConflictStrategy.FAIL_IF_EXISTING:
    conflicts = LabelConflictService.detect_conflicts(existing_labels, labels_to_restore)
    if conflicts:
        raise ConflictError("label_name", conflicts, ["Use different conflict strategy"])
        
elif strategy == LabelConflictStrategy.FAIL_IF_CONFLICT:
    conflicts = LabelConflictService.detect_semantic_conflicts(existing_labels, labels_to_restore)
    if conflicts:
        suggestions = LabelConflictService.suggest_merge_strategy(conflicts)
        raise ConflictError("label_semantic", conflicts, list(suggestions.values()))
        
elif strategy == LabelConflictStrategy.DELETE_ALL:
    # Use entity methods for validation before deletion
    for label in existing_labels:
        if not label.can_be_deleted():  # New entity method
            raise DomainValidationError("Label", f"Cannot delete system label: {label.name}")
    
    _handle_delete_all(client, repo_name, existing_labels)
    existing_labels = []
    
elif strategy == LabelConflictStrategy.OVERWRITE:
    resolved_labels, conflicts = LabelConflictService.resolve_conflicts_automatically(
        existing_labels, labels_to_restore, "prefer_new"
    )
    _create_labels_with_entity_validation(client, repo_name, resolved_labels)
    return
```

### Task 1.3: Issue Restoration Migration (10 hours)

#### Current Procedural Code (Lines 135-165)
```python
def _restore_issues(client: GitHubService, repo_name: str, input_dir: Path, include_original_metadata: bool) -> Dict[int, int]:
    """Restore issues and return mapping from original to new issue numbers."""
    issues_data = load_json_data(input_dir / "issues.json")
    issues = [converters.convert_to_issue(issue_dict) for issue_dict in issues_data]
    
    # Sort by number to maintain issue relationships
    issues.sort(key=lambda x: x.number)
    
    issue_number_mapping = {}
    
    for issue in issues:
        # Create issue using GitHub API
        api_data = converters.convert_from_issue(issue)
        
        if include_original_metadata:
            api_data = _add_original_metadata_to_body(api_data, issue)
        
        created_issue_data = client.create_issue(repo_name, api_data)
        created_issue = converters.convert_to_issue(created_issue_data)
        
        issue_number_mapping[issue.number] = created_issue.number
        print(f"Restored issue #{issue.number} as #{created_issue.number}: {issue.title}")
    
    return issue_number_mapping
```

#### Target Entity-Based Implementation
```python
def _restore_issues(client: GitHubService, repo_name: str, input_dir: Path, include_original_metadata: bool) -> Dict[int, int]:
    """Restore issues using entity methods and domain services."""
    from ..domain.factories import IssueFactory
    from ..domain.services.issue_services import IssueConflictService
    
    issues_data = load_json_data(input_dir / "issues.json")
    
    # Use factory to create validated entities
    issues = []
    for issue_dict in issues_data:
        try:
            issue = IssueFactory.create_from_github_data(issue_dict)
            # Validate business rules before restoration
            if not issue.is_valid():
                print(f"Skipping invalid issue #{issue.number}: {issue.validation_errors}")
                continue
            issues.append(issue)
        except DomainValidationError as e:
            print(f"Skipping issue #{issue_dict.get('number', 'unknown')}: {e.validation_error}")
            continue
    
    # Use domain service to detect and resolve conflicts
    existing_issues = _get_existing_issues(client, repo_name)
    conflicts = IssueConflictService.detect_number_conflicts(existing_issues, issues)
    
    if conflicts:
        resolution_strategy = IssueConflictService.suggest_resolution_strategy(conflicts)
        print(f"Issue conflicts detected: {conflicts}")
        print(f"Suggested resolution: {resolution_strategy}")
        # Could implement automatic resolution here
    
    # Sort by number to maintain relationships (now using entity method)
    issues.sort(key=lambda x: x.number)
    
    issue_number_mapping = {}
    
    for issue in issues:
        try:
            # Use entity method for state validation
            if not issue.can_be_created():  # New entity method
                print(f"Skipping issue #{issue.number}: cannot be created in current state")
                continue
            
            # Convert to API format using entity method
            api_data = issue.to_api_format()  # New entity method
            
            if include_original_metadata:
                api_data = issue.add_metadata_to_body(api_data)  # New entity method
            
            created_issue_data = client.create_issue(repo_name, api_data)
            created_issue = IssueFactory.create_from_github_data(created_issue_data)
            
            issue_number_mapping[issue.number] = created_issue.number
            print(f"Restored issue #{issue.number} as #{created_issue.number}: {issue.title}")
            
        except DomainValidationError as e:
            print(f"Failed to restore issue #{issue.number}: {e.validation_error}")
            continue
    
    return issue_number_mapping
```

**New Entity Methods Required:**
```python
# Add to Issue class in src/models.py
def can_be_created(self) -> bool:
    """Check if issue can be created in target repository."""
    
def to_api_format(self) -> Dict[str, Any]:
    """Convert issue to GitHub API format."""
    
def add_metadata_to_body(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add original metadata to issue body."""
    
@property
def validation_errors(self) -> List[str]:
    """Get list of validation errors for this issue."""
```

### Task 1.4: Sub-issue Hierarchy Migration (12 hours)

#### Current Procedural Code (Lines 281-320)
```python
def _restore_sub_issues(client: GitHubService, repo_name: str, input_dir: Path, issue_number_mapping: Dict[int, int]) -> None:
    """Restore sub-issue relationships after all issues are created."""
    sub_issues_data = load_json_data(input_dir / "sub_issues.json")
    sub_issues = [converters.convert_to_sub_issue(sub_dict) for sub_dict in sub_issues_data]
    
    # Group by parent issue
    sub_issues_by_parent = {}
    for sub_issue in sub_issues:
        parent_num = sub_issue.parent_issue_number
        if parent_num not in sub_issues_by_parent:
            sub_issues_by_parent[parent_num] = []
        sub_issues_by_parent[parent_num].append(sub_issue)
    
    # Restore relationships for each parent
    for original_parent_num, sub_issue_list in sub_issues_by_parent.items():
        if original_parent_num not in issue_number_mapping:
            print(f"Skipping sub-issues for unmapped parent #{original_parent_num}")
            continue
        
        new_parent_num = issue_number_mapping[original_parent_num]
        
        # Sort by position to maintain order
        sub_issue_list.sort(key=lambda x: x.position)
        
        for sub_issue in sub_issue_list:
            if sub_issue.sub_issue_number not in issue_number_mapping:
                print(f"Skipping unmapped sub-issue #{sub_issue.sub_issue_number}")
                continue
            
            new_sub_issue_num = issue_number_mapping[sub_issue.sub_issue_number]
            
            # Create sub-issue relationship via GitHub API
            client.add_sub_issue(repo_name, new_parent_num, new_sub_issue_num, sub_issue.position)
            print(f"Added sub-issue #{new_sub_issue_num} to parent #{new_parent_num}")
```

#### Target Entity and Service-Based Implementation
```python
def _restore_sub_issues(client: GitHubService, repo_name: str, input_dir: Path, issue_number_mapping: Dict[int, int]) -> None:
    """Restore sub-issue relationships using entity methods and hierarchy service."""
    from ..domain.services.issue_services import IssueHierarchyService
    
    sub_issues_data = load_json_data(input_dir / "sub_issues.json")
    sub_issues = [converters.convert_to_sub_issue(sub_dict) for sub_dict in sub_issues_data]
    
    # Get all restored issues as entities
    all_issues = _get_all_restored_issues(client, repo_name, issue_number_mapping)
    issue_lookup = {issue.number: issue for issue in all_issues}
    
    # Validate hierarchy integrity before any relationships are created
    validation_errors = []
    
    # Check for circular dependencies
    circular_deps = IssueHierarchyService.detect_circular_dependencies(all_issues)
    if circular_deps:
        validation_errors.extend([f"Circular dependency: {dep}" for dep in circular_deps])
    
    # Validate hierarchy depth constraints
    for sub_issue in sub_issues:
        original_parent = sub_issue.parent_issue_number
        original_sub = sub_issue.sub_issue_number
        
        if original_parent in issue_number_mapping and original_sub in issue_number_mapping:
            new_parent_num = issue_number_mapping[original_parent]
            new_sub_num = issue_number_mapping[original_sub]
            
            if new_parent_num in issue_lookup and new_sub_num in issue_lookup:
                parent_issue = issue_lookup[new_parent_num]
                sub_issue_entity = issue_lookup[new_sub_num]
                
                try:
                    IssueHierarchyService.validate_hierarchy_depth(parent_issue, sub_issue_entity, all_issues)
                except HierarchyError as e:
                    validation_errors.append(str(e))
    
    if validation_errors:
        print(f"Sub-issue hierarchy validation failed:")
        for error in validation_errors:
            print(f"  - {error}")
        raise DomainValidationError("SubIssueHierarchy", "Hierarchy validation failed", validation_errors)
    
    # Group by parent issue using entity method
    sub_issues_by_parent = {}
    for sub_issue in sub_issues:
        parent_num = sub_issue.parent_issue_number
        if parent_num not in sub_issues_by_parent:
            sub_issues_by_parent[parent_num] = []
        sub_issues_by_parent[parent_num].append(sub_issue)
    
    # Restore relationships using entity methods
    for original_parent_num, sub_issue_list in sub_issues_by_parent.items():
        if original_parent_num not in issue_number_mapping:
            print(f"Skipping sub-issues for unmapped parent #{original_parent_num}")
            continue
        
        new_parent_num = issue_number_mapping[original_parent_num]
        parent_issue = issue_lookup.get(new_parent_num)
        
        if not parent_issue:
            print(f"Parent issue #{new_parent_num} not found")
            continue
        
        # Validate parent can accept sub-issues
        if not parent_issue.can_accept_sub_issues():  # New entity method
            print(f"Parent issue #{new_parent_num} cannot accept sub-issues (state: {parent_issue.state})")
            continue
        
        # Sort by position to maintain order
        sub_issue_list.sort(key=lambda x: x.position)
        
        for sub_issue in sub_issue_list:
            if sub_issue.sub_issue_number not in issue_number_mapping:
                print(f"Skipping unmapped sub-issue #{sub_issue.sub_issue_number}")
                continue
            
            new_sub_issue_num = issue_number_mapping[sub_issue.sub_issue_number]
            sub_issue_entity = issue_lookup.get(new_sub_issue_num)
            
            if not sub_issue_entity:
                print(f"Sub-issue #{new_sub_issue_num} not found")
                continue
            
            try:
                # Use entity method to add sub-issue with validation
                parent_issue.add_sub_issue(SubIssue(
                    sub_issue_id=sub_issue_entity.id,
                    sub_issue_number=new_sub_issue_num,
                    parent_issue_id=parent_issue.id,
                    parent_issue_number=new_parent_num,
                    position=sub_issue.position
                ))
                
                # Create relationship via GitHub API
                client.add_sub_issue(repo_name, new_parent_num, new_sub_issue_num, sub_issue.position)
                print(f"Added sub-issue #{new_sub_issue_num} to parent #{new_parent_num}")
                
            except DomainValidationError as e:
                print(f"Failed to add sub-issue #{new_sub_issue_num} to #{new_parent_num}: {e.validation_error}")
                continue
```

**New Entity Methods Required:**
```python
# Add to Issue class in src/models.py
def can_accept_sub_issues(self) -> bool:
    """Check if issue can accept new sub-issues."""
    # Closed issues cannot accept sub-issues
    return self.is_open()

def add_sub_issue(self, sub_issue: SubIssue) -> None:
    """Add sub-issue with validation."""
    if not self.can_accept_sub_issues():
        raise StateTransitionError(
            entity=f"Issue #{self.number}",
            current_state=self.state,
            attempted_state="accept_sub_issues"
        )
    
    # Check for duplicate positions
    existing_positions = {sub.position for sub in self.sub_issues}
    if sub_issue.position in existing_positions:
        raise DomainValidationError(
            entity_type="SubIssue",
            validation_error=f"Position {sub_issue.position} already occupied",
            suggestions=["Use next available position", "Reorder existing sub-issues"]
        )
    
    self.sub_issues.append(sub_issue)
```

## Sprint 2: Save Operations Migration (Week 3)

### Sprint Goal
Migrate save operations to use entity validation and domain services for data consistency.

### Task 2.1: Save Operations Enhancement (8 hours)

#### Current State Analysis
**File:** `src/operations/save.py` - Contains procedural data saving logic

#### Migration Strategy
```python
# Current procedural approach
def save_repository_data(github_token: str, repo_name: str, output_path: str, ...) -> None:
    """Save repository data to JSON files."""
    # Procedural data collection and validation

# Target entity-based approach  
def save_repository_data(github_token: str, repo_name: str, output_path: str, ...) -> None:
    """Save repository data using entity validation and domain services."""
    from ..domain.factories import RepositoryDataBuilder
    from ..domain.services.repository_services import RepositoryValidationService
    
    # Use builder pattern for data assembly
    builder = RepositoryDataBuilder(repo_name)
    
    # Add data with validation
    labels = _collect_labels_with_validation(client, repo_name)
    builder.add_labels(labels)
    
    issues = _collect_issues_with_validation(client, repo_name)
    builder.add_issues(issues)
    
    # Validate and build complete dataset
    repo_data = builder.validate_and_build()
    
    # Use entity methods for serialization
    repo_data.save_to_directory(output_path)
```

## Sprint 3: Conflict Strategies Migration (Week 4)

### Sprint Goal
Migrate all conflict resolution logic from procedural functions to domain services.

### Task 3.1: Conflict Strategies Refactoring (6 hours)

#### Current File Structure
**File:** `src/conflict_strategies.py` (43 lines) - All procedural

#### Migration Plan
1. **Keep enum definitions** (no change needed)
2. **Migrate functions to LabelConflictService methods**
3. **Add backward compatibility adapters**
4. **Add deprecation warnings**

#### Implementation
```python
# src/conflict_strategies.py - Updated file
"""Label conflict resolution strategies.

DEPRECATED: Conflict resolution logic has moved to domain services.
This module provides backward compatibility adapters.
"""

import warnings
from enum import Enum
from typing import List

from .models import Label
from .domain.services.label_services import LabelConflictService


class LabelConflictStrategy(Enum):
    """Strategies for handling label conflicts during restoration."""
    # Keep existing enum - no changes needed


def parse_conflict_strategy(strategy_str: str) -> LabelConflictStrategy:
    """Parse conflict strategy from string with validation."""
    # Keep existing implementation - no changes needed


def detect_label_conflicts(existing_labels: List[Label], labels_to_restore: List[Label]) -> List[str]:
    """Detect conflicting label names between existing and restoration sets.
    
    DEPRECATED: Use LabelConflictService.detect_conflicts() instead.
    """
    warnings.warn(
        "detect_label_conflicts is deprecated. Use LabelConflictService.detect_conflicts",
        DeprecationWarning,
        stacklevel=2
    )
    
    return LabelConflictService.detect_conflicts(existing_labels, labels_to_restore)
```

## Sprint 4: Metadata Formatting Migration (Week 5)

### Sprint Goal
Move data formatting logic from github.metadata to entity methods.

### Task 4.1: Metadata Module Refactoring (6 hours)

#### Current State Analysis
**File:** `src/github/metadata.py` - Contains formatting utilities

#### Migration Strategy
Move formatting logic to entity methods where it belongs logically:

```python
# Current procedural approach
from ..github.metadata import format_issue_metadata

metadata = format_issue_metadata(issue, original_data)

# Target entity-based approach
metadata = issue.format_metadata(original_data)  # Entity method
```

## Testing Strategy for Phase 3

### Test Coverage Requirements
- **Migration Tests**: Verify identical behavior before/after migration
- **Integration Tests**: Ensure operations work with new entity/service calls
- **Regression Tests**: All existing CLI functionality preserved
- **Performance Tests**: No degradation in operation speed

### Test Structure
```
tests/migration/
├── __init__.py
├── test_restore_migration.py      # Before/after comparison tests
├── test_save_migration.py         # Save operation migration tests
├── test_conflict_migration.py     # Conflict resolution migration
├── test_metadata_migration.py     # Metadata formatting migration
└── fixtures/
    ├── legacy_outputs.py          # Expected outputs from current code
    └── migration_datasets.py      # Test data for migration validation
```

### Migration Validation Tests
```python
class TestRestoreMigration:
    """Test that migrated restore operations produce identical results."""
    
    def test_restore_produces_same_results(self):
        """Test that new entity-based restore matches old procedural restore."""
        # Run both implementations on same data
        # Compare final GitHub repository state
        # Ensure identical results
    
    def test_error_messages_preserved(self):
        """Test that error messages remain user-friendly."""
        # Test error scenarios with both implementations
        # Ensure error messages are equivalent or better
```

## Performance Considerations

### Performance Targets
- **Operations execution time**: No increase >5%
- **Memory usage**: No increase >10%
- **Error handling overhead**: <1ms additional per validation

### Optimization Strategies
- **Lazy loading**: Load entity methods only when needed
- **Caching**: Cache validation results for repeated operations
- **Batch operations**: Group entity operations for efficiency

## Risk Mitigation

### Risk 1: Behavioral Changes
**Mitigation:**
- Comprehensive before/after testing
- Gradual rollout with feature flags
- Rollback plan for each migration step

### Risk 2: Performance Regression
**Mitigation:**
- Benchmark every migrated operation
- Profile memory usage changes
- Optimize entity methods based on profiling

### Risk 3: Breaking Integrations
**Mitigation:**
- Maintain all public interfaces
- Add deprecation warnings before removal
- Provide clear migration documentation

## Backward Compatibility Strategy

### Compatibility Timeline
- **Phase 3**: All old interfaces maintained with deprecation warnings
- **Phase 4**: Documentation for migration to new interfaces
- **Phase 5**: Remove deprecated interfaces (major version bump)

### Adapter Pattern Implementation
```python
# Example adapter for backward compatibility
def legacy_validate_data_files(input_dir: Path, **kwargs) -> None:
    """Legacy interface adapter.
    
    DEPRECATED: Use RepositoryValidationService.validate_file_requirements
    """
    warnings.warn(
        "legacy_validate_data_files is deprecated",
        DeprecationWarning,
        stacklevel=2
    )
    
    from ..domain.services.repository_services import RepositoryValidationService
    RepositoryValidationService.validate_file_requirements(input_dir, **kwargs)
```

## Success Criteria

### Phase 3 Completion Definition
- [ ] All procedural business logic migrated to entities/services
- [ ] All operations use entity methods and domain services
- [ ] 100% backward compatibility maintained
- [ ] All existing tests pass without modification
- [ ] Performance targets met
- [ ] Comprehensive migration test suite
- [ ] Documentation updated with new patterns

### Quality Gates
1. **Functionality**: All CLI operations produce identical results
2. **Performance**: No regression in operation speed
3. **Testing**: Migration test suite with 100% coverage
4. **Documentation**: Clear migration guides for developers
5. **Compatibility**: All existing interfaces preserved

## Next Phase Preparation

### Foundation for Phase 4
- Entity methods established and tested
- Domain services proven in production
- Factory and builder patterns can now be implemented
- Complex object creation patterns identified

This systematic migration transforms the codebase from procedural to domain-driven while ensuring zero functionality loss and maintaining full backward compatibility.