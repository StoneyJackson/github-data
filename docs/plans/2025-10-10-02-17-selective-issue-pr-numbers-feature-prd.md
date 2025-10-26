# Selective Issue and Pull Request Numbers Feature - PRD

**Document**: Product Requirements Document (PRD)  
**Date**: 2025-10-10  
**Status**: Draft  
**Author**: Claude Code  

## Executive Summary

This feature enables users to selectively save and restore specific GitHub issues and pull requests by specifying issue/PR numbers and number ranges through environment variables, rather than the current all-or-nothing boolean approach.

## Problem Statement

### Current Limitations

The existing implementation uses boolean environment variables (`INCLUDE_ISSUES`, `INCLUDE_PULL_REQUESTS`) that operate in an all-or-nothing mode:

- `INCLUDE_ISSUES=true` → Save/restore ALL issues
- `INCLUDE_ISSUES=false` → Skip ALL issues  
- `INCLUDE_PULL_REQUESTS=true` → Save/restore ALL pull requests
- `INCLUDE_PULL_REQUESTS=false` → Skip ALL pull requests

### User Pain Points

1. **Bulk Operations**: Users cannot selectively work with specific issues/PRs
2. **Large Repositories**: Processing hundreds/thousands of issues/PRs when only specific ones are needed
3. **Targeted Workflows**: Migration scenarios requiring only specific issue/PR subsets
4. **Performance Impact**: Unnecessary API calls and data processing for unwanted issues/PRs

### Use Cases

