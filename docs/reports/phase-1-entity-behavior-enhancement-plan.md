# Phase 1: Entity Behavior Enhancement - Detailed Implementation Plan

**Phase:** 1 of 5  
**Duration:** 3-4 sprints (6-8 weeks)  
**Priority:** Critical Path - Foundation for all other phases  
**Dependencies:** None (can start immediately)

## Executive Summary

This phase transforms anemic domain models into rich entities by adding 87+ business methods across 4 core entities. Implementation follows Test-Driven Development (TDD) with careful attention to backward compatibility and performance.

## Implementation Strategy

### Development Approach
- **Test-Driven Development**: Write tests first for each method
- **Incremental Implementation**: Add methods in dependency order
- **Backward Compatibility**: Maintain all existing interfaces
- **Performance Monitoring**: Benchmark before/after for critical methods

### Implementation Order
1. **Issue Entity** (Highest business impact, 41 methods)
2. **Label Entity** (Foundation for Issue labels, 12 methods) 
3. **Comment Entity** (Medium complexity, 11 methods)
4. **PullRequest Entity** (Complex state management, 13 methods)
5. **RepositoryData Entity** (Validation orchestration, 6 methods)

## Sprint 1: Issue Entity - Core State Management (Week 1-2)

### Sprint Goal
Implement critical Issue state management and validation methods that form the foundation for business logic.

### Tasks

#### Task 1.1: Issue State Management Methods (6 hours)
**File:** `src/models.py` - Issue class  
**Lines to modify:** After line 110

**Methods to implement:**
```python
def close(self, reason: Optional[str] = None, closed_by: Optional[GitHubUser] = None) -> None:
    """Close issue with business rule validation."""
    
def reopen(self) -> None:
    """Reopen a closed issue with validation."""
    
def can_be_closed(self) -> bool:
    """Check if issue can be closed based on business rules."""
    
def can_be_reopened(self) -> bool:
    """Check if issue can be reopened based on business rules."""
    
def is_open(self) -> bool:
    """Check if issue is in open state."""
    
def is_closed(self) -> bool:
    """Check if issue is in closed state."""
```

**Business Rules:**
- Issues can only be closed if currently open
- Closed issues must have closed_at timestamp
- Reopened issues must clear closed_at and closed_by
- State transitions must be logged

**Test Scenarios:**
```python
# Test file: tests/domain/test_issue_state_management.py
def test_close_open_issue():
    """Test closing an open issue sets proper fields."""
    
def test_close_already_closed_issue():
    """Test closing closed issue raises StateTransitionError."""
    
def test_reopen_closed_issue():
    """Test reopening closed issue clears closure fields."""
    
def test_can_be_closed_validation():
    """Test business rule validation for closing."""
```

#### Task 1.2: Issue Validation Methods (4 hours)
**Methods to implement:**
```python
def validate_title(self) -> None:
    """Validate issue title meets business rules."""
    
def validate_state_transition(self, new_state: str) -> bool:
    """Validate if state transition is allowed."""
    
def validate_assignees(self) -> None:
    """Validate assignee business rules."""
    
def is_valid(self) -> bool:
    """Comprehensive validation check."""
```

**Business Rules:**
- Title cannot be empty or whitespace-only
- Title maximum length: 256 characters
- Valid states: "open", "closed"
- Maximum 10 assignees per issue
- State transitions: open ↔ closed only

#### Task 1.3: Issue Timing and Age Methods (3 hours)
**Methods to implement:**
```python
def calculate_age(self) -> timedelta:
    """Calculate issue age from creation."""
    
def is_stale(self, days: int = 30) -> bool:
    """Check if issue is stale based on last activity."""
    
def has_activity_since(self, date: datetime) -> bool:
    """Check if issue has activity since given date."""
```

**Business Rules:**
- Age calculated from created_at to now (if open) or closed_at (if closed)
- Stale determination based on updated_at field
- Activity includes updates to issue or comments

## Sprint 2: Issue Entity - Sub-issue Hierarchy (Week 3)

