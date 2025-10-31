# Proposal: INCLUDE_ISSUE_COMMENTS Environment Variable

**Date:** 2025-09-28  
**Status:** Proposal  
**Author:** Claude Code

## Overview

Add an `INCLUDE_ISSUE_COMMENTS` environment variable to provide granular control over issue comment save and restore operations.

## Current State

The GitHub Data project currently saves and restores issue comments as part of the standard workflow without optional exclusion. All issue comments are processed during save and restore operations.

## Proposed Solution

### Environment Variable

- **Name:** `INCLUDE_ISSUE_COMMENTS`
- **Type:** String (boolean-like)
- **Default Value:** `"true"`
- **Valid Values:** `"true"`, `"false"` (case-insensitive)

### Behavior

#### When `INCLUDE_ISSUE_COMMENTS="true"` (default)
- Save operations save issue comments to JSON files
- Restore operations recreate issue comments from saved data
- Maintains current behavior for backward compatibility

#### When `INCLUDE_ISSUE_COMMENTS="false"`
- Save operations skip issue comment collection
- Restore operations skip issue comment recreation
- Issues themselves are still processed normally
- Reduces saved file size and restore time for comment-heavy repositories

## Implementation Areas

### 1. Environment Variable Handling
- Add to configuration module
- Implement validation for accepted values
- Provide clear error messages for invalid values

### 2. Save Workflow Changes
- Modify save logic to conditionally skip comment collection
- Update progress indicators to reflect comment exclusion
- Adjust save metadata to indicate comment inclusion status

### 3. Restore Workflow Changes  
- Modify restore logic to conditionally skip comment restoration
- Handle cases where saved data may contain comments but environment excludes them
- Update progress indicators and logging

### 4. CLI Integration
- Display current setting in verbose output
- Include in save/restore operation summaries
- Add to help documentation

## Benefits

1. **Performance Optimization**: Faster save/restore for repositories with extensive comment history
2. **Storage Efficiency**: Smaller saved files when comments aren't needed
3. **Selective Data Migration**: Flexibility for different use cases
4. **Backward Compatibility**: Default behavior unchanged for existing workflows

## Use Cases

- **Repository Structure Migration**: Moving issues without comment history
- **Performance Testing**: Faster operations for CI/CD pipelines
- **Storage Constraints**: Reducing saved file size requirements
- **Privacy Compliance**: Excluding potentially sensitive comment content

## Implementation Considerations

### Error Handling
- Graceful handling of missing environment variable
- Clear validation messages for invalid values
- Fallback to default behavior on configuration errors

### Logging and Feedback
- Log current setting at operation start
- Include comment processing status in progress updates
- Reflect setting in operation summaries

### Testing Requirements
- Unit tests for environment variable parsing
- Integration tests for save/restore with comments disabled
- Validation of backward compatibility with existing workflows

## Future Enhancements

This pattern could be extended to other data types:
- `INCLUDE_PULL_REQUEST_COMMENTS`
- `INCLUDE_REVIEW_COMMENTS`
- `INCLUDE_COMMIT_COMMENTS`

## Implementation Priority

**Medium Priority** - Enhances flexibility without breaking existing functionality. Can be implemented as a standalone feature without dependencies on other planned enhancements.