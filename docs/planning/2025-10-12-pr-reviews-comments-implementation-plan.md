# Implementation Plan: Pull Request Reviews and Review Comments Feature

**Date:** 2025-10-12  
**Version:** 1.0  
**Status:** Ready for Implementation  
**Based on:** [2025-10-12-pr-reviews-comments-feature-prd.md](./2025-10-12-pr-reviews-comments-feature-prd.md)

## Executive Summary

This implementation plan provides a detailed roadmap for adding PR reviews and review comments support to the GitHub Data project. The implementation follows established architectural patterns from the existing issue→comment and PR→comment relationships, ensuring consistency and leveraging proven frameworks.

## Implementation Strategy

### Architecture Consistency Requirements

The implementation MUST mirror existing patterns exactly:

1. **PR Reviews** → Mirror **Issues** patterns (parent entities)
2. **Review Comments** → Mirror **Issue Comments** patterns (child entities)  
3. **Review Dependencies** → Mirror **Issue-Comment Dependencies** patterns
4. **Configuration** → Mirror **INCLUDE_ISSUES/INCLUDE_ISSUE_COMMENTS** patterns

### Key Architectural Components to Leverage

- `EntityCouplingMixin` - For review→comment relationships
- `SelectiveFilteringMixin` - For PR-based filtering  
- Strategy pattern framework - Existing save/restore template methods
- Configuration validation - Existing dependency enforcement
- Metadata integration - Existing comment body appendix patterns

## Phase 1: Foundation and PR Reviews Support

### 1.1 Data Models and Entities

**Create Review Entity Model**
- **File:** `src/entities/pr_reviews/models.py`
- **Pattern:** Mirror `src/entities/issues/models.py`
- **Key Fields:**
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

**Create Review Comments Entity Model**
- **File:** `src/entities/pr_review_comments/models.py`
- **Pattern:** Mirror `src/entities/comments/models.py`
- **Key Fields:**
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

### 1.2 Configuration Extensions

**Environment Variables**
- **File:** `src/config/settings.py`
- **Add:**
  ```python
  include_pr_reviews: bool = parse_boolean_env_var("INCLUDE_PR_REVIEWS", default=True)
  include_pr_review_comments: bool = parse_boolean_env_var("INCLUDE_PR_REVIEW_COMMENTS", default=True)
  ```

**Dependency Validation**
- **Pattern:** Mirror existing `INCLUDE_ISSUE_COMMENTS` validation
- **Rules:**
  - `INCLUDE_PR_REVIEWS=true` requires `INCLUDE_PULL_REQUESTS=true`
  - `INCLUDE_PR_REVIEW_COMMENTS=true` requires `INCLUDE_PR_REVIEWS=true`
  - `INCLUDE_PR_REVIEW_COMMENTS=true` requires `INCLUDE_PULL_REQUESTS=true`

### 1.3 GitHub API Integration

**GraphQL Query Extensions**
- **File:** `src/github/queries/pull_requests.py`
- **Add review and review comments fields to existing PR queries**
- **Pattern:** Mirror issue comments query structure

**Service Method Extensions**
- **File:** `src/github/services/repository_service.py`
- **New Methods:**
  ```python
  def get_pull_request_reviews(self, repo_name: str, pr_number: int) -> List[Dict[str, Any]]
  def get_pull_request_review_comments(self, repo_name: str, review_id: str) -> List[Dict[str, Any]]
  def create_pull_request_review(self, repo_name: str, pr_number: int, body: str, state: str) -> Dict[str, Any]
  def create_pull_request_review_comment(self, repo_name: str, review_id: str, body: str) -> Dict[str, Any]
  ```

### 1.4 Save Strategy Implementation

**PR Reviews Save Strategy**
- **File:** `src/operations/save/strategies/pr_reviews_strategy.py`
- **Base Class:** `EntityCouplingMixin + SaveEntityStrategy`
- **Dependencies:** `["pull_requests"]`
- **Pattern:** Identical to `CommentsSaveStrategy` but for reviews

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

**Review Comments Save Strategy**  
- **File:** `src/operations/save/strategies/pr_review_comments_strategy.py`
- **Base Class:** `EntityCouplingMixin + SaveEntityStrategy`
- **Dependencies:** `["pr_reviews", "pull_requests"]`
- **Pattern:** Identical to issue comments but with review dependency

### 1.5 Restore Strategy Implementation

