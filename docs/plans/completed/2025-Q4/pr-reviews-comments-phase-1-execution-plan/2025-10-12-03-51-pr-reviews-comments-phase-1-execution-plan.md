# Phase 1 Execution Plan: PR Reviews Foundation

**Date:** 2025-10-12  
**Version:** 1.0  
**Status:** Ready for Implementation  
**Based on:** [2025-10-12-pr-reviews-comments-implementation-plan.md](./2025-10-12-pr-reviews-comments-implementation-plan.md)

## Phase 1 Overview

Phase 1 establishes the foundation for PR reviews support by implementing the core data models, configuration, and basic save/restore strategies. This phase mirrors existing issue patterns exactly to ensure architectural consistency.

## Implementation Steps

### Step 1: Data Models and Entities (Day 1, Morning)

#### 1.1 Create PR Reviews Entity Model
**File:** `src/entities/pr_reviews/models.py`
**Pattern:** Mirror `src/entities/issues/models.py`
**Implementation:**
```python
@dataclass
class PullRequestReview:
    id: str
    pr_number: int
    user: Dict[str, Any]
    body: str
    state: str  # PENDING, APPROVED, CHANGES_REQUESTED, DISMISSED
    html_url: str
    pull_request_url: str
    author_association: str
    submitted_at: str
    commit_id: str
    _original_id: Optional[str] = None
    _original_reviewer: Optional[str] = None
    _original_submitted_at: Optional[str] = None
```

#### 1.2 Create PR Reviews Package Init
**File:** `src/entities/pr_reviews/__init__.py`
**Content:** Export PullRequestReview model

#### 1.3 Create Review Comments Entity Model
**File:** `src/entities/pr_review_comments/models.py`
**Pattern:** Mirror `src/entities/comments/models.py`
**Implementation:**
```python
@dataclass  
class PullRequestReviewComment:
    id: str
    review_id: str
    pr_number: int
    diff_hunk: str
    path: str
    line: Optional[int]
    body: str
    user: Dict[str, Any]
    created_at: str
    updated_at: str
    html_url: str
    pull_request_url: str
    in_reply_to_id: Optional[str] = None
    _original_id: Optional[str] = None
    _original_author: Optional[str] = None
    _original_created_at: Optional[str] = None
    _original_path: Optional[str] = None
    _original_line: Optional[int] = None
```

#### 1.4 Create Review Comments Package Init
**File:** `src/entities/pr_review_comments/__init__.py`
**Content:** Export PullRequestReviewComment model

### Step 2: Configuration Extensions (Day 1, Afternoon)

#### 2.1 Environment Variables
**File:** `src/config/settings.py`
**Additions:**
```python
include_pr_reviews: bool = parse_boolean_env_var("INCLUDE_PR_REVIEWS", default=True)
include_pr_review_comments: bool = parse_boolean_env_var("INCLUDE_PR_REVIEW_COMMENTS", default=True)
```

#### 2.2 Dependency Validation
**Location:** Within existing validation logic in `src/config/settings.py`
**Rules to implement:**
- `INCLUDE_PR_REVIEWS=true` requires `INCLUDE_PULL_REQUESTS=true`
- `INCLUDE_PR_REVIEW_COMMENTS=true` requires `INCLUDE_PR_REVIEWS=true`
- `INCLUDE_PR_REVIEW_COMMENTS=true` requires `INCLUDE_PULL_REQUESTS=true`

**Pattern:** Mirror existing `INCLUDE_ISSUE_COMMENTS` validation logic exactly

### Step 3: GitHub API Integration (Day 2, Morning)

#### 3.1 GraphQL Query Extensions
**File:** `src/github/queries/pull_requests.py`
**Task:** Add review and review comments fields to existing PR queries
**Pattern:** Mirror issue comments query structure

#### 3.2 Service Method Extensions
**File:** `src/github/services/repository_service.py`
**New Methods to implement:**
```python
def get_pull_request_reviews(self, repo_name: str, pr_number: int) -> List[Dict[str, Any]]
def get_pull_request_review_comments(self, repo_name: str, review_id: str) -> List[Dict[str, Any]]
def create_pull_request_review(self, repo_name: str, pr_number: int, body: str, state: str) -> Dict[str, Any]
def create_pull_request_review_comment(self, repo_name: str, review_id: str, body: str) -> Dict[str, Any]
```

### Step 4: Save Strategy Implementation (Day 2, Afternoon)

#### 4.1 PR Reviews Save Strategy
**File:** `src/operations/save/strategies/pr_reviews_strategy.py`
**Base Classes:** `EntityCouplingMixin + SaveEntityStrategy`
**Dependencies:** `["pull_requests"]`
**Pattern:** Identical structure to `CommentsSaveStrategy`

**Key Implementation:**
```python
class PullRequestReviewsSaveStrategy(EntityCouplingMixin, SaveEntityStrategy):
    def get_dependencies(self) -> List[str]:
        return ["pull_requests"]
    
    def get_parent_entity_name(self) -> str:
        return "pull_requests"
        
    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        saved_prs = context.get("pull_requests", [])
        return self.filter_children_by_parents(entities, saved_prs, "pull_requests")
```

#### 4.2 Review Comments Save Strategy
**File:** `src/operations/save/strategies/pr_review_comments_strategy.py`
**Base Classes:** `EntityCouplingMixin + SaveEntityStrategy`
**Dependencies:** `["pr_reviews", "pull_requests"]`
**Pattern:** Mirror issue comments with review dependency

