# Docker Test Environments for Selective Operations

This directory contains Docker environment configurations for testing selective issue/PR operations in containerized environments.

## Environment Files

### `selective.env`
Standard selective operations test configuration with:
- Issues: 1-5, 10, 15-20
- PRs: 2, 4, 6-8
- Both issue and PR comments enabled

### `selective-restore.env`
Restore-specific configuration for testing:
- Restore only issues 1, 3, 5
- Issue comments enabled
- PRs disabled

### `selective-mixed.env`
Mixed boolean and selective configuration:
- Issues: all (boolean true)
- Issue comments: disabled (boolean false)
- PRs: selective ranges (10-15, 20, 25-30)
- PR comments enabled

### `selective-large-range.env`
Large-scale selective operations:
- Issues: 1-1000 (large range)
- PRs: 100-500 (medium range)
- All comments enabled

## Usage

### Basic Container Testing

```bash
# Test selective save operation
docker run --rm \
  --env-file docker/test-environments/selective.env \
  -v $(pwd)/test-data:/data \
  github-data:latest

# Test selective restore operation
docker run --rm \
  --env-file docker/test-environments/selective-restore.env \
  -v $(pwd)/test-data:/data \
  github-data:latest
```

### Development Testing

```bash
# Test with development build
docker build -t github-data:dev .
docker run --rm \
  --env-file docker/test-environments/selective.env \
  -v $(pwd)/dev-data:/data \
  github-data:dev
```

### Performance Testing

```bash
# Test large range performance
docker run --rm \
  --env-file docker/test-environments/selective-large-range.env \
  -v $(pwd)/perf-data:/data \
  -m 512m \
  github-data:latest
```

### CI/CD Integration

```bash
# Run all test environments in sequence
for env_file in docker/test-environments/*.env; do
  echo "Testing with $env_file"
  docker run --rm \
    --env-file "$env_file" \
    -v $(pwd)/test-output:/data \
    github-data:test
done
```

## Environment Variable Testing

### Valid Configurations

Test with various valid selective configurations:

```bash
# Single issue selection
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=test_token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUES="42" \
  -e INCLUDE_ISSUE_COMMENTS=true \
  -v $(pwd)/single-test:/data \
  github-data:latest

# Range selection
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=test_token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUES="1-10" \
  -e INCLUDE_PULL_REQUESTS="20-25" \
  -v $(pwd)/range-test:/data \
  github-data:latest

# Mixed selection
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=test_token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUES="1-5 10 15-20" \
  -e INCLUDE_PULL_REQUESTS="100 105-110 120" \
  -v $(pwd)/mixed-test:/data \
  github-data:latest
```

### Error Testing

Test error handling with invalid configurations:

```bash
# Invalid number format
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=test_token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUES="invalid-format" \
  -v $(pwd)/error-test:/data \
  github-data:latest

# Empty selection
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=test_token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUES="" \
  -v $(pwd)/empty-test:/data \
  github-data:latest

# Legacy format (should error)
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=test_token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUE_COMMENTS="1" \
  -v $(pwd)/legacy-test:/data \
  github-data:latest
```

## Integration with Test Suites

These environment files are used by:
- `tests/container/test_selective_container_workflows.py`
- Manual testing scenarios
- CI/CD pipeline validation
- Performance benchmarking

## Best Practices

1. **Use specific tokens**: Replace `test_token` with actual GitHub tokens for real testing
2. **Volume mounting**: Always mount a volume to `/data` for data persistence
3. **Memory limits**: Use `-m` flag to test memory constraints
4. **Timeout handling**: Set appropriate timeouts for large operations
5. **Error validation**: Test both success and failure scenarios

## Security Notes

- Never commit real GitHub tokens to these files
- Use environment variable substitution for sensitive data in CI/CD
- Test files use placeholder tokens that will fail authentication (by design)
- For real testing, provide tokens via secure environment variable injection