**PR Reviews Restore Strategy**
- **File:** `src/operations/restore/strategies/pr_reviews_strategy.py`
- **Base Class:** `RestoreEntityStrategy`
- **Dependencies:** `["pull_requests"]`
- **Pattern:** Mirror `src/operations/restore/strategies/comments_strategy.py`

**Review Comments Restore Strategy**
- **File:** `src/operations/restore/strategies/pr_review_comments_strategy.py`  
- **Base Class:** `RestoreEntityStrategy`
- **Dependencies:** `["pr_reviews"]`
- **Pattern:** Mirror PR comments restore strategy

### 1.6 Strategy Factory Integration

**File:** `src/operations/strategy_factory.py`

**Save Factory Updates:**
```python
def _create_pr_reviews_strategy(self) -> SaveEntityStrategy:
    return PullRequestReviewsSaveStrategy(selective_mode=self._selective_mode_enabled())

def _create_pr_review_comments_strategy(self) -> SaveEntityStrategy:
    return PullRequestReviewCommentsSaveStrategy(selective_mode=self._selective_mode_enabled())
```

**Restore Factory Updates:**
```python
def _create_pr_reviews_restore_strategy(self) -> RestoreEntityStrategy:
    return PullRequestReviewsRestoreStrategy(
        conflict_strategy=create_pr_reviews_conflict_strategy(),
        include_original_metadata=self._config.include_original_metadata
    )
```

## Phase 2: Advanced Features and Integration

### 2.1 Metadata Integration

**Review Metadata Footer**
- **File:** `src/github/metadata.py`
- **Function:** `add_pr_review_metadata_footer(review: PullRequestReview) -> str`
- **Pattern:** Mirror `add_comment_metadata_footer`

**Review Comment Metadata Footer**
- **Function:** `add_pr_review_comment_metadata_footer(comment: PullRequestReviewComment) -> str`
- **Include:** Original path, line number, author, timestamps

### 2.2 Converter Functions

**PR Review Converter**
- **File:** `src/operations/save/converters.py`
- **Function:** `convert_to_pr_review(api_data: Dict[str, Any]) -> PullRequestReview`

**PR Review Comment Converter**
- **Function:** `convert_to_pr_review_comment(api_data: Dict[str, Any]) -> PullRequestReviewComment`

### 2.3 Selective Filtering Integration

**Configuration Builder Extensions**
- **File:** `tests/shared/builders/config_builder.py`
- **Add:** PR reviews and review comments to environment variable mapping

**Selective Mode Detection**
- **File:** `src/operations/strategy_factory.py`
- **Update:** `_selective_mode_enabled()` to include PR review variables

## Phase 3: Testing and Quality Assurance

### 3.1 Unit Tests

**Strategy Tests**
- **Files:**
  - `tests/unit/operations/save/strategies/test_pr_reviews_strategy.py`
  - `tests/unit/operations/save/strategies/test_pr_review_comments_strategy.py`
  - `tests/unit/operations/restore/strategies/test_pr_reviews_strategy.py`
  - `tests/unit/operations/restore/strategies/test_pr_review_comments_strategy.py`

**Configuration Tests**
- **Files:**
  - `tests/unit/test_pr_reviews_validation_unit.py`
  - `tests/unit/test_pr_review_comments_validation_unit.py`

### 3.2 Integration Tests

**Feature Tests**
- **Files:**
  - `tests/integration/test_include_pr_reviews_feature.py`
  - `tests/integration/test_include_pr_review_comments_feature.py`
  - `tests/integration/test_pr_review_coupling.py`

**End-to-End Tests**
- **File:** `tests/integration/test_pr_reviews_feature_end_to_end.py`

### 3.3 Container Tests

**Workflow Tests**
- **File:** `tests/container/test_pr_reviews_container_workflows.py`
- **Include:** Full save/restore cycles with various configurations

## Implementation Dependencies

### Internal Dependencies Required

1. **Existing Pull Request Infrastructure**
   - `src/entities/pull_requests/models.py`
   - `src/operations/save/strategies/pull_requests_strategy.py`
   - `src/operations/restore/strategies/pull_requests_strategy.py`

2. **Strategy Framework Components**
   - `EntityCouplingMixin` (parent-child relationships)
   - `SelectiveFilteringMixin` (PR-based filtering)
   - `SaveEntityStrategy` and `RestoreEntityStrategy` base classes