### Step 5: Restore Strategy Implementation (Day 3, Morning)

#### 5.1 PR Reviews Restore Strategy
**File:** `src/operations/restore/strategies/pr_reviews_strategy.py`
**Base Class:** `RestoreEntityStrategy`
**Dependencies:** `["pull_requests"]`
**Pattern:** Mirror `src/operations/restore/strategies/comments_strategy.py`

#### 5.2 Review Comments Restore Strategy
**File:** `src/operations/restore/strategies/pr_review_comments_strategy.py`
**Base Class:** `RestoreEntityStrategy`
**Dependencies:** `["pr_reviews"]`
**Pattern:** Mirror PR comments restore strategy

### Step 6: Strategy Factory Integration (Day 3, Afternoon)

#### 6.1 Save Factory Updates
**File:** `src/operations/strategy_factory.py`
**Additions:**
```python
def _create_pr_reviews_strategy(self) -> SaveEntityStrategy:
    return PullRequestReviewsSaveStrategy(selective_mode=self._selective_mode_enabled())

def _create_pr_review_comments_strategy(self) -> SaveEntityStrategy:
    return PullRequestReviewCommentsSaveStrategy(selective_mode=self._selective_mode_enabled())
```

#### 6.2 Restore Factory Updates
**File:** `src/operations/strategy_factory.py`
**Additions:**
```python
def _create_pr_reviews_restore_strategy(self) -> RestoreEntityStrategy:
    return PullRequestReviewsRestoreStrategy(
        conflict_strategy=create_pr_reviews_conflict_strategy(),
        include_original_metadata=self._config.include_original_metadata
    )
```

## Testing Requirements

### Unit Tests (Minimum Viable)
1. **Configuration Validation Tests**
   - File: `tests/unit/test_pr_reviews_validation_unit.py`
   - Test dependency validation rules
   - Test boolean parsing for new environment variables

2. **Strategy Tests**
   - File: `tests/unit/operations/save/strategies/test_pr_reviews_strategy.py`
   - Test dependency handling and coupling logic
   - Test selective filtering integration

### Integration Tests (End of Phase 1)
1. **Basic Feature Test**
   - File: `tests/integration/test_include_pr_reviews_feature.py`
   - Test end-to-end save/restore of PR reviews
   - Test configuration integration

## Success Criteria for Phase 1

- [ ] **Data Models Created**: Both PullRequestReview and PullRequestReviewComment models implemented
- [ ] **Configuration Working**: Environment variables functional with proper validation
- [ ] **Basic Coupling Established**: PR reviews properly coupled with pull requests
- [ ] **Save Strategy Functional**: Can save PR reviews following parent-child patterns
- [ ] **Restore Strategy Functional**: Can restore PR reviews with proper dependencies
- [ ] **Factory Integration Complete**: Strategies properly registered and instantiated
- [ ] **Unit Tests Passing**: Core validation and strategy tests working
- [ ] **Integration Test Passing**: Basic end-to-end functionality verified

## Implementation Notes

### Critical Pattern Adherence
1. **Mirror Existing Patterns Exactly**: Use identical structure to issues/comments
2. **Use Existing Mixins**: Leverage EntityCouplingMixin and SelectiveFilteringMixin
3. **Follow Dependency Patterns**: Same validation logic as INCLUDE_ISSUE_COMMENTS
4. **Test Pattern Consistency**: Copy and adapt existing test structures

### Development Commands for Phase 1
```bash
# Quick validation during development
make test-fast

# Full validation before phase completion
make check

# Run specific unit tests
pdm run pytest tests/unit/test_pr_reviews_validation_unit.py -v

# Run integration test for reviews
pdm run pytest tests/integration/test_include_pr_reviews_feature.py -v
```

### Files Created in Phase 1 (6 new files)
1. `src/entities/pr_reviews/models.py`
2. `src/entities/pr_reviews/__init__.py`
3. `src/entities/pr_review_comments/models.py`
4. `src/entities/pr_review_comments/__init__.py`
5. `src/operations/save/strategies/pr_reviews_strategy.py`
6. `src/operations/restore/strategies/pr_reviews_strategy.py`

### Files Modified in Phase 1 (3 files)
1. `src/config/settings.py` - Add environment variables and validation
2. `src/operations/strategy_factory.py` - Add strategy creation methods
3. `src/github/services/repository_service.py` - Add basic API methods

## Risk Mitigation

### Technical Risks
1. **Pattern Divergence**: Strict adherence to existing patterns mitigates this
2. **API Integration**: Use existing GraphQL patterns and error handling
3. **Dependency Chain**: Follow proven EntityCouplingMixin patterns

### Quality Risks
1. **Test Coverage**: Mirror existing test structure exactly
2. **Configuration Bugs**: Extensive validation testing required

## Next Steps After Phase 1

Once Phase 1 is complete:
1. Validate all tests pass with `make check`
2. Run basic container test to ensure Docker integration works
3. Begin Phase 2: Advanced Features and Integration
4. Focus on metadata integration and converter functions

## Estimated Timeline

**Day 1:** Data models and configuration (6-8 hours)
**Day 2:** API integration and save strategies (6-8 hours)  
**Day 3:** Restore strategies and factory integration (6-8 hours)

**Total Phase 1 Duration:** 2-3 days