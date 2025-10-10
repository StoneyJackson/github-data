# Phase 2 Implementation Plan: Selective Issue/PR Numbers Feature

**Document**: Implementation Plan  
**Date**: 2025-10-10  
**Status**: Ready for Implementation  
**Author**: Claude Code  
**Related**: [Feature PRD](./2025-10-10-selective-issue-pr-numbers-feature-prd.md), [Phase 1 Plan](./2025-10-10-phase-1-implementation-plan.md)

## Phase 2 Overview

Phase 2 focuses on integrating the number specification parsing from Phase 1 into the save/restore operations. This includes updating data collection logic, implementing selective filtering, and ensuring comment coupling works correctly.

### Phase 2 Goals

1. ✅ Update save operation filtering for selective issue/PR processing
2. ✅ Update restore operation filtering for selective issue/PR processing  
3. ✅ Implement comment coupling logic
4. ✅ Add integration tests for end-to-end workflows
5. ✅ Performance optimization for selective operations

## Implementation Tasks

### Task 1: Update Save Operation Filtering

**File**: `src/operations/save/save.py`

**Current State Analysis**:
- Save operations currently use boolean flags (`include_issues`, `include_pull_requests`)
- All issues/PRs are fetched via `get_repository_issues()` and `get_repository_pull_requests()`
- No selective filtering based on issue/PR numbers
- Config integration exists but doesn't utilize `Union[bool, set[int]]` types

**Required Changes**:

1. **Update Function Signatures**:
```python
# Current
def save_repository_data_with_config(
    config: ApplicationConfig,
    # ... other params
) -> None:

# Enhanced to handle Union types
def save_repository_data_with_config(
    config: ApplicationConfig,
    # ... other params
) -> None:
    """Save repository data with selective issue/PR filtering support."""
```

2. **Add Selective Filtering Helper**:
```python
def _should_include_issue(issue_data: Dict[str, Any], include_spec: Union[bool, Set[int]]) -> bool:
    """Determine if issue should be included based on specification.
    
    Args:
        issue_data: Issue data dict with 'number' field
        include_spec: Boolean (all/none) or set of specific numbers
        
    Returns:
        True if issue should be included, False otherwise
    """
    if isinstance(include_spec, bool):
        return include_spec
    else:
        return issue_data.get('number') in include_spec

def _should_include_pull_request(pr_data: Dict[str, Any], include_spec: Union[bool, Set[int]]) -> bool:
    """Determine if pull request should be included based on specification.
    
    Args:
        pr_data: PR data dict with 'number' field
        include_spec: Boolean (all/none) or set of specific numbers
        
    Returns:
        True if PR should be included, False otherwise
    """
    if isinstance(include_spec, bool):
        return include_spec
    else:
        return pr_data.get('number') in include_spec
```

3. **Update Data Collection Logic**:
```python
# Issues processing
if isinstance(config.include_issues, bool):
    if config.include_issues:
        # Existing behavior: fetch all issues
        issues_data = github_service.get_repository_issues(repo_name)
    else:
        # Skip all issues
        issues_data = []
else:
    # Selective processing: fetch all but filter
    all_issues = github_service.get_repository_issues(repo_name)
    issues_data = [
        issue for issue in all_issues 
        if _should_include_issue(issue, config.include_issues)
    ]

# Pull requests processing (similar pattern)
if isinstance(config.include_pull_requests, bool):
    if config.include_pull_requests:
        prs_data = github_service.get_repository_pull_requests(repo_name)
    else:
        prs_data = []
else:
    all_prs = github_service.get_repository_pull_requests(repo_name)
    prs_data = [
        pr for pr in all_prs 
        if _should_include_pull_request(pr, config.include_pull_requests)
    ]
```

