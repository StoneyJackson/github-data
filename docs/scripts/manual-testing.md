# Manual Container Testing Guide

This guide explains how to manually test the GitHub Data container against different repositories.

## Prerequisites

1. **GitHub Token**: Export your GitHub personal access token:
   ```bash
   export GITHUB_TOKEN=your_github_token_here
   ```

2. **Docker**: Ensure Docker is installed and running

3. **Repository Access**: Ensure your token has access to the repositories you want to test

## Quick Start

### Single Repository Test

Test a single repository:

```bash
# Test save operation
./scripts/manual-testing/test-repo.sh microsoft/vscode save

# Test restore operation  
./scripts/manual-testing/test-repo.sh microsoft/vscode restore
```

### Multiple Repository Test

1. **Configure test repositories**:
   ```bash
   cp manual-test-repos.yml manual-test-repos.local.yml
   # Edit manual-test-repos.local.yml with real repository names
   ```

2. **Run batch tests**:
   ```bash
   # Test save operation on all configured repos
   ./scripts/manual-testing/batch-test.sh save
   
   # Test restore operation on all configured repos
   ./scripts/manual-testing/batch-test.sh restore
   ```

### Analyze Results

View test results and data:

```bash
./scripts/manual-testing/analyze-results.sh
```

## Manual Testing Workflow

### 1. Environment Setup

Create a `.env` file:

```bash
# .env file format (no 'export' keyword)
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=owner/repo-name
```

Or export environment variables directly:

```bash
export GITHUB_TOKEN=your_github_token_here
export GITHUB_REPO=owner/repo-name
```

### 2. Container Testing Options

#### Option A: Direct Docker Commands

```bash
# Build container
make docker-build

# Test save operation
docker run --rm \
    -v $(pwd)/manual-test-data:/data \
    -e GITHUB_TOKEN=$GITHUB_TOKEN \
    -e GITHUB_REPO=microsoft/vscode \
    -e OPERATION=save \
    github-data

# Test restore operation
docker run --rm \
    -v $(pwd)/manual-test-data:/data \
    -e GITHUB_TOKEN=$GITHUB_TOKEN \
    -e GITHUB_REPO=microsoft/vscode \
    -e OPERATION=restore \
    github-data
```

#### Option B: Makefile Commands

```bash
# Save operation
GITHUB_TOKEN=your_token GITHUB_REPO=owner/repo make docker-run-save

# Restore operation  
GITHUB_TOKEN=your_token GITHUB_REPO=owner/repo make docker-run-restore
```

#### Option C: Docker Compose

```bash
# Set environment variables
export GITHUB_TOKEN=your_token
export GITHUB_REPO=owner/repo

# Run save operation
make docker-compose-up-save

# Run restore operation
make docker-compose-up-restore
```

### 3. Data Verification

After running tests, verify the data:

```bash
# Check data directory structure
ls -la manual-test-data/owner-repo/

# Analyze JSON files
jq . manual-test-data/owner-repo/issues.json | head -20
jq . manual-test-data/owner-repo/labels.json | head -10
```

## Test Repository Recommendations

### Small Repositories (< 10 issues)
- Good for quick testing and debugging
- Fast execution
- Easy to verify manually

### Medium Repositories (10-100 issues)
- Realistic testing scenarios
- Good for performance testing
- Reasonable verification time

### Large Repositories (> 100 issues)
- Stress testing
- Performance evaluation
- Rate limiting testing

## Expected Data Structure

After successful save operation, expect these files:

```
manual-test-data/owner-repo/
├── issues.json          # All issues with comments
├── labels.json          # All repository labels
└── metadata.json        # Backup metadata
```

### File Contents

- **issues.json**: Array of GitHub issue objects with embedded comments
- **labels.json**: Array of GitHub label objects
- **metadata.json**: Backup timestamp, repository info, and operation details

## Troubleshooting

### Authentication Issues
```bash
# Test token access
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

### Container Issues
```bash
# Check container logs
docker logs <container_id>

# Run container interactively for debugging
docker run -it --rm github-data /bin/bash
```

### Data Issues
```bash
# Verify JSON files are valid
jq . manual-test-data/owner-repo/issues.json > /dev/null
jq . manual-test-data/owner-repo/labels.json > /dev/null
```

### Permission Issues
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER manual-test-data/
```

## Best Practices

1. **Start Small**: Begin with repositories that have few issues
2. **Test Both Operations**: Always test both save and restore
3. **Verify Data**: Check JSON files after each operation
4. **Monitor Rate Limits**: GitHub API has rate limits
5. **Clean Up**: Remove test data when done

## Integration with Automated Tests

Manual testing complements the automated test suite:

- **Automated tests**: `/tests/test_container_integration.py`
- **Manual tests**: Real repositories with actual data
- **Both are important** for comprehensive validation

## Data Cleanup

Clean up test data when finished:

```bash
# Remove all manual test data
rm -rf manual-test-data/

# Remove specific repository data
rm -rf manual-test-data/owner-repo/
```