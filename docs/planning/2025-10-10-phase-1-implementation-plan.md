# Phase 1 Implementation Plan: Selective Issue/PR Numbers Feature

**Document**: Implementation Plan  
**Date**: 2025-10-10  
**Status**: Ready for Implementation  
**Author**: Claude Code  
**Related**: [Feature PRD](./2025-10-10-selective-issue-pr-numbers-feature-prd.md)

## Phase 1 Overview

Phase 1 focuses on implementing the core infrastructure for parsing and handling number specifications. This includes the number parser component, configuration updates, and comprehensive unit tests.

### Phase 1 Goals

1. ✅ Implement `NumberSpecificationParser` class
2. ✅ Update `ApplicationConfig` parsing logic  
3. ✅ Add comprehensive unit tests
4. ✅ Update configuration validation

## Implementation Tasks

### Task 1: Create NumberSpecificationParser

**File**: `src/config/number_parser.py`

**Implementation Details**:

```python
class NumberSpecificationParser:
    """Parse number specifications for selective issue/PR processing."""
    
    @staticmethod
    def parse(specification: str) -> set[int]:
        """Parse number specification into set of integers.
        
        Supports:
        - Single numbers: "5" → {5}
        - Number lists: "1 3 5", "1,3,5", "1, 3, 5" → {1, 3, 5}
        - Ranges: "1-5" → {1, 2, 3, 4, 5}
        - Combined: "1-3 5", "1-3,5", "1-3, 5" → {1, 2, 3, 5}
        
        Args:
            specification: Number specification string
            
        Returns:
            Set of integers specified
            
        Raises:
            ValueError: For invalid formats or ranges
        """
        
    @staticmethod  
    def is_boolean_value(value: str) -> bool:
        """Check if value is a boolean specification.
        
        Args:
            value: String value to check
            
        Returns:
            True if value represents a boolean, False otherwise
        """
        
    @staticmethod
    def parse_boolean_value(value: str) -> bool:
        """Parse boolean value (true/false).
        
        Supports case-insensitive:
        - True values: "true", "yes", "on"
        - False values: "false", "no", "off"
        
        Args:
            value: Boolean string to parse
            
        Returns:
            Boolean value
            
        Raises:
            ValueError: If value is not a valid boolean
        """
```

**Key Features**:
- Parse single numbers, ranges, and combinations
- Handle multiple delimiters (spaces, commas, mixed)
- Validate number formats and ranges
- Support boolean fallback detection
- Clear error messages for invalid formats

**Validation Rules**:
- Numbers must be positive integers (≥ 1)
- Ranges must have start ≤ end
- No duplicate numbers in output set
- Empty specifications are invalid

### Task 2: Update ApplicationConfig

**File**: `src/config/settings.py`

**Current State Analysis**:
- Current config uses `bool` types for `include_issues` and `include_pull_requests`
- Boolean parsing via `_parse_bool_env()` supports: "true", "1", "yes", "on" for True
- Boolean parsing supports: "false", "0", "no", "off" for False

**Required Changes**:

1. **Update Type Annotations**:
```python
# Current
include_issues: bool
include_pull_requests: bool

# New
include_issues: Union[bool, set[int]]
include_pull_requests: Union[bool, set[int]]
```

2. **Create New Parsing Methods**:
```python
@classmethod
def _parse_number_or_bool_env(cls, key: str, default: bool = False) -> Union[bool, set[int]]:
    """Parse environment variable as number specification or boolean.
    
    Args:
        key: Environment variable name
        default: Default boolean value if variable not set
        
    Returns:
        Boolean for all/none behavior, or set of integers for selective behavior
        
    Raises:
        ValueError: For invalid number specifications
    """
```

3. **Remove Legacy Boolean Support**:
- **BREAKING CHANGE**: Remove support for "0" and "1" as boolean values
- Update all boolean environment variables to use new boolean value formats
- Affected variables: `INCLUDE_GIT_REPO`, `INCLUDE_ISSUE_COMMENTS`, `INCLUDE_PULL_REQUEST_COMMENTS`, `INCLUDE_SUB_ISSUES`

4. **Update from_environment() Method**:
```python
@classmethod
def from_environment(cls) -> "ApplicationConfig":
    """Create configuration from environment variables."""
    return cls(
        # ... existing fields ...
        include_issues=cls._parse_number_or_bool_env("INCLUDE_ISSUES", default=True),
        include_pull_requests=cls._parse_number_or_bool_env("INCLUDE_PULL_REQUESTS", default=True),
        # ... existing fields with updated boolean parsing ...
        include_git_repo=cls._parse_enhanced_bool_env("INCLUDE_GIT_REPO", default=True),
        include_issue_comments=cls._parse_enhanced_bool_env("INCLUDE_ISSUE_COMMENTS", default=True),
        include_pull_request_comments=cls._parse_enhanced_bool_env("INCLUDE_PULL_REQUEST_COMMENTS", default=True),
        include_sub_issues=cls._parse_enhanced_bool_env("INCLUDE_SUB_ISSUES", default=True),
    )
```