1. **Selective Migration**: Moving specific issues (e.g., #1, #5, #10-15) to a new repository
2. **Incremental Restore**: Restoring only recently created issues/PRs (e.g., #100-110)
3. **Feature-Specific Backup**: Saving issues related to specific milestones or features
4. **Development Workflows**: Working with specific PR ranges during release cycles

## Solution Overview

### Core Concept

Enhance `INCLUDE_ISSUES` and `INCLUDE_PULL_REQUESTS` to support both **boolean and flexible number specification** values:

**Boolean Values**:
- **`"true"`**: Include ALL issues/pull requests (existing behavior)
- **`"false"`**: Skip ALL issues/pull requests (existing behavior)

**Number Specification Values**:
- **Single numbers**: `"1"`, `"5"` - Include only specified issue/PR numbers
- **Number lists**: `"1 2 3"`, `"1,2,3"`, `"1, 2, 3"` - Include multiple specific numbers
- **Number ranges**: `"1-5"`, `"10-20"` - Include contiguous ranges  
- **Combined formats**: `"1-3 5 8-10"`, `"1-3,5,8-10"`, `"1-3, 5, 8-10"` - Mix ranges and individual numbers

### Key Design Principles

1. **Intuitive Syntax**: Natural number specification formats users expect
2. **Flexible Parsing**: Support multiple delimiters (spaces, commas, mixed)
3. **Range Support**: Efficient specification of contiguous number ranges  
4. **Comment Coupling**: Comments are included only for selected issues/PRs
5. **Validation**: Clear error messages for invalid formats
6. **Performance**: Efficient filtering to avoid unnecessary API calls

## Detailed Requirements

### 1. Environment Variable Behavior

#### Current Boolean Handling Elimination

**BREAKING CHANGE**: Remove support for `"0"` and `"1"` as boolean values across all environment variables.

**Rationale**: 
- `"0"` and `"1"` now represent issue/PR numbers to select
- Eliminates ambiguity between boolean and number interpretations
- Improves consistency across all boolean environment variables

**Affected Variables**:
- `INCLUDE_GIT_REPO`
- `INCLUDE_ISSUE_COMMENTS` 
- `INCLUDE_PULL_REQUEST_COMMENTS`
- `INCLUDE_SUB_ISSUES`

**New Boolean Value Support** (all variables):
- **True values**: `"true"`, `"yes"`, `"on"` (case-insensitive)
- **False values**: `"false"`, `"no"`, `"off"` (case-insensitive)

#### INCLUDE_ISSUES Specification

| Format | Example | Description |
|--------|---------|-------------|
| Boolean - All | `INCLUDE_ISSUES="true"` | Save/restore ALL issues |
| Boolean - None | `INCLUDE_ISSUES="false"` | Skip ALL issues |
| Single number | `INCLUDE_ISSUES="5"` | Save/restore issue #5 only |
| Multiple numbers (space) | `INCLUDE_ISSUES="1 3 7"` | Save/restore issues #1, #3, #7 |
| Multiple numbers (comma) | `INCLUDE_ISSUES="1,3,7"` | Save/restore issues #1, #3, #7 |
| Multiple numbers (mixed) | `INCLUDE_ISSUES="1, 3, 7"` | Save/restore issues #1, #3, #7 |
| Range | `INCLUDE_ISSUES="5-10"` | Save/restore issues #5 through #10 |
| Combined | `INCLUDE_ISSUES="1-3 5 8-10"` | Save/restore issues #1-3, #5, #8-10 |
| Combined (comma) | `INCLUDE_ISSUES="1-3,5,8-10"` | Save/restore issues #1-3, #5, #8-10 |
| Combined (mixed) | `INCLUDE_ISSUES="1-3, 5, 8-10"` | Save/restore issues #1-3, #5, #8-10 |

#### INCLUDE_PULL_REQUESTS Specification

Identical format support as `INCLUDE_ISSUES` but applies to pull requests:

| Format | Example | Description |
|--------|---------|-------------|
| Boolean - All | `INCLUDE_PULL_REQUESTS="true"` | Save/restore ALL pull requests |
| Boolean - None | `INCLUDE_PULL_REQUESTS="false"` | Skip ALL pull requests |
| Single number | `INCLUDE_PULL_REQUESTS="12"` | Save/restore PR #12 only |
| Range | `INCLUDE_PULL_REQUESTS="10-15"` | Save/restore PRs #10 through #15 |
| Combined | `INCLUDE_PULL_REQUESTS="1-5 8 12-15"` | Save/restore PRs #1-5, #8, #12-15 |

#### Comment Coupling Behavior

Comments are automatically included/excluded based on their parent issue/PR selection:

**Issue Comments**:
- If `INCLUDE_ISSUES="1 5"` → Only comments from issues #1 and #5 are processed
- `INCLUDE_ISSUE_COMMENTS` controls whether selected issue comments are included
- If `INCLUDE_ISSUE_COMMENTS=false` → No issue comments are saved/restored regardless of issue selection

**Pull Request Comments**:
- If `INCLUDE_PULL_REQUESTS="10-12"` → Only comments from PRs #10, #11, #12 are processed  
- `INCLUDE_PULL_REQUEST_COMMENTS` controls whether selected PR comments are included
- If `INCLUDE_PULL_REQUEST_COMMENTS=false` → No PR comments are saved/restored regardless of PR selection

### 2. Implementation Architecture

#### Number Parsing Component

**Location**: `src/config/number_parser.py`

```python
class NumberSpecificationParser:
    """Parse number specifications for selective issue/PR processing."""
    
    @staticmethod
    def parse(specification: str) -> set[int]:
        """Parse number specification into set of integers."""
        
    @staticmethod  
    def is_boolean_value(value: str) -> bool:
        """Check if value is a boolean specification."""
        
    @staticmethod
    def parse_boolean_value(value: str) -> bool:
        """Parse boolean value (true/false)."""
```

**Features**:
- Parse single numbers: `"5"` → `{5}`
- Parse number lists: `"1 3 5"` → `{1, 3, 5}`  
- Parse ranges: `"1-5"` → `{1, 2, 3, 4, 5}`
- Parse combined: `"1-3 5"` → `{1, 2, 3, 5}`
- Handle multiple delimiters: spaces, commas, mixed
- Validate number formats and ranges
- Support boolean fallback for backwards compatibility

#### Configuration Updates

**Location**: `src/config/settings.py`

**Current**:
```python
include_issues: bool
include_pull_requests: bool
```

**New**:
```python  
include_issues: Union[bool, set[int]]
include_pull_requests: Union[bool, set[int]]
```

**Parsing Logic**:
1. Check if value is boolean (`"true"`, `"false"`, `"yes"`, `"no"`, `"on"`, `"off"`)
2. If boolean → return boolean value for all-or-nothing behavior  
3. If not boolean → parse as number specification and return set of integers
4. Return appropriate type (`bool` for all/none, `set[int]` for selective)

#### Filter Integration

**Save Operations**:
- Boolean `true`: Process ALL issues/PRs (existing behavior)
- Boolean `false`: Skip ALL issues/PRs (existing behavior)
- Number specification: Filter GitHub API responses to only process specified numbers
- Reduce API calls and data processing overhead for selective operations

**Restore Operations**: 
- Boolean `true`: Restore ALL issues/PRs from saved data (existing behavior)
- Boolean `false`: Skip ALL issues/PRs restoration (existing behavior)
- Number specification: Filter JSON data to only restore specified numbers
- Skip unspecified issues/PRs entirely for selective operations

### 3. Validation and Error Handling

#### Input Validation

**Valid Formats**:
- Numbers: `1`, `10`, `999`
- Ranges: `1-5`, `10-20` (start ≤ end)
- Lists: `1 2 3`, `1,2,3`, `1, 2, 3`
- Combined: `1-3 5`, `1-3,5`, `1-3, 5`

**Invalid Formats**:
- Negative numbers: `-1`, `1--3`
- Zero: `0` (GitHub issues/PRs start at #1)
- Invalid ranges: `5-1` (end < start)
- Non-numeric: `abc`, `1-abc`
- Empty ranges: `1-`, `-5`

#### Error Messages

```
Invalid number specification in INCLUDE_ISSUES: "5-1". Range end (1) must be >= range start (5).

Invalid number specification in INCLUDE_ISSUES: "abc". Expected numbers, ranges (e.g., "1-5"), or boolean values.

Invalid number specification in INCLUDE_PULL_REQUESTS: "0". GitHub issue/PR numbers start at 1.
```

#### Backwards Compatibility

**Supported Boolean Values** (all boolean environment variables):
- `"true"`, `"false"` 
- `"yes"`, `"no"`
- `"on"`, `"off"`
- Case-insensitive

**Removed Boolean Values**:
- `"1"`, `"0"` (now interpreted as issue/PR numbers)

**Migration Path**:
- Update documentation with new boolean value requirements
- Add deprecation warnings for `"0"`/`"1"` usage
- Provide clear error messages for invalid formats

### 4. Performance Considerations

#### Efficient Filtering

**Save Operations**:
- Pre-filter GitHub API queries where possible
- Use GitHub API pagination efficiently  
- Avoid fetching unnecessary issues/PRs

**Restore Operations**:
- Filter JSON data before processing
- Skip parsing/validation for unselected items
- Maintain fast startup times

#### Memory Usage

- Use `set[int]` for O(1) lookup performance
- Avoid loading large data structures for unselected items
- Stream processing where applicable

## Examples and Use Cases

### Example 1: Single Issue Migration

**Scenario**: Migrate only issue #5 and its comments

```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=token \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -e INCLUDE_ISSUES="5" \
  -e INCLUDE_ISSUE_COMMENTS=true \
  -e INCLUDE_PULL_REQUESTS=false \
  -v $(pwd)/data:/data \
  github-data:latest
```

**Result**: Saves issue #5 and its comments, skips all other issues and PRs

### Example 2: PR Range with Comments Disabled

**Scenario**: Migrate PRs #10-15 without their comments

```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=token \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -e INCLUDE_ISSUES=false \
  -e INCLUDE_PULL_REQUESTS="10-15" \
  -e INCLUDE_PULL_REQUEST_COMMENTS=false \
  -v $(pwd)/data:/data \
  github-data:latest
```

**Result**: Saves PRs #10-15 without comments, skips all issues

### Example 3: Mixed Selection

**Scenario**: Migrate specific issues and PR ranges

```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=token \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -e INCLUDE_ISSUES="1-3 5 8-10" \
  -e INCLUDE_PULL_REQUESTS="20-25" \
  -v $(pwd)/data:/data \
  github-data:latest
```

**Result**: Saves issues #1-3, #5, #8-10 and PRs #20-25 with their comments

### Example 4: Boolean Values (All/None Behavior)

**Scenario**: Use boolean values for all-or-nothing behavior

```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=token \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -e INCLUDE_ISSUES=true \
  -e INCLUDE_PULL_REQUESTS=false \
  -v $(pwd)/data:/data \
  github-data:latest
```

**Result**: Saves ALL issues, skips all PRs (boolean behavior for comprehensive operations)

## Testing Strategy

### Unit Tests

**Number Parser Tests** (`tests/unit/config/test_number_parser.py`):
- Valid number specifications
- Invalid format handling  
- Range validation
- Boolean value detection
- Error message verification

**Configuration Tests** (`tests/unit/config/test_settings.py`):
- Environment variable parsing
- Type conversion validation
- Backwards compatibility  
- Error handling

### Integration Tests

**Save Operation Tests** (`tests/integration/test_selective_save.py`):
- Single number selection
- Range selection  
- Combined selection formats
- Comment coupling behavior

**Restore Operation Tests** (`tests/integration/test_selective_restore.py`):
- Filtered data restoration
- Missing number handling
- Comment restoration coupling

### End-to-End Tests

**Container Tests** (`tests/container/test_selective_workflows.py`):
- Complete save/restore workflows
- Docker environment variable handling
- Real GitHub API interaction simulation

## Documentation Updates

### README.md Updates

**Environment Variables Section**:
- Update `INCLUDE_ISSUES` and `INCLUDE_PULL_REQUESTS` descriptions
- Add number specification format examples
- Update boolean value format documentation
- Add migration guide from old boolean format

**Examples Section**:
- Add selective save/restore examples
- Show various number specification formats
- Demonstrate comment coupling behavior

### CLAUDE.md Updates

**Environment Variable Examples**:
- Replace existing boolean examples
- Add number specification examples
- Update boolean value format documentation

## Migration Plan

### Phase 1: Core Implementation
1. Implement `NumberSpecificationParser`
2. Update `ApplicationConfig` parsing logic
3. Add comprehensive unit tests
4. Update configuration validation

### Phase 2: Integration
1. Update save/restore operation filtering
2. Implement comment coupling logic
3. Add integration tests
4. Performance optimization

### Phase 3: Documentation and Testing  
1. Update all documentation
2. Add end-to-end tests
3. Container integration testing
4. Performance benchmarking

### Phase 4: Release
1. Code review and quality checks
2. Final testing validation
3. Documentation review
4. Release preparation

## Success Criteria

### Functional Requirements
- ✅ Parse single numbers, ranges, and combinations correctly
- ✅ Maintain backwards compatibility with boolean values
- ✅ Filter save/restore operations based on number selection
- ✅ Couple comments with their parent issue/PR selection
- ✅ Provide clear error messages for invalid formats

### Performance Requirements  
- ✅ No significant performance degradation for existing boolean usage
- ✅ Improved performance for selective operations (fewer API calls)
- ✅ Memory usage scales with selected items, not total repository size

### Quality Requirements
- ✅ Comprehensive test coverage (>95%)
- ✅ Clear documentation with examples
- ✅ Robust error handling and validation
- ✅ Consistent behavior across save/restore operations

## Future Enhancements

### Advanced Selection Features
- **Label-based selection**: `INCLUDE_ISSUES="label:bug,enhancement"`
- **Date-based selection**: `INCLUDE_ISSUES="created:2024-01-01..2024-12-31"`
- **Author-based selection**: `INCLUDE_ISSUES="author:username"`

### Performance Optimizations
- **Parallel processing**: Process selected issues/PRs concurrently
- **Incremental updates**: Update only changed items
- **Smart caching**: Cache selection results for repeated operations

### CLI Enhancements
- **Interactive selection**: Terminal UI for choosing issues/PRs
- **Preview mode**: Show what would be selected before operation
- **Selection validation**: Verify numbers exist before processing

---

**Document Status**: Draft Ready for Implementation  
**Next Steps**: Begin Phase 1 implementation with `NumberSpecificationParser`