# INCLUDE_PULL_REQUEST_COMMENTS Use Cases and Scenarios

**Date:** 2025-09-29  
**Author:** Claude Code  
**Related:** 2025-09-29-14-08-include-pull-request-comments-feature-analysis.md

## Overview

This document outlines comprehensive use cases for the proposed `INCLUDE_PULL_REQUEST_COMMENTS` environment variable, demonstrating expected behavior across all possible configuration combinations with `INCLUDE_PULL_REQUESTS`.

## Configuration Matrix

| INCLUDE_PULL_REQUESTS | INCLUDE_PULL_REQUEST_COMMENTS | Result |
|----------------------|------------------------------|---------|
| `false` | `false` | Neither PRs nor comments |
| `false` | `true` | Warning + Skip comments (dependency not met) |
| `true` | `false` | PRs only, no comments |
| `true` | `true` | PRs with comments (current behavior) |

## Use Case 1: Basic Issue Tracking Only
**Configuration:** `INCLUDE_PULL_REQUESTS=false`, `INCLUDE_PULL_REQUEST_COMMENTS=false`

### Scenario
A team using GitHub primarily for issue tracking, not pull requests. They want to backup/restore only labels, issues, and issue comments.

### Expected Behavior

**Save Operation:**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_PULL_REQUESTS=false \
  -e INCLUDE_PULL_REQUEST_COMMENTS=false \
  -v $(pwd)/backup:/data \
  github-data:latest
```

**Output Files Created:**
- `labels.json`
- `issues.json` 
- `comments.json` (issue comments only)
- `git_repo/` (if `INCLUDE_GIT_REPO=true`)

**Output Files NOT Created:**
- `pull_requests.json`
- `pr_comments.json`

**Console Output:**
```
✓ Saving labels...
✓ Saving issues...
✓ Saving issue comments...
✓ Save operation completed
```

**Restore Operation:**
Restores labels, issues, and issue comments only. No pull request data processed.

---

## Use Case 2: Comments Requested Without Pull Requests (Invalid Configuration)
**Configuration:** `INCLUDE_PULL_REQUESTS=false`, `INCLUDE_PULL_REQUEST_COMMENTS=true`

### Scenario
User misconfiguration - attempting to backup PR comments without pull requests themselves.

### Expected Behavior

**Save Operation:**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_PULL_REQUESTS=false \
  -e INCLUDE_PULL_REQUEST_COMMENTS=true \
  -v $(pwd)/backup:/data \
  github-data:latest
```

**Console Output:**
```
⚠️  Warning: INCLUDE_PULL_REQUEST_COMMENTS=true requires INCLUDE_PULL_REQUESTS=true. Ignoring PR comments.
✓ Saving labels...
✓ Saving issues...
✓ Saving issue comments...
✓ Save operation completed
```

**Output Files Created:**
- `labels.json`
- `issues.json`
- `comments.json` (issue comments only)

**Output Files NOT Created:**
- `pull_requests.json`
- `pr_comments.json`

**Restore Operation:**
Same behavior - warning displayed, PR comments ignored.

---

## Use Case 3: Pull Requests Without Comments
**Configuration:** `INCLUDE_PULL_REQUESTS=true`, `INCLUDE_PULL_REQUEST_COMMENTS=false`

### Scenario
A development team wants to backup pull request metadata (titles, descriptions, merge status) but exclude the conversation comments to reduce backup size and focus on structural data.

### Expected Behavior

**Save Operation:**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_PULL_REQUESTS=true \
  -e INCLUDE_PULL_REQUEST_COMMENTS=false \
  -v $(pwd)/backup:/data \
  github-data:latest
```

**Console Output:**
```
✓ Saving labels...
✓ Saving issues...
✓ Saving issue comments...
✓ Saving pull requests...
✓ Save operation completed
```

**Output Files Created:**
- `labels.json`
- `issues.json`
- `comments.json` (issue comments only)
- `pull_requests.json`

**Output Files NOT Created:**
- `pr_comments.json`

**Pull Requests JSON Structure:**
```json
[
  {
    "id": "PR_123",
    "number": 42,
    "title": "Add new feature",
    "body": "This PR adds...",
    "state": "MERGED",
    "createdAt": "2025-09-29T10:00:00Z",
    "mergedAt": "2025-09-29T15:30:00Z",
    "author": {...},
    "labels": [...],
    "assignees": [...]
    // No comments field or empty comments array
  }
]
```

**Restore Operation:**
- Creates pull requests with all metadata
- Does not attempt to restore PR comments
- Branch creation and merging handled normally

---

## Use Case 4: Complete Pull Request Backup (Current Behavior)
**Configuration:** `INCLUDE_PULL_REQUESTS=true`, `INCLUDE_PULL_REQUEST_COMMENTS=true`

### Scenario
Full project migration or comprehensive backup including all pull request data and discussion history.

### Expected Behavior

**Save Operation:**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_PULL_REQUESTS=true \
  -e INCLUDE_PULL_REQUEST_COMMENTS=true \
  -v $(pwd)/backup:/data \
  github-data:latest
```

**Console Output:**
```
✓ Saving labels...
✓ Saving issues...
✓ Saving issue comments...
✓ Saving pull requests...
✓ Saving pull request comments...
✓ Save operation completed
```

**Output Files Created:**
- `labels.json`
- `issues.json`
- `comments.json` (issue comments)
- `pull_requests.json`
- `pr_comments.json`