### Sprint Goal
Implement complete sub-issue relationship management with hierarchy validation.

#### Task 2.1: Sub-issue Management Core (8 hours)
**Methods to implement:**
```python
def add_sub_issue(self, sub_issue: 'SubIssue') -> None:
    """Add sub-issue with hierarchy validation."""
    
def remove_sub_issue(self, sub_issue_number: int) -> None:
    """Remove sub-issue by number."""
    
def reorder_sub_issues(self, new_order: List[int]) -> None:
    """Reorder sub-issues by position."""
    
def has_sub_issues(self) -> bool:
    """Check if issue has sub-issues."""
    
def is_sub_issue(self) -> bool:
    """Check if this issue is a sub-issue of another."""
    
def get_max_hierarchy_depth(self) -> int:
    """Calculate maximum depth in sub-issue hierarchy."""
```

**Business Rules:**
- Maximum hierarchy depth: 8 levels (GitHub limitation)
- No circular dependencies allowed
- Sub-issues cannot be added to closed parent issues
- Position must be unique within parent
- Sub-issues inherit some parent properties

**Complex Test Scenarios:**
```python
def test_hierarchy_depth_validation():
    """Test 8-level depth limit enforcement."""
    
def test_circular_dependency_prevention():
    """Test prevention of circular sub-issue relationships."""
    
def test_closed_parent_sub_issue_addition():
    """Test adding sub-issue to closed parent fails."""
```

## Sprint 3: Label and Comment Entities (Week 4)

### Sprint Goal
Complete Label entity behavior and Comment entity analysis methods.

#### Task 3.1: Label Entity Implementation (6 hours)
**Methods to implement:**
```python
# Validation methods
def validate_color(self) -> None:
def validate_name(self) -> None:
def is_valid_hex_color(self) -> bool:
def is_conflict_with(self, other: 'Label') -> bool:

# Utility methods  
def to_hex_color(self) -> str:
def get_contrast_color(self) -> str:
def is_system_label(self) -> bool:
def get_color_brightness(self) -> float:

# Comparison methods
def is_equivalent_to(self, other: 'Label') -> bool:
def differs_only_in_color(self, other: 'Label') -> bool:
```

