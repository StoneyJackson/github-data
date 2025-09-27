# Selective Issues and PRs Backup/Restore Design

**Date**: 2025-09-27
**Topic**: Selective backup and restore of GitHub issues and pull requests
**Status**: Design Phase

## Overview

Design a feature to allow users to specify which issues and PRs to backup/restore using number lists and ranges (e.g., `1,3,5-8,12`).

## Use Cases

### Primary Use Cases
1. **Selective Migration**: Moving specific issues/PRs between repositories
2. **Incremental Backup**: Backing up only new issues since last backup
3. **Testing**: Working with subset of data for testing restore workflows
4. **Cleanup Operations**: Restoring only important issues after repository cleanup
5. **Branch-specific PRs**: Backing up PRs related to specific features/branches

### User Scenarios
- Developer wants to migrate issues #1-50 to new repository
- Team wants to backup only critical issues (tagged as P0/P1)
- QA wants to restore specific test-related issues for validation
- Manager wants to backup PRs from specific milestone

## Interface Design

### Environment Variable Names

```bash
ISSUES="1,3,5-8,12"
PULL_REQUESTS="1,3,5-8,12"
```

### Input Format Specification
```
Format: "number[,number|range]..."
Range: "start-end" (inclusive)
Examples:
  - "1"           → [1]
  - "1,3,5"       → [1, 3, 5]
  - "1-5"         → [1, 2, 3, 4, 5]
  - "1,3,5-8,12"  → [1, 3, 5, 6, 7, 8, 12]
  - "1-3,8-10"    → [1, 2, 3, 8, 9, 10]
```

### Environment Variable Examples
```bash
# Backup specific issues
export ISSUES="1,3,5-8,12"
python -m github_data backup --repo owner/repo

# Backup specific PRs
export PULL_REQUESTS="1,3,5-8,12"
python -m github_data backup --repo owner/repo

# Backup both issues and PRs
export ISSUES="1-10"
export PULL_REQUESTS="5,7,9-12"
python -m github_data backup --repo owner/repo

# Restore specific issues
export ISSUES="1,3,5"
python -m github_data restore --repo owner/repo --data-file backup.json

# Using .env file for complex configurations
echo "ISSUES=1,3,5-8,12" > .env
echo "PULL_REQUESTS=1,3,5-8,12" >> .env
python -m github_data backup --repo owner/repo

# CI/CD pipeline example
env:
  ISSUES: "1-50"
  PULL_REQUESTS: "1-20"
run: python -m github_data backup --repo ${{ github.repository }}

# Alternative shorter form for PRs
export PRS="1,3,5-8,12"
python -m github_data backup --repo owner/repo
```

## Implementation Design

### 1. Input Parsing Module
```python
# github_data/utils/number_parser.py
class NumberRangeParser:
    @staticmethod
    def parse(input_str: str) -> List[int]:
        """Parse "1,3,5-8,12" into [1, 3, 5, 6, 7, 8, 12]"""

    @staticmethod
    def validate_range(start: int, end: int) -> None:
        """Validate range is valid (start <= end, positive numbers)"""

    @staticmethod
    def expand_range(range_str: str) -> List[int]:
        """Expand "5-8" into [5, 6, 7, 8]"""
```

### 2. Environment Variable Integration
```python
# github_data/utils/env_config.py
import os
from typing import Optional, List

class SelectiveConfig:
    @staticmethod
    def get_issue_numbers() -> Optional[List[int]]:
        """Get issue numbers from ISSUES environment variable"""
        issues_env = os.getenv('ISSUES')
        return NumberRangeParser.parse(issues_env) if issues_env else None

    @staticmethod
    def get_pr_numbers() -> Optional[List[int]]:
        """Get PR numbers from PULL_REQUESTS or PRS environment variable"""
        # Check PULL_REQUESTS first, then PRS as fallback
        prs_env = os.getenv('PULL_REQUESTS') or os.getenv('PRS')
        return NumberRangeParser.parse(prs_env) if prs_env else None

# github_data/cli.py modifications
def backup(repo: str, ...):
    issue_numbers = SelectiveConfig.get_issue_numbers()
    pr_numbers = SelectiveConfig.get_pr_numbers()

    if issue_numbers:
        click.echo(f"Selective backup: Issues {issue_numbers}")
    if pr_numbers:
        click.echo(f"Selective backup: PRs {pr_numbers}")
```

### 3. Service Layer Updates
```python
# github_data/services/backup_service.py
class BackupService:
    async def backup_selective_issues(
        self,
        repo: str,
        issue_numbers: Optional[List[int]] = None
    ) -> List[Dict]:
        """Backup only specified issues"""

    async def backup_selective_prs(
        self,
        repo: str,
        pr_numbers: Optional[List[int]] = None
    ) -> List[Dict]:
        """Backup only specified PRs"""
```

### 4. GitHub API Client Updates
```python
# github_data/github_client.py
class GitHubClient:
    async def get_issues_by_numbers(
        self,
        repo: str,
        issue_numbers: List[int]
    ) -> List[Dict]:
        """Fetch specific issues by number"""

    async def get_prs_by_numbers(
        self,
        repo: str,
        pr_numbers: List[int]
    ) -> List[Dict]:
        """Fetch specific PRs by number"""
```

### 5. Data Filtering
```python
# For restore operations
class RestoreService:
    def filter_data_by_numbers(
        self,
        data: Dict,
        issue_numbers: Optional[List[int]] = None,
        pr_numbers: Optional[List[int]] = None
    ) -> Dict:
        """Filter backup data to only specified items"""
```

## Implementation Phases