4. **Implement Comment Coupling**:
```python
def _filter_issue_comments(
    comments_data: List[Dict[str, Any]], 
    included_issues: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Filter issue comments to only include comments from selected issues.
    
    Args:
        comments_data: All issue comments from repository
        included_issues: Issues that were selected for inclusion
        
    Returns:
        Filtered list of comments from selected issues only
    """
    included_issue_urls = {issue.get('url') for issue in included_issues}
    return [
        comment for comment in comments_data
        if comment.get('issue_url') in included_issue_urls
    ]

def _filter_pr_comments(
    comments_data: List[Dict[str, Any]], 
    included_prs: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Filter PR comments to only include comments from selected PRs."""
    included_pr_urls = {pr.get('url') for pr in included_prs}
    return [
        comment for comment in comments_data
        if comment.get('pull_request_url') in included_pr_urls
    ]
```

**Performance Optimizations**:
- Consider adding GitHub API filtering in future (not in Phase 2 scope)
- Use generator expressions for memory efficiency with large datasets
- Add logging for selective operation performance metrics

### Task 2: Update Restore Operation Filtering

**File**: `src/operations/restore/restore.py`

**Current State Analysis**:
- Restore operations read all JSON data and process based on boolean flags
- No selective filtering during restore based on issue/PR numbers
- Config integration exists but doesn't utilize selective specifications

**Required Changes**:

1. **Update Restore Logic**:
```python
def restore_repository_data_with_config(
    config: ApplicationConfig,
    # ... other params
) -> None:
    """Restore repository data with selective issue/PR filtering support."""
    
    # Issues restoration
    if isinstance(config.include_issues, bool):
        if config.include_issues:
            # Restore all issues from JSON
            restore_all_issues(storage_service, github_service, repo_name)
        # If False, skip issues entirely
    else:
        # Selective restoration: filter JSON data
        restore_selective_issues(
            storage_service, github_service, repo_name, config.include_issues
        )
    
    # Pull requests restoration (similar pattern)
    if isinstance(config.include_pull_requests, bool):
        if config.include_pull_requests:
            restore_all_pull_requests(storage_service, github_service, repo_name)
    else:
        restore_selective_pull_requests(
            storage_service, github_service, repo_name, config.include_pull_requests
        )
```

2. **Add Selective Restore Functions**:
```python
def restore_selective_issues(
    storage_service: StorageService,
    github_service: RepositoryService, 
    repo_name: str,
    issue_numbers: Set[int]
) -> None:
    """Restore only specified issues from saved data.
    
    Args:
        storage_service: Service for reading saved data
        github_service: Service for GitHub API operations
        repo_name: Repository name
        issue_numbers: Set of issue numbers to restore
    """
    # Load saved issues data
    all_issues_data = storage_service.read_data('issues.json')
    
    # Filter to only selected issues
    selected_issues = [
        issue for issue in all_issues_data
        if issue.get('number') in issue_numbers
    ]
    
    # Log selection results
    found_numbers = {issue.get('number') for issue in selected_issues}
    missing_numbers = issue_numbers - found_numbers
    if missing_numbers:
        print(f"Warning: Issues not found in saved data: {sorted(missing_numbers)}")
    
    # Restore filtered issues
    for issue in selected_issues:
        github_service.create_issue(repo_name, issue)

def restore_selective_pull_requests(
    storage_service: StorageService,
    github_service: RepositoryService, 
    repo_name: str,
    pr_numbers: Set[int]
) -> None:
    """Restore only specified pull requests from saved data."""
    # Similar implementation to restore_selective_issues
    # but for pull requests
```

3. **Update Comment Restoration Coupling**:
```python
def restore_selective_issue_comments(
    storage_service: StorageService,
    github_service: RepositoryService,
    repo_name: str,
    restored_issues: List[Dict[str, Any]]
) -> None:
    """Restore comments only for issues that were restored.
    
    Args:
        storage_service: Service for reading saved data
        github_service: Service for GitHub API operations
        repo_name: Repository name
        restored_issues: Issues that were successfully restored
    """
    # Load all saved comments
    all_comments_data = storage_service.read_data('issue_comments.json')
    
    # Create mapping of original issue URLs to restored issue URLs
    url_mapping = create_issue_url_mapping(restored_issues)
    
    # Filter and restore comments for restored issues only
    for comment in all_comments_data:
        original_issue_url = comment.get('issue_url')
        if original_issue_url in url_mapping:
            # Update comment to reference new issue URL
            comment['issue_url'] = url_mapping[original_issue_url]
            github_service.create_issue_comment(repo_name, comment)
```