5. **Add Enhanced Boolean Parsing**:
```python
@staticmethod
def _parse_enhanced_bool_env(key: str, default: bool = False) -> bool:
    """Parse boolean environment variable with enhanced format support.
    
    Supported formats (case-insensitive):
    - True values: "true", "yes", "on"
    - False values: "false", "no", "off"
    
    Args:
        key: Environment variable name
        default: Default value if variable not set
        
    Returns:
        Boolean value
        
    Raises:
        ValueError: For unsupported boolean formats (e.g., "0", "1")
    """
```

### Task 3: Comprehensive Unit Tests

**File**: `tests/unit/config/test_number_parser.py`

**Test Categories**:

1. **Number Parsing Tests**:
   - Single numbers: `"5"` → `{5}`
   - Multiple numbers (space-separated): `"1 3 5"` → `{1, 3, 5}`
   - Multiple numbers (comma-separated): `"1,3,5"` → `{1, 3, 5}`
   - Multiple numbers (mixed delimiters): `"1, 3, 5"` → `{1, 3, 5}`

2. **Range Parsing Tests**:
   - Simple ranges: `"1-5"` → `{1, 2, 3, 4, 5}`
   - Single number ranges: `"5-5"` → `{5}`
   - Large ranges: `"100-105"` → `{100, 101, 102, 103, 104, 105}`

3. **Combined Format Tests**:
   - Range + numbers: `"1-3 5"` → `{1, 2, 3, 5}`
   - Multiple ranges: `"1-3 8-10"` → `{1, 2, 3, 8, 9, 10}`
   - Complex combinations: `"1-3, 5, 8-10"` → `{1, 2, 3, 5, 8, 9, 10}`

4. **Boolean Detection Tests**:
   - Boolean values: `"true"`, `"false"`, `"yes"`, `"no"`, `"on"`, `"off"`
   - Case insensitivity: `"True"`, `"FALSE"`, `"Yes"`, `"NO"`
   - Non-boolean values: `"1"`, `"5"`, `"1-5"`, `"abc"`

5. **Error Handling Tests**:
   - Invalid ranges: `"5-1"` (end < start)
   - Zero numbers: `"0"`, `"1-0"`
   - Negative numbers: `"-1"`, `"1--3"`
   - Non-numeric: `"abc"`, `"1-abc"`
   - Empty ranges: `"1-"`, `"-5"`
   - Empty input: `""`, `"   "`

6. **Edge Cases**:
   - Whitespace handling: `" 1 , 2 , 3 "`
   - Duplicate numbers: `"1 1 2"` → `{1, 2}`
   - Large numbers: `"999999"`
   - Single character inputs: `"a"`, `" "`

**File**: `tests/unit/config/test_settings.py` (Updates)

**Additional Test Categories**:

1. **Number Specification Environment Variables**:
   - `INCLUDE_ISSUES` with number specifications
   - `INCLUDE_PULL_REQUESTS` with number specifications
   - Return type validation (`Union[bool, set[int]]`)

2. **Enhanced Boolean Environment Variables**:
   - Updated boolean parsing for all boolean variables
   - Deprecation of "0"/"1" formats
   - Error handling for legacy formats

3. **Configuration Validation**:
   - Valid number specifications pass validation
   - Invalid number specifications fail validation
   - Type consistency validation

### Task 4: Update Configuration Validation

**File**: `src/config/settings.py` (validate method updates)

**New Validation Rules**:

1. **Number Specification Validation**:
```python
def validate(self) -> None:
    """Validate configuration values."""
    # ... existing validation ...
    
    # Validate number specifications
    if isinstance(self.include_issues, set):
        if not self.include_issues:
            raise ValueError("INCLUDE_ISSUES number specification cannot be empty")
        if any(n <= 0 for n in self.include_issues):
            raise ValueError("INCLUDE_ISSUES numbers must be positive integers")
    
    if isinstance(self.include_pull_requests, set):
        if not self.include_pull_requests:
            raise ValueError("INCLUDE_PULL_REQUESTS number specification cannot be empty")
        if any(n <= 0 for n in self.include_pull_requests):
            raise ValueError("INCLUDE_PULL_REQUESTS numbers must be positive integers")
```