**Business Rules:**
- Color must be valid 6-character hex (no #)
- Names 1-50 characters, no leading/trailing whitespace
- System labels: "bug", "enhancement", "question", "documentation"
- Brightness calculation for accessibility

#### Task 3.2: Comment Entity Implementation (5 hours)
**Methods to implement:**
```python
# Content validation
def validate_body(self) -> None:
def is_empty(self) -> bool:
def exceeds_max_length(self, max_length: int = 65536) -> bool:

# Content analysis
def get_word_count(self) -> int:
def get_character_count(self) -> int:
def mentions_users(self) -> List[str]:
def extract_mentioned_users(self) -> List[GitHubUser]:
def contains_code_blocks(self) -> bool:

# Timing analysis
def calculate_response_time(self, previous_comment: 'Comment') -> timedelta:
def is_recent(self, hours: int = 24) -> bool:
def time_since_creation(self) -> timedelta:
```

## Sprint 4: PullRequest Entity and RepositoryData (Week 5-6)

### Sprint Goal
Complete PullRequest entity with complex state management and RepositoryData validation.

#### Task 4.1: PullRequest State Management (8 hours)
**Methods to implement:**
```python
def can_be_merged(self) -> bool:
def is_mergeable(self) -> bool:
def has_merge_conflicts(self) -> bool:
def is_draft(self) -> bool:
def is_ready_for_review(self) -> bool:
def validate_branch_names(self) -> None:
def validate_merge_conditions(self) -> None:
def has_required_reviews(self, min_reviews: int = 1) -> bool:
```

**Complex Business Rules:**
- Merge states: OPEN → MERGED or CLOSED
- Draft PRs cannot be merged
- Branch validation (no self-merges)
- Review requirements configurable

#### Task 4.2: RepositoryData Validation (4 hours)
**Methods to implement:**
```python
def validate_required_files(self, data_path: Path) -> None:
def validate_data_consistency(self) -> None:
def has_complete_dataset(self, include_prs: bool, include_sub_issues: bool) -> bool:
def get_data_summary(self) -> Dict[str, int]:
def validate_relationships(self) -> None:
def is_export_complete(self) -> bool:
```

## Testing Strategy

### Test Structure
```
tests/
├── domain/
│   ├── __init__.py
│   ├── test_issue_behavior.py      # 25+ test methods
│   ├── test_label_behavior.py      # 15+ test methods  
│   ├── test_comment_behavior.py    # 12+ test methods
│   ├── test_pullrequest_behavior.py # 18+ test methods
│   └── test_repository_data.py     # 8+ test methods
└── fixtures/
    ├── sample_issues.py
    ├── sample_labels.py
    └── sample_comments.py
```

### Test Categories

#### 1. Unit Tests (Fast, Isolated)
- Individual method behavior
- Business rule validation
- Edge cases and error conditions
- Performance benchmarks

#### 2. Integration Tests  
- Entity interaction scenarios
- Complex business workflows
- Cross-entity validation
- Data consistency checks

#### 3. Property-Based Tests
- Using Hypothesis for validation edge cases
- Generated test data for robustness
- Boundary condition testing

### Coverage Requirements
- **Line Coverage**: 95%+ for all entity methods
- **Branch Coverage**: 90%+ for complex validation logic
- **Edge Case Coverage**: All business rule violations tested

## Performance Considerations

### Benchmarking Plan
```python
# Performance test file: tests/performance/test_entity_performance.py

def test_issue_state_methods_performance():
    """Ensure state methods complete in <1ms."""
    
def test_hierarchy_calculation_performance():
    """Test hierarchy depth calculation scales with issue count."""
    
def test_label_validation_batch_performance():
    """Test label validation performance with 1000+ labels."""
```

### Performance Targets
- **State management methods**: <1ms per call
- **Hierarchy calculations**: <10ms for 100 sub-issues
- **Validation methods**: <5ms per entity
- **Memory usage**: No increase >10% from current baseline

## Risk Mitigation

### Risk 1: Breaking Existing Code
**Mitigation:**
- Add methods alongside existing fields
- Comprehensive integration tests
- Gradual rollout with feature flags

### Risk 2: Performance Degradation
**Mitigation:**
- Benchmark every method implementation
- Lazy loading for expensive calculations
- Caching for frequently accessed derived data

### Risk 3: Complex Sub-issue Logic
**Mitigation:**
- Start with simple hierarchy operations
- Extensive test coverage for edge cases
- Clear error messages for business rule violations

## Migration Strategy

### Backward Compatibility
1. **Existing Code**: All current functionality preserved
2. **New Methods**: Added without changing existing interfaces
3. **Deprecation**: Future phase will deprecate procedural functions
4. **Documentation**: Clear migration guides for each method

### Integration Points
- **Operations Layer**: Will use new methods in Phase 3
- **Storage Layer**: No changes required in Phase 1
- **CLI Interface**: Enhanced error messages from validation

## Success Criteria

### Phase 1 Completion Definition
- [ ] All 87+ entity methods implemented with business logic
- [ ] Comprehensive test suite with 95%+ coverage
- [ ] Performance benchmarks meet targets
- [ ] All existing functionality preserved
- [ ] Documentation updated with new method usage
- [ ] Integration tests pass with enhanced entities

### Quality Gates
1. **Code Review**: All methods peer-reviewed
2. **Testing**: TDD approach with tests-first
3. **Performance**: Benchmarks within targets
4. **Integration**: Existing workflows unaffected
5. **Documentation**: Method signatures and business rules documented

## Next Phase Preparation

### Phase 2 Foundation
- Domain service interfaces defined based on entity methods
- Complex business logic identified for extraction
- Service layer integration points planned

This detailed plan ensures systematic, test-driven implementation of rich domain entities while maintaining system stability and performance.