3. **Configuration Infrastructure**  
   - `src/config/settings.py` boolean parsing
   - Dependency validation framework
   - Strategy factory configuration integration

### External API Dependencies

1. **GitHub GraphQL API v4**
   - Pull request reviews endpoint
   - Review comments endpoint with code context

2. **GitHub REST API v3**
   - Fallback endpoints for review operations
   - Review creation endpoints

## Risk Mitigation

### Technical Risks

1. **API Rate Limiting**
   - **Mitigation:** Leverage existing rate limiting infrastructure
   - **Implementation:** Use same patterns as issue comments

2. **Code Context Loss**
   - **Mitigation:** Store original path/line in metadata
   - **Implementation:** Best-effort restoration with graceful degradation

3. **Complex Dependencies**
   - **Mitigation:** Follow existing parent-child patterns exactly
   - **Implementation:** Use proven EntityCouplingMixin patterns

### Quality Risks

1. **Pattern Divergence**
   - **Mitigation:** Strict adherence to existing patterns
   - **Implementation:** Use identical mixins and base classes

2. **Test Coverage Gaps**
   - **Mitigation:** Mirror existing test structure exactly
   - **Implementation:** Copy and adapt existing test patterns

## Success Criteria

### Phase 1 Complete
- [ ] PR reviews save/restore working end-to-end
- [ ] Configuration variables functional with validation
- [ ] Basic coupling with pull requests established
- [ ] Unit and integration tests passing

### Phase 2 Complete  
- [ ] Review comments save/restore working end-to-end
- [ ] Metadata integration preserving original context
- [ ] Full dependency chain PR→Reviews→Comments working
- [ ] Selective filtering operational

### Phase 3 Complete
- [ ] Comprehensive test suite covering all scenarios
- [ ] Container integration tests passing
- [ ] Performance validation for large repositories
- [ ] Documentation and examples completed

## Timeline Estimate

### Phase 1: Foundation (2-3 days)
- Data models and configuration: 1 day
- Save strategies implementation: 1 day  
- Basic testing and validation: 1 day

### Phase 2: Advanced Features (2-3 days)
- Restore strategies implementation: 1 day
- Metadata integration and converters: 1 day
- Integration testing: 1 day

### Phase 3: Quality Assurance (1-2 days)
- Comprehensive test suite: 1 day
- Container tests and performance validation: 1 day

**Total Estimated Duration:** 5-8 days

## Files to Create/Modify

### New Files (12)
1. `src/entities/pr_reviews/models.py`
2. `src/entities/pr_reviews/__init__.py`  
3. `src/entities/pr_review_comments/models.py`
4. `src/entities/pr_review_comments/__init__.py`
5. `src/operations/save/strategies/pr_reviews_strategy.py`
6. `src/operations/save/strategies/pr_review_comments_strategy.py`
7. `src/operations/restore/strategies/pr_reviews_strategy.py`
8. `src/operations/restore/strategies/pr_review_comments_strategy.py`
9. `tests/unit/test_pr_reviews_validation_unit.py`
10. `tests/unit/test_pr_review_comments_validation_unit.py`
11. `tests/integration/test_include_pr_reviews_feature.py`
12. `tests/integration/test_include_pr_review_comments_feature.py`

### Modified Files (8)
1. `src/config/settings.py` - Add new environment variables
2. `src/operations/strategy_factory.py` - Add strategy creation methods
3. `src/github/queries/pull_requests.py` - Extend GraphQL queries
4. `src/github/services/repository_service.py` - Add API methods
5. `src/github/metadata.py` - Add metadata functions
6. `src/operations/save/converters.py` - Add converter functions
7. `tests/shared/builders/config_builder.py` - Add env var mappings
8. `tests/container/test_selective_container_workflows.py` - Add new scenarios

## Next Steps

1. **Immediate Actions:**
   - Create Phase 1 data models and configuration
   - Implement PR reviews save strategy following existing patterns
   - Add basic configuration validation

2. **Follow-up Actions:**
   - Extend GitHub API integration for reviews
   - Implement restore strategies  
   - Build comprehensive test suite

3. **Validation Steps:**
   - Run `make test-fast` after each major component
   - Run `make check` before phase completion
   - Validate container workflows end-to-end

This implementation plan ensures architectural consistency while delivering the complete PR reviews and review comments feature as specified in the PRD.