### Phase 1: Core Parser and CLI
- [ ] Implement `NumberRangeParser` with comprehensive validation
- [ ] Add CLI options to backup/restore commands
- [ ] Unit tests for parser with edge cases

### Phase 2: Backup Integration
- [ ] Update `BackupService` for selective backup
- [ ] Modify GitHub API client for batch fetching by numbers
- [ ] Integration tests for selective backup

### Phase 3: Restore Integration
- [ ] Update `RestoreService` for selective restore
- [ ] Data filtering logic for restore operations
- [ ] Integration tests for selective restore

### Phase 4: Advanced Features
- [ ] Validation against existing repository state
- [ ] Progress reporting for large number sets
- [ ] `--exclude` options for inverse selection

## Risks and Mitigation

### 1. Invalid Issue/PR Numbers
**Risk**: User specifies non-existent issue/PR numbers
**Mitigation**:
- Validate numbers exist before processing
- Clear error messages with suggestions
- Option to continue with valid numbers only

### 2. Large Number Sets
**Risk**: Performance issues with large ranges (e.g., "1-10000")
**Mitigation**:
- Implement batch processing
- Progress indicators
- Rate limiting respect
- Memory-efficient streaming

### 3. Dependencies and Sub-issues
**Risk**: Missing dependencies when selecting subset
**Mitigation**:
- Detect and warn about missing sub-issue dependencies
- Option to auto-include dependencies
- Clear documentation about dependency handling

### 4. API Rate Limiting
**Risk**: Hitting rate limits with many individual requests
**Mitigation**:
- Batch API calls where possible
- Respect existing rate limiting
- Progress indicators for long operations

### 5. Data Integrity
**Risk**: Partial failures leaving inconsistent state
**Mitigation**:
- Atomic operations where possible
- Clear rollback procedures
- Comprehensive logging
- Dry-run mode for validation

### 6. Input Validation Edge Cases
**Risk**: Malformed input causing crashes
**Mitigation**:
- Comprehensive input validation
- Clear error messages
- Graceful degradation

### 7. Environment Variable Security
**Risk**: Sensitive information exposure in environment variables
**Mitigation**:
- Document security best practices
- Support .env files for local development
- Clear variables after use in CI/CD
- Avoid logging environment variable values

### 8. Configuration Conflicts
**Risk**: Environment variables conflicting with existing configuration
**Mitigation**:
- Clear precedence rules (env vars override defaults)
- Validation of conflicting settings
- Comprehensive documentation of all configuration sources

## Testing Strategy

### Unit Tests
- Number range parser with all edge cases
- Input validation scenarios
- Error handling paths

### Integration Tests
- Selective backup with real GitHub API
- Selective restore with sample data
- Mixed issue/PR operations

### Edge Case Tests
```python
# Test cases to cover
- Empty ranges: ""
- Single numbers: "5"
- Complex ranges: "1,3,5-8,10-12,15"
- Invalid formats: "1-", "-5", "abc", "1--5"
- Large ranges: "1-1000"
- Duplicate numbers: "1,2,2,3"
- Reverse ranges: "8-5" (should error)
- Non-existent numbers: Issues that don't exist

# Environment variable specific tests
- Missing environment variables
- Empty environment variables: ISSUES=""
- Whitespace handling: ISSUES=" 1, 3, 5-8 "
- Case sensitivity (should be case sensitive)
- Multiple processes with different env vars
- .env file loading and precedence
- Environment variable injection attacks
- PULL_REQUESTS vs PRS precedence testing
```

## Future Enhancements

### Advanced Selection
- Issue filters by label, milestone, assignee
- PR filters by branch, author, state
- Date range selection
- Combined filters: `--issues="1-10" --labels="bug,critical"`

### Configuration Files
```bash
# .env file approach (recommended)
ISSUES="1,3,5-8,12"
PULL_REQUESTS="1-5"
ISSUE_LABELS="bug,critical"
ISSUE_SINCE="2024-01-01"
PR_STATE="merged"

# Alternative: YAML config file (future enhancement)
# .github-data-config.yml
backup:
  issues:
    numbers: "1,3,5-8,12"
    labels: "bug,critical"
    since: "2024-01-01"
  pull_requests:
    numbers: "1-5"
    state: "merged"
```

### Interactive Mode
```bash
# Interactive selection (future enhancement)
python -m github_data backup --repo owner/repo --interactive
# Shows list of issues/PRs, user selects which to backup
# Could generate .env file with selections

# Alternative: Use environment variables for automation
export ISSUES="$(some-script-to-determine-issues.sh)"
python -m github_data backup --repo owner/repo
```

## Success Metrics

- [ ] Parser handles 100% of valid input formats correctly
- [ ] Performance: Handle ranges up to 1000 items efficiently
- [ ] User experience: Clear error messages for all failure modes
- [ ] Reliability: No data corruption with selective operations
- [ ] Compatibility: Works with existing backup/restore workflows

## Questions for Review

1. Should we support negative ranges (exclude) in initial version?
2. How should we handle sub-issue dependencies in selective backup?
3. Should ranges be inclusive or exclusive of endpoints?
4. What's the maximum reasonable range size before requiring confirmation?
5. Should we support issue/PR references (e.g., "owner/repo#123")?

## Next Steps

1. **Validate Design**: Review with team/users for feedback
2. **Create Tasks**: Break down into specific implementation tasks
3. **Prototype Parser**: Start with number range parsing as proof of concept
4. **Update Architecture**: Ensure current codebase can support selective operations
5. **Define Test Cases**: Comprehensive test scenarios before implementation