### Task 3: Enhanced Configuration Integration

**File**: `src/operations/save/save.py` and `src/operations/restore/restore.py`

**Required Changes**:

1. **Remove Legacy Interface Support**:
```python
# BREAKING CHANGE: Remove backward compatibility functions
# These functions will be deprecated and removed:
# - save_repository_data_with_strategy_pattern()
# - Any functions using direct boolean parameters instead of config

# All operations must use ApplicationConfig for consistent behavior
```

2. **Add Configuration Validation**:
```python
def validate_save_config(config: ApplicationConfig) -> None:
    """Validate configuration for save operations.
    
    Args:
        config: Application configuration
        
    Raises:
        ValueError: For invalid save-specific configurations
    """
    # Validate number specifications contain valid issue/PR numbers
    if isinstance(config.include_issues, set):
        if not config.include_issues:
            raise ValueError("INCLUDE_ISSUES number specification cannot be empty")
    
    if isinstance(config.include_pull_requests, set):
        if not config.include_pull_requests:
            raise ValueError("INCLUDE_PULL_REQUESTS number specification cannot be empty")
    
    # Validate comment coupling logic
    if config.include_issue_comments and isinstance(config.include_issues, bool):
        if not config.include_issues:
            print("Warning: INCLUDE_ISSUE_COMMENTS=true but INCLUDE_ISSUES=false. Comments will be skipped.")

def validate_restore_config(config: ApplicationConfig) -> None:
    """Validate configuration for restore operations."""
    # Similar validation logic for restore-specific requirements
```

### Task 4: GitHub API Integration Updates

**Files**: `src/github/service.py`, `src/github/boundary.py`

**Enhancement Options** (Optional - Performance Optimization):

1. **API Query Optimization** (Future enhancement):
```python
# This is beyond Phase 2 scope but documented for future enhancement
def get_repository_issues_selective(
    self, 
    repo_name: str, 
    issue_numbers: Optional[Set[int]] = None
) -> List[Dict[str, Any]]:
    """Get specific issues by number to reduce API calls.
    
    Note: GitHub API doesn't support filtering by issue numbers in a single call,
    so this would require multiple individual API calls. May not be more efficient
    than fetching all and filtering locally for typical use cases.
    """
```

2. **Current Approach** (Phase 2):
- Fetch all issues/PRs as currently implemented
- Filter in application layer based on number specifications
- This approach maintains API call efficiency for most use cases
- Selective filtering provides memory and processing benefits

### Task 5: Integration Testing

**File**: `tests/integration/test_selective_save_restore.py`

**Test Categories**:

1. **Selective Save Tests**:
```python
def test_save_single_issue_with_comments():
    """Test saving a single issue and its comments."""
    # Setup: Repository with multiple issues
    # Config: INCLUDE_ISSUES="5", INCLUDE_ISSUE_COMMENTS=true
    # Verify: Only issue #5 and its comments are saved

def test_save_issue_range_without_comments():
    """Test saving issue range without comments."""
    # Config: INCLUDE_ISSUES="1-3", INCLUDE_ISSUE_COMMENTS=false
    # Verify: Issues #1, #2, #3 saved without any comments

def test_save_mixed_specification():
    """Test combined issue and PR selection."""
    # Config: INCLUDE_ISSUES="1-3 5", INCLUDE_PULL_REQUESTS="10-12"
    # Verify: Correct issues and PRs saved with proper coupling
```