2. **Comment Coupling Validation**:
```python
    # Enhanced comment dependency validation
    if self.include_issue_comments:
        if isinstance(self.include_issues, bool) and not self.include_issues:
            # Boolean false for issues
            logging.warning(...)
            self.include_issue_comments = False
        elif isinstance(self.include_issues, set) and not self.include_issues:
            # Empty number specification for issues
            logging.warning(...)
            self.include_issue_comments = False
    
    # Similar validation for PR comments
```

## Implementation Order

### Step 1: NumberSpecificationParser
1. Create `src/config/number_parser.py`
2. Implement core parsing logic
3. Add comprehensive error handling
4. Create unit tests in `tests/unit/config/test_number_parser.py`

### Step 2: Enhanced Boolean Parsing
1. Add `_parse_enhanced_bool_env()` method to ApplicationConfig
2. Update all boolean environment variable parsing
3. Add deprecation warnings for "0"/"1" usage
4. Update existing tests for new boolean formats

### Step 3: Number Specification Integration
1. Add `_parse_number_or_bool_env()` method
2. Update `include_issues` and `include_pull_requests` parsing
3. Update type annotations to `Union[bool, set[int]]`
4. Add integration tests

### Step 4: Validation Updates
1. Update `validate()` method for number specifications
2. Enhanced comment coupling validation
3. Add validation tests
4. Error message testing

## Testing Strategy

### Unit Test Coverage
- **NumberSpecificationParser**: 100% line coverage
- **ApplicationConfig parsing**: All new methods covered
- **Error handling**: All error paths tested
- **Edge cases**: Comprehensive boundary testing

### Test Execution
```bash
# Run Phase 1 tests
make test-unit  # Fast unit tests
pytest tests/unit/config/ -v  # Specific config tests

# Full validation
make test-fast  # All tests except container tests
make check      # Full quality validation
```

### Test Performance
- All unit tests should complete in < 5 seconds total
- Individual test methods should complete in < 100ms
- No external dependencies or API calls in Phase 1 tests

## Success Criteria

### Functional Requirements
- ✅ Parse single numbers: `"5"` → `{5}`
- ✅ Parse ranges: `"1-5"` → `{1, 2, 3, 4, 5}`
- ✅ Parse combinations: `"1-3 5"` → `{1, 2, 3, 5}`
- ✅ Handle multiple delimiters: spaces, commas, mixed
- ✅ Detect boolean values: `"true"`, `"false"`, etc.
- ✅ Enhanced boolean parsing for all boolean variables
- ✅ Clear error messages for invalid formats

### Quality Requirements
- ✅ 100% unit test coverage for new code
- ✅ All tests pass with `make test-fast`
- ✅ Code quality passes with `make check`
- ✅ Type annotations are complete and accurate
- ✅ Documentation strings for all public methods

### Performance Requirements
- ✅ Number parsing completes in < 10ms for typical specifications
- ✅ Configuration creation time remains < 50ms
- ✅ Memory usage scales linearly with number specification size

## Risk Mitigation

### Breaking Changes
- **Risk**: "0"/"1" boolean values no longer supported
- **Mitigation**: Clear error messages guide users to new formats
- **Documentation**: Prominent migration guide in README

### Performance Impact
- **Risk**: Set operations slower than boolean comparisons
- **Mitigation**: Benchmark parsing performance, optimize if needed
- **Monitoring**: Performance tests in Phase 2

### Type Safety
- **Risk**: `Union[bool, set[int]]` types complicate logic
- **Mitigation**: Helper methods for type checking
- **Validation**: Comprehensive type testing

## Dependencies

### Internal Dependencies
- Existing `ApplicationConfig` class
- Current test infrastructure
- Shared test fixtures and builders

### External Dependencies
- No new external dependencies required
- Uses standard library only (`re`, `typing`, etc.)

## Deliverables

### Code Deliverables
1. `src/config/number_parser.py` - Complete implementation
2. Updated `src/config/settings.py` - Enhanced configuration
3. `tests/unit/config/test_number_parser.py` - Comprehensive tests
4. Updated `tests/unit/config/test_settings.py` - Enhanced tests

### Documentation Deliverables
- Updated docstrings for all new methods
- Error message documentation
- Type annotation documentation

### Validation Deliverables
- 100% passing unit tests
- Code quality validation passes
- Performance benchmarks established

## Next Steps (Phase 2 Preview)

After Phase 1 completion:
1. **Integration**: Update save/restore operation filtering
2. **Comment Coupling**: Implement selective comment processing
3. **Integration Tests**: End-to-end workflow testing
4. **Performance**: Optimize API call patterns

---

**Status**: Ready for Implementation  
**Estimated Effort**: 2-3 development days  
**Risk Level**: Low (isolated changes, comprehensive testing)