**PR Comments JSON Structure:**
```json
[
  {
    "id": "IC_789",
    "pullRequestNumber": 42,
    "body": "This looks great! LGTM.",
    "author": {
      "login": "developer1",
      "id": "USER_456"
    },
    "createdAt": "2025-09-29T11:30:00Z",
    "updatedAt": "2025-09-29T11:30:00Z",
    "url": "https://github.com/owner/repo/pull/42#issuecomment-789"
  }
]
```

**Restore Operation:**
- Creates pull requests with all metadata
- Creates all PR comments in chronological order
- Maintains comment authorship and timestamps

---

## Advanced Use Cases

### Use Case 5: Selective Migration - Structure Only
**Scenario:** Migrating repository structure without discussion history

**Configuration:** `INCLUDE_PULL_REQUESTS=true`, `INCLUDE_PULL_REQUEST_COMMENTS=false`, `INCLUDE_ISSUE_COMMENTS=false`

**Business Value:** 
- Preserves development workflow and merge history
- Reduces backup size significantly
- Focuses on code changes rather than discussions
- Useful for public repository forks where discussion history isn't needed

**Expected File Size Reduction:** 60-80% compared to full backup

---

### Use Case 6: Discussion Archive - Comments Only
**Scenario:** Archiving project discussions while excluding structural data

**Configuration:** `INCLUDE_PULL_REQUESTS=false`, `INCLUDE_PULL_REQUEST_COMMENTS=false`, `INCLUDE_ISSUE_COMMENTS=true`

**Business Value:**
- Captures team decision-making process
- Preserves knowledge sharing in issue discussions
- Excludes code-specific pull request workflow
- Useful for research or team retrospectives

---

### Use Case 7: Compliance and Audit Trail
**Scenario:** Legal/compliance requirement to preserve all project communications

**Configuration:** `INCLUDE_PULL_REQUESTS=true`, `INCLUDE_PULL_REQUEST_COMMENTS=true`, `INCLUDE_ISSUE_COMMENTS=true`

**Business Value:**
- Complete audit trail of all project decisions
- Regulatory compliance for software development
- Full historical record for patent or IP purposes
- Complete project archaeology capabilities

---

## Default Behavior Analysis

### Recommended Defaults
Based on the analysis document:
- `INCLUDE_PULL_REQUESTS`: `false` (conservative default)
- `INCLUDE_PULL_REQUEST_COMMENTS`: `true` (when PRs are enabled)

### Rationale
1. **Backward Compatibility**: Maintains current behavior when PRs are enabled
2. **Conservative Approach**: Doesn't enable PR backup by default (large data impact)
3. **Intuitive Coupling**: Comments naturally enabled when PRs are enabled
4. **User Expectation**: Users who enable PRs likely want the full conversation context

---

## Error Scenarios and Edge Cases

### Edge Case 1: Orphaned PR Comments During Restore
**Scenario:** `pr_comments.json` exists but `INCLUDE_PULL_REQUESTS=false`

**Expected Behavior:**
```
⚠️  Warning: Found pr_comments.json but INCLUDE_PULL_REQUESTS=false. Skipping PR comment restore.
```

### Edge Case 2: Missing Dependencies During Restore
**Scenario:** `pr_comments.json` exists but `pull_requests.json` is missing/corrupted

**Expected Behavior:**
```
❌ Error: Cannot restore PR comments - pull_requests.json not found or invalid.
```

### Edge Case 3: Partial Restore Recovery
**Scenario:** PR restore succeeds but PR comment restore fails

**Expected Behavior:**
- Pull requests are successfully restored
- Error logged for comment restoration failure
- Operation continues (graceful degradation)
- Clear indication of what succeeded vs. failed

---

## Performance Implications

### Save Operation Performance by Configuration

| Configuration | Relative Save Time | API Calls | Storage Size |
|--------------|-------------------|-----------|--------------|
| PRs: false, Comments: false | 1x (baseline) | ~10 | Small |
| PRs: false, Comments: true | 1x | ~10 | Small |
| PRs: true, Comments: false | 2.5x | ~25 | Medium |
| PRs: true, Comments: true | 4x | ~40 | Large |

### Restore Operation Performance
- **PR-only restore**: ~2x baseline time (branch operations)
- **PR+Comments restore**: ~3x baseline time (sequential comment creation)
- **Rate limiting impact**: Proportional to API calls required

---

## Testing Scenarios

### Unit Test Coverage Required
1. Configuration parsing for all combinations
2. Strategy factory logic for conditional registration
3. Dependency validation warnings
4. Entity list generation

### Integration Test Coverage Required
1. Save operation file generation for each configuration
2. Restore operation behavior for each configuration  
3. Error handling for invalid configurations
4. Warning message display and logging

### Container Test Coverage Required
1. Full workflow testing for each valid configuration
2. Docker environment variable handling
3. File system state validation
4. Cross-configuration compatibility

---

## Documentation Impact

### README.md Updates Required
1. New environment variable documentation
2. Configuration examples for each use case
3. Performance considerations section
4. Troubleshooting guide for dependency warnings

### CLAUDE.md Updates Required
1. Updated environment variables list
2. Boolean value handling examples
3. Use case examples in development guidance

---

## Conclusion

The `INCLUDE_PULL_REQUEST_COMMENTS` feature provides valuable granular control while maintaining intuitive behavior patterns. The four configuration combinations cover distinct use cases from basic issue tracking to comprehensive project archival, with appropriate safeguards for invalid configurations.

The implementation should prioritize clear user feedback, graceful error handling, and performance optimization for large repositories.