2. **Selective Restore Tests**:
```python
def test_restore_selective_issues_from_full_backup():
    """Test restoring specific issues from complete backup."""
    # Setup: Complete repository backup with all issues/PRs
    # Config: INCLUDE_ISSUES="2 4 6" for restore
    # Verify: Only specified issues restored

def test_restore_missing_issue_numbers():
    """Test restore behavior when specified numbers don't exist."""
    # Setup: Backup with issues #1-5
    # Config: INCLUDE_ISSUES="3 7 9" (7, 9 don't exist)
    # Verify: Issue #3 restored, warning logged for missing numbers
```

3. **Comment Coupling Tests**:
```python
def test_comment_coupling_selective_save():
    """Test that comments are only saved for selected issues."""
    # Setup: Repository with issues #1-5, each with comments
    # Config: INCLUDE_ISSUES="2 4", INCLUDE_ISSUE_COMMENTS=true
    # Verify: Only comments from issues #2 and #4 are saved

def test_comment_coupling_selective_restore():
    """Test that comments are only restored for restored issues."""
    # Setup: Backup with all issues and comments
    # Config: INCLUDE_ISSUES="1 3" for restore
    # Verify: Only comments for issues #1 and #3 are restored
```

4. **Performance Tests**:
```python
def test_selective_save_performance():
    """Test that selective operations are more efficient."""
    # Setup: Large repository (100+ issues)
    # Config: INCLUDE_ISSUES="1-5" vs INCLUDE_ISSUES=true
    # Verify: Selective save processes significantly less data

def test_selective_restore_memory_usage():
    """Test memory efficiency of selective restore."""
    # Verify: Memory usage scales with selected items, not total backup size
```

**File**: `tests/integration/test_comment_coupling.py`

**Test Categories**:

1. **Issue Comment Coupling**:
```python
def test_issue_comments_follow_issue_selection():
    """Verify issue comments are automatically coupled to issue selection."""

def test_issue_comments_disabled_overrides_selection():
    """Verify INCLUDE_ISSUE_COMMENTS=false disables comments regardless of issue selection."""
```

2. **PR Comment Coupling**:
```python
def test_pr_comments_follow_pr_selection():
    """Verify PR comments are automatically coupled to PR selection."""

def test_pr_comments_disabled_overrides_selection():
    """Verify INCLUDE_PULL_REQUEST_COMMENTS=false disables comments regardless of PR selection."""
```

### Task 6: Error Handling and Edge Cases

**Error Scenarios to Handle**:

1. **Missing Data Scenarios**:
```python
def handle_missing_issue_data(issue_numbers: Set[int], available_data: List[Dict]) -> tuple:
    """Handle cases where specified issues don't exist in saved data.
    
    Returns:
        (found_issues, missing_numbers) for logging and user feedback
    """
```

2. **API Error Scenarios**:
```python
def handle_selective_restore_api_errors(
    issues_to_restore: List[Dict], 
    github_service: RepositoryService
) -> Dict[str, Any]:
    """Handle API errors during selective restore operations.
    
    Returns:
        Summary of successful/failed restore operations
    """
```

3. **Configuration Validation**:
```python
def validate_number_specification_against_data(
    specification: Set[int], 
    available_data: List[Dict],
    data_type: str
) -> None:
    """Validate that specified numbers exist in available data."""
```

## Implementation Order

### Step 1: Save Operation Updates
1. Update `save_repository_data_with_config()` function
2. Add selective filtering helper functions
3. Implement comment coupling for save operations
4. Add configuration validation for save operations

### Step 2: Restore Operation Updates  
1. Update `restore_repository_data_with_config()` function
2. Add selective restore functions
3. Implement comment coupling for restore operations
4. Add configuration validation for restore operations

### Step 3: Integration Testing
1. Create comprehensive integration tests
2. Add comment coupling tests
3. Add performance and edge case tests
4. Validate end-to-end workflows

