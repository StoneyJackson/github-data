# Advanced Selective Operations Guide

This guide provides comprehensive documentation for using selective issue and PR operations in GitHub Data, including advanced use cases, best practices, troubleshooting, and optimization strategies.

## Table of Contents

- [Overview](#overview)
- [Selective Format Specification](#selective-format-specification)
- [Use Cases and Examples](#use-cases-and-examples)
- [Performance Optimization](#performance-optimization)
- [Comment Coupling Behavior](#comment-coupling-behavior)
- [Best Practices](#best-practices)
- [Advanced Scenarios](#advanced-scenarios)
- [Troubleshooting](#troubleshooting)
- [Integration Patterns](#integration-patterns)

## Overview

Selective operations allow you to save and restore specific issues and pull requests by number, rather than processing all data. This provides significant benefits:

- **Performance Improvement**: 50-90% reduction in processing time and API calls
- **Memory Efficiency**: Memory usage scales with selected items, not repository size
- **Focused Migration**: Migrate specific issues/PRs between repositories
- **Development Testing**: Create targeted test datasets
- **Backup Optimization**: Save only critical or current milestone data

## Selective Format Specification

### Supported Formats

| Format | Syntax | Example | Result |
|--------|--------|---------|--------|
| **Boolean All** | `true` | `INCLUDE_ISSUES=true` | All issues |
| **Boolean None** | `false` | `INCLUDE_ISSUES=false` | No issues |
| **Single Number** | `"N"` | `INCLUDE_ISSUES="42"` | Issue #42 only |
| **Simple Range** | `"N-M"` | `INCLUDE_ISSUES="1-10"` | Issues #1 through #10 |
| **Multiple Singles** | `"N M P"` | `INCLUDE_ISSUES="1 5 10"` | Issues #1, #5, #10 |
| **Multiple Ranges** | `"N-M P-Q"` | `INCLUDE_ISSUES="1-5 10-15"` | Issues #1-5, #10-15 |
| **Mixed Format** | `"N-M P Q-R"` | `INCLUDE_ISSUES="1-5 10 15-20"` | Issues #1-5, #10, #15-20 |

### Validation Rules

1. **Positive Numbers Only**: All numbers must be positive integers (> 0)
2. **No Empty Sets**: Cannot specify empty selection (use `false` instead)
3. **Range Format**: Ranges must be `N-M` where N ≤ M
4. **Space Separated**: Multiple selections separated by spaces
5. **No Duplicates**: Duplicate numbers are automatically deduplicated

### Examples

```bash
# Valid specifications
INCLUDE_ISSUES="1"                    # Single issue
INCLUDE_ISSUES="1-100"                # Range of issues
INCLUDE_ISSUES="1 5 10"               # Multiple singles
INCLUDE_ISSUES="1-10 20-30"           # Multiple ranges  
INCLUDE_ISSUES="1-5 10 15-20 25"      # Mixed format

# Invalid specifications (will cause errors)
INCLUDE_ISSUES=""                     # Empty string (use false)
INCLUDE_ISSUES="0"                    # Zero not allowed
INCLUDE_ISSUES="-5"                   # Negative numbers not allowed
INCLUDE_ISSUES="10-5"                 # Invalid range (start > end)
INCLUDE_ISSUES="1,2,3"                # Commas not supported (use spaces)
```

## Use Cases and Examples

### 1. Issue Migration Between Repositories

**Scenario**: Migrate specific issues from an old repository to a new one.

```bash
# Step 1: Save issues from source repository
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=oldorg/legacy-repo \
  -e INCLUDE_ISSUES="100-150 200-250" \
  -e INCLUDE_ISSUE_COMMENTS=true \
  -e INCLUDE_PULL_REQUESTS=false \
  -e INCLUDE_GIT_REPO=false \
  -v $(pwd)/migration-data:/data \
  ghcr.io/stoneyjackson/github-data:latest

# Step 2: Restore issues to target repository
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=neworg/current-repo \
  -e INCLUDE_ISSUES="100-150 200-250" \
  -e INCLUDE_ISSUE_COMMENTS=true \
  -e INCLUDE_PULL_REQUESTS=false \
  -v $(pwd)/migration-data:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

### 2. Milestone-Based Backup

**Scenario**: Create backups for specific development milestones.

```bash
# Backup current sprint issues (assume issues 500-600)
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=company/project \
  -e INCLUDE_ISSUES="500-600" \
  -e INCLUDE_PULL_REQUESTS="300-350" \
  -e INCLUDE_ISSUE_COMMENTS=true \
  -e INCLUDE_PULL_REQUEST_COMMENTS=true \
  -v $(pwd)/sprint-backup:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

### 3. Development Test Data Generation

**Scenario**: Create focused test datasets for development and testing.

```bash
# Create test data with specific issue patterns
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=example/repo \
  -e INCLUDE_ISSUES="1 5 10-15 20 25" \
  -e INCLUDE_ISSUE_COMMENTS=false \
  -e INCLUDE_PULL_REQUESTS="1-3" \
  -e INCLUDE_PULL_REQUEST_COMMENTS=true \
  -v $(pwd)/test-data:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

### 4. Gradual Migration Strategy

**Scenario**: Migrate large repositories in phases to manage risk and resources.

```bash
# Phase 1: Critical issues (1-100)
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_REPO=source/repo \
  -e INCLUDE_ISSUES="1-100" \
  -v $(pwd)/phase1:/data \
  ghcr.io/stoneyjackson/github-data:latest

# Phase 2: Feature issues (101-500)  
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_REPO=source/repo \
  -e INCLUDE_ISSUES="101-500" \
  -v $(pwd)/phase2:/data \
  ghcr.io/stoneyjackson/github-data:latest

# Phase 3: Archive issues (501+)
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_REPO=source/repo \
  -e INCLUDE_ISSUES="501-1000" \
  -v $(pwd)/phase3:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

### 5. Cross-Repository PR Analysis

**Scenario**: Analyze specific PRs across multiple repositories.

```bash
# Save specific PRs from multiple repos for analysis
for repo in "team/frontend" "team/backend" "team/mobile"; do
  docker run --rm \
    -e OPERATION=save \
    -e GITHUB_REPO="$repo" \
    -e INCLUDE_ISSUES=false \
    -e INCLUDE_PULL_REQUESTS="1-50" \
    -e INCLUDE_PULL_REQUEST_COMMENTS=true \
    -v $(pwd)/analysis-data/$repo:/data \
    ghcr.io/stoneyjackson/github-data:latest
done
```

## Performance Optimization

### Memory Usage Optimization

**Optimal Range Sizes:**
- **Small Operations**: 1-50 items (< 100MB memory)
- **Medium Operations**: 51-200 items (100-500MB memory)
- **Large Operations**: 201-1000 items (500MB-2GB memory)

**Memory-Efficient Patterns:**
```bash
# Good: Process large ranges in chunks
for start in 1 101 201 301; do
  end=$((start + 99))
  docker run --rm \
    -e INCLUDE_ISSUES="$start-$end" \
    -v $(pwd)/chunk-$start:/data \
    ghcr.io/stoneyjackson/github-data:latest
done

# Avoid: Very large single ranges that may cause memory issues
# INCLUDE_ISSUES="1-10000"  # May use excessive memory
```

### API Call Optimization

**Efficient Selection Patterns:**
```bash
# Efficient: Use ranges instead of individual numbers
INCLUDE_ISSUES="1-100"           # 1 range specification
# vs
INCLUDE_ISSUES="1 2 3 ... 100"   # 100 individual specifications

# Efficient: Combine related ranges
INCLUDE_ISSUES="1-50 51-100"     # Can be optimized to "1-100"
```

### Bandwidth and Storage Optimization

**Selective Comments Strategy:**
```bash
# Option 1: Include comments only when needed
docker run --rm \
  -e INCLUDE_ISSUES="1-100" \
  -e INCLUDE_ISSUE_COMMENTS=true \    # Full data
  -v $(pwd)/full-data:/data \
  ghcr.io/stoneyjackson/github-data:latest

# Option 2: Skip comments for faster operations
docker run --rm \
  -e INCLUDE_ISSUES="1-100" \
  -e INCLUDE_ISSUE_COMMENTS=false \   # Faster, smaller
  -v $(pwd)/issues-only:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

## Comment Coupling Behavior

### Automatic Coupling Rules

1. **Issue Comments**: Only saved/restored for selected issues
2. **PR Comments**: Only saved/restored for selected PRs
3. **Boolean Override**: `INCLUDE_*_COMMENTS=false` disables all comments
4. **Warning Behavior**: Warns when comments enabled but parent items disabled

### Coupling Examples

```bash
# Example 1: Selective issues with automatic comment coupling
INCLUDE_ISSUES="5 10 15"
INCLUDE_ISSUE_COMMENTS=true
# Result: Only comments from issues #5, #10, #15 are saved

# Example 2: Boolean override
INCLUDE_ISSUES="5 10 15"  
INCLUDE_ISSUE_COMMENTS=false
# Result: No comments saved, regardless of issue selection

# Example 3: Warning scenario
INCLUDE_ISSUES=false
INCLUDE_ISSUE_COMMENTS=true
# Result: Warning logged, no comments saved
```

### Advanced Coupling Scenarios

```bash
# Mixed boolean and selective with comments
docker run --rm \
  -e INCLUDE_ISSUES=true \              # All issues
  -e INCLUDE_ISSUE_COMMENTS=true \      # All issue comments
  -e INCLUDE_PULL_REQUESTS="10-20" \    # Selective PRs
  -e INCLUDE_PULL_REQUEST_COMMENTS=true \ # Only PR comments from #10-20
  -v $(pwd)/mixed-data:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

## Best Practices

### 1. Start Small and Test

Always test with small selections before processing large datasets:

```bash
# Test with small selection first
docker run --rm \
  -e INCLUDE_ISSUES="1-5" \
  -v $(pwd)/test:/data \
  ghcr.io/stoneyjackson/github-data:latest

# Scale up after validation
docker run --rm \
  -e INCLUDE_ISSUES="1-100" \
  -v $(pwd)/production:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

### 2. Use Ranges for Efficiency

```bash
# Preferred: Range notation
INCLUDE_ISSUES="1-100"

# Avoid: Individual number lists for large selections
# INCLUDE_ISSUES="1 2 3 4 5 6 7 8 9 10 ... 100"
```

### 3. Plan for Missing Numbers

```bash
# Request numbers that may not exist - tool handles gracefully
INCLUDE_ISSUES="1-1000"  # Repository may only have 500 issues
# Result: Issues 1-500 saved, 501-1000 ignored (not an error)
```

### 4. Optimize Comment Strategy

```bash
# Enable comments only when needed
docker run --rm \
  -e INCLUDE_ISSUES="1-100" \
  -e INCLUDE_ISSUE_COMMENTS=true \      # When comments needed
  -v $(pwd)/full-backup:/data \
  ghcr.io/stoneyjackson/github-data:latest

# Disable comments for faster operations
docker run --rm \
  -e INCLUDE_ISSUES="1-100" \
  -e INCLUDE_ISSUE_COMMENTS=false \     # When speed/size matters
  -v $(pwd)/fast-backup:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

### 5. Verify Results

Always verify selective operations completed as expected:

```bash
# After operation, check saved data
ls -la /path/to/data/
cat /path/to/data/issues.json | jq 'length'     # Count saved issues
cat /path/to/data/comments.json | jq 'length'   # Count saved comments
```

## Advanced Scenarios

### 1. Conditional Operations

Use shell scripting for conditional selective operations:

```bash
#!/bin/bash
# Conditional backup based on repository size
REPO="owner/repo"
ISSUE_COUNT=$(gh api repos/$REPO | jq '.open_issues_count')

if [ $ISSUE_COUNT -lt 100 ]; then
    # Small repo: backup all
    SELECTION="true"
else
    # Large repo: backup recent issues only
    SELECTION="$((ISSUE_COUNT - 100))-$ISSUE_COUNT"
fi

docker run --rm \
  -e INCLUDE_ISSUES="$SELECTION" \
  -v $(pwd)/conditional-backup:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

### 2. Multi-Repository Synchronized Operations

Coordinate selective operations across multiple repositories:

```bash
#!/bin/bash
# Synchronize specific issues across related repositories
REPOS=("frontend/app" "backend/api" "mobile/app")
CRITICAL_ISSUES="1-10 50-60"

for repo in "${REPOS[@]}"; do
    echo "Processing $repo..."
    docker run --rm \
      -e GITHUB_REPO="$repo" \
      -e INCLUDE_ISSUES="$CRITICAL_ISSUES" \
      -v $(pwd)/sync-$repo:/data \
      ghcr.io/stoneyjackson/github-data:latest
done
```

### 3. Progressive Migration with Verification

Implement progressive migration with validation steps:

```bash
#!/bin/bash
# Progressive migration with validation
SOURCE_REPO="old/repo"
TARGET_REPO="new/repo" 
BATCH_SIZE=50

for start in $(seq 1 $BATCH_SIZE 500); do
    end=$((start + BATCH_SIZE - 1))
    echo "Migrating issues $start-$end"
    
    # Save batch
    docker run --rm \
      -e OPERATION=save \
      -e GITHUB_REPO="$SOURCE_REPO" \
      -e INCLUDE_ISSUES="$start-$end" \
      -v $(pwd)/batch-$start:/data \
      ghcr.io/stoneyjackson/github-data:latest
    
    # Restore batch
    docker run --rm \
      -e OPERATION=restore \
      -e GITHUB_REPO="$TARGET_REPO" \
      -e INCLUDE_ISSUES="$start-$end" \
      -v $(pwd)/batch-$start:/data \
      ghcr.io/stoneyjackson/github-data:latest
    
    # Verify batch (example verification)
    echo "Batch $start-$end completed"
    sleep 5  # Rate limiting pause
done
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Empty Results

**Problem**: No data saved despite specifying issue numbers.

**Diagnosis**:
```bash
# Check if specified issues exist in repository
gh api repos/owner/repo/issues?per_page=100 | jq '.[].number' | sort -n
```

**Solution**: Verify issue numbers exist in the source repository.

#### 2. Memory Issues

**Problem**: Container runs out of memory with large selections.

**Diagnosis**: Check memory usage patterns and selection size.

**Solutions**:
```bash
# Solution 1: Reduce selection size
INCLUDE_ISSUES="1-50"     # Instead of "1-1000"

# Solution 2: Increase container memory
docker run --rm -m 2g \   # Allocate 2GB memory
  -e INCLUDE_ISSUES="1-500" \
  -v $(pwd)/data:/data \
  ghcr.io/stoneyjackson/github-data:latest

# Solution 3: Process in batches
for batch in "1-100" "101-200" "201-300"; do
    docker run --rm \
      -e INCLUDE_ISSUES="$batch" \
      -v $(pwd)/batch-data:/data \
      ghcr.io/stoneyjackson/github-data:latest
done
```

#### 3. API Rate Limiting

**Problem**: Operations fail due to GitHub API rate limits.

**Solutions**:
```bash
# Solution 1: Use smaller selections
INCLUDE_ISSUES="1-25"     # Instead of "1-100"

# Solution 2: Add delays between operations
sleep 60  # Wait between operations

# Solution 3: Check rate limit status
gh api rate_limit
```

#### 4. Comment Coupling Confusion

**Problem**: Unexpected comment behavior with selective operations.

**Understanding**:
```bash
# Comments follow their parent selections
INCLUDE_ISSUES="5"        # Only issue #5
INCLUDE_ISSUE_COMMENTS=true  # Only comments from issue #5

# To disable comments entirely
INCLUDE_ISSUE_COMMENTS=false  # No comments, regardless of selection
```

#### 5. Validation Errors

**Problem**: Environment variable validation failures.

**Common Errors and Fixes**:
```bash
# Error: "cannot be empty"
INCLUDE_ISSUES=""         # ❌ Invalid
INCLUDE_ISSUES=false      # ✅ Correct

# Error: "must be positive integers"  
INCLUDE_ISSUES="0 -1"     # ❌ Invalid
INCLUDE_ISSUES="1 2"      # ✅ Correct

# Error: "invalid format"
INCLUDE_ISSUES="1,2,3"    # ❌ Invalid (commas)
INCLUDE_ISSUES="1 2 3"    # ✅ Correct (spaces)
```

### Debugging Tips

#### 1. Enable Verbose Logging

```bash
# Add logging environment variables
docker run --rm \
  -e LOG_LEVEL=DEBUG \
  -e INCLUDE_ISSUES="1-10" \
  -v $(pwd)/data:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

#### 2. Dry Run Testing

```bash
# Test configuration without actual operations
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=fake_token \
  -e GITHUB_REPO=test/repo \
  -e INCLUDE_ISSUES="1-5" \
  --entrypoint=/bin/bash \
  ghcr.io/stoneyjackson/github-data:latest \
  -c "echo 'Config validation test'"
```

#### 3. Validate Data Files

```bash
# Check saved data structure
jq '.[] | {number, title}' /path/to/data/issues.json
jq 'length' /path/to/data/comments.json
```

## Integration Patterns

### 1. CI/CD Pipeline Integration

```yaml
# GitHub Actions example
name: Selective Backup
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Selective Issue Backup
        run: |
          docker run --rm \
            -e OPERATION=save \
            -e GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }} \
            -e GITHUB_REPO=${{ github.repository }} \
            -e INCLUDE_ISSUES="1-100" \
            -v ./backup:/data \
            ghcr.io/stoneyjackson/github-data:latest
```

### 2. Monitoring and Alerting

```bash
#!/bin/bash
# Monitoring script for selective operations
OPERATION_LOG="/var/log/github-data-operations.log"

# Run selective operation with monitoring
docker run --rm \
  -e INCLUDE_ISSUES="1-100" \
  -v $(pwd)/data:/data \
  ghcr.io/stoneyjackson/github-data:latest \
  2>&1 | tee -a "$OPERATION_LOG"

# Check for errors
if grep -q "ERROR" "$OPERATION_LOG"; then
    echo "Operation failed - alerting team"
    # Send alert (email, Slack, etc.)
fi
```

### 3. Data Pipeline Integration

```bash
#!/bin/bash
# Data pipeline with selective operations
SOURCE_REPOS=("team/frontend" "team/backend")
ANALYSIS_RANGE="1-50"

# Extract phase
for repo in "${SOURCE_REPOS[@]}"; do
    docker run --rm \
      -e OPERATION=save \
      -e GITHUB_REPO="$repo" \
      -e INCLUDE_ISSUES="$ANALYSIS_RANGE" \
      -v $(pwd)/extract/$repo:/data \
      ghcr.io/stoneyjackson/github-data:latest
done

# Transform phase (example: combine data)
jq -s 'add' extract/*/issues.json > combined-issues.json

# Load phase (example: import to analysis system)
# python analyze-issues.py combined-issues.json
```

This comprehensive guide should help users master selective operations in GitHub Data, from basic usage to advanced integration scenarios.