### Step 4: Error Handling and Optimization
1. Add comprehensive error handling
2. Implement performance optimizations
3. Add logging and user feedback
4. Validate memory usage and efficiency

## Testing Strategy

### Integration Test Coverage
- **Save Operations**: Selective filtering, comment coupling, configuration validation
- **Restore Operations**: Selective restoration, missing data handling, comment coupling
- **End-to-End Workflows**: Complete save/restore cycles with various specifications
- **Performance**: Memory usage, processing efficiency, API call optimization

### Test Execution
```bash
# Run Phase 2 integration tests
make test-integration  # Integration tests
pytest tests/integration/test_selective* -v  # Specific selective tests

# Performance validation
pytest tests/integration/test_selective* -k performance -v

# Full validation
make test-fast  # All tests except container tests
make check      # Full quality validation
```

### Test Performance Targets
- Integration tests should complete in < 30 seconds total
- Individual integration test methods should complete in < 5 seconds
- Selective operations should show measurable performance improvements
- Memory usage should scale with selected items, not total repository size

## Success Criteria

### Functional Requirements
- ✅ Save operations filter issues/PRs based on number specifications
- ✅ Restore operations filter data based on number specifications  
- ✅ Comments are properly coupled to their parent issue/PR selection
- ✅ Missing numbers are handled gracefully with appropriate warnings
- ✅ Boolean behavior (all/none) continues to work as before

### Quality Requirements
- ✅ 100% integration test coverage for new selective functionality
- ✅ All existing tests continue to pass (backward compatibility)
- ✅ Code quality passes with `make check`
- ✅ Clear error messages and user feedback
- ✅ Comprehensive logging for debugging and monitoring

### Performance Requirements
- ✅ Selective operations show measurable efficiency improvements
- ✅ Memory usage scales with selected items, not total data size
- ✅ No performance degradation for existing boolean usage
- ✅ API call patterns remain efficient

## Risk Mitigation

### Data Integrity Risks
- **Risk**: Selective operations might miss dependent data
- **Mitigation**: Comprehensive comment coupling tests, validation functions
- **Monitoring**: Integration tests validate data consistency

### Performance Risks
- **Risk**: Filtering large datasets might be slower than expected
- **Mitigation**: Performance tests, memory usage monitoring
- **Optimization**: Consider streaming/generator patterns for large datasets

### Backward Compatibility Risks
- **Risk**: Changes might break existing workflows
- **Mitigation**: Comprehensive regression testing, gradual deprecation
- **Validation**: All existing tests must pass unchanged

## Dependencies

### Internal Dependencies
- Phase 1 completion: NumberSpecificationParser implementation
- Enhanced ApplicationConfig with Union[bool, Set[int]] types
- Existing save/restore infrastructure
- Test fixtures and shared infrastructure

### External Dependencies
- No new external dependencies required
- Relies on existing GitHub API client infrastructure
- Uses standard library facilities only

## Deliverables

### Code Deliverables
1. Updated `src/operations/save/save.py` - Selective save operations
2. Updated `src/operations/restore/restore.py` - Selective restore operations
3. `tests/integration/test_selective_save_restore.py` - Integration tests
4. `tests/integration/test_comment_coupling.py` - Comment coupling tests

### Documentation Deliverables
- Updated function docstrings for all modified operations
- Error handling documentation
- Performance characteristics documentation

### Validation Deliverables
- 100% passing integration tests
- Performance benchmarks
- Memory usage validation
- Backward compatibility validation

## Next Steps (Phase 3 Preview)

After Phase 2 completion:
1. **Documentation**: Update README and CLAUDE.md with examples
2. **Container Tests**: End-to-end Docker workflow testing
3. **Performance**: Advanced API optimization and caching
4. **CLI Enhancements**: Better user feedback and validation

---

**Status**: Ready for Implementation  
**Estimated Effort**: 3-4 development days  
**Risk Level**: Medium (integration complexity, performance considerations)