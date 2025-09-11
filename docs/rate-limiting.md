# Rate Limiting Documentation

This document provides comprehensive information about rate limiting implementation in the GitHub Data project.

## Overview

The GitHub Data project implements intelligent rate limiting to handle GitHub API constraints gracefully. Rate limiting is built into the `GitHubApiBoundary` class and automatically applied to all GitHub API operations.

## Architecture

### Components

- **`GitHubApiBoundary`**: Main API wrapper that coordinates rate limiting
- **`RateLimitHandler`**: Dedicated class that implements retry logic and monitoring
- **Retry Decorator Pattern**: All API operations are wrapped with retry logic

### Flow

```
User Request → GitHubService → GitHubApiBoundary → RateLimitHandler → GitHub API
                                    ↑                    ↓
                              Monitor & Retry ← Exception Handling
```

## Configuration

### Default Settings

```python
max_retries = 3         # Maximum retry attempts
base_delay = 1.0        # Base delay in seconds  
max_delay = 60.0        # Maximum delay cap in seconds
jitter = True           # Add randomization to delays
```

### Initialization

```python
# Default configuration (recommended)
boundary = GitHubApiBoundary(token)

# Custom configuration (for testing/special cases)
boundary = GitHubApiBoundary(
    token,
    max_retries=5,
    base_delay=2.0,
    max_delay=120.0,
    jitter=False
)
```

**Note**: Custom configuration is only available at the boundary layer. The service layer uses default settings.

## Retry Logic

### Exponential Backoff

Retry delays follow exponential backoff with optional jitter:

```
Attempt 1: base_delay * 2^0 = 1.0s (± jitter)
Attempt 2: base_delay * 2^1 = 2.0s (± jitter)  
Attempt 3: base_delay * 2^2 = 4.0s (± jitter)
Attempt 4: min(base_delay * 2^3, max_delay) = min(8.0s, 60.0s) = 8.0s (± jitter)
```

### Jitter Calculation

When enabled, jitter adds ±25% randomization to prevent thundering herd:

```python
jitter_range = delay * 0.25
actual_delay = delay + random.uniform(-jitter_range, jitter_range)
```

### Error Handling

| Exception Type | Behavior | Retry |
|---------------|----------|--------|
| `RateLimitExceededException` | Apply exponential backoff, retry up to max_retries | Yes |
| `GithubException` (other) | Log error, fail immediately | No |
| Other exceptions | Propagate without retry | No |

## Monitoring

### Rate Limit Status

The system monitors GitHub's rate limit status and provides warnings:

```python
# Check current rate limit status
status = boundary.get_rate_limit_status()
# Returns: {"core": {"limit": 5000, "remaining": 4999, "reset": "2025-01-01T12:00:00"}}
```

### Low Rate Limit Warnings

Automatic warnings when remaining requests drop below 100:

```
WARNING: GitHub API rate limit low: 50 requests remaining, resets at 2025-01-01T12:00:00
```

### Retry Logging

Each retry attempt is logged with context:

```
WARNING: GitHub API rate limit exceeded. Retrying in 2.1s (attempt 2/4)
ERROR: GitHub API rate limit exceeded. Max retries (3) reached.
```

## Implementation Details

### Boundary Pattern

The `GitHubApiBoundary` class implements a clean separation between GitHub API concerns and business logic:

- **Input**: Business objects and parameters
- **Output**: Raw JSON data from GitHub API
- **Responsibility**: Authentication, rate limiting, error handling

### Service Layer Integration

The `GitHubService` class uses the boundary with default rate limiting:

```python
class GitHubService:
    def __init__(self, token: str):
        self._boundary = GitHubApiBoundary(token)  # Uses defaults
```

### Operation Wrapping

All API operations are wrapped with retry logic:

```python
def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
    return self._execute_with_retry(
        lambda: self._fetch_repository_labels(repo_name)
    )
```

## Testing

### Test Categories

- **Unit Tests**: Individual component behavior (`test_rate_limit_handling.py`)
- **Configuration Tests**: Default and custom settings validation
- **Integration Tests**: End-to-end retry scenarios

### Key Test Scenarios

```python
# Rate limit exceeded with successful retry
def test_rate_limit_exceeded_with_successful_retry()

# Maximum retries reached
def test_rate_limit_exceeded_max_retries_reached()

# Low rate limit monitoring
def test_successful_operation_with_low_rate_limit_warning()

# Exponential backoff calculation
def test_retry_delay_calculation()
```

### Testing Best Practices

- Use `patch("time.sleep")` to speed up retry tests
- Mock `github_client.get_rate_limit()` for monitoring tests
- Test both success and failure scenarios
- Verify logging output with `caplog` fixture

## Best Practices

### For Developers

1. **Don't Override Defaults**: Default settings work for most use cases
2. **Test Rate Limiting**: Include retry scenarios in integration tests  
3. **Monitor Logs**: Watch for rate limit warnings in production
4. **Handle Exceptions**: Be prepared for `RateLimitExceededException` after max retries

### For Operations

1. **Monitor Rate Usage**: Track API consumption patterns
2. **Scale Gradually**: Large operations may hit rate limits
3. **Time Operations**: Schedule bulk operations during off-peak hours
4. **Token Management**: Use tokens with appropriate scopes only

## Troubleshooting

### Common Issues

**Problem**: Operations failing with rate limit exceptions
- **Cause**: Sustained high API usage exceeding GitHub limits
- **Solution**: Wait for rate limit reset or reduce operation frequency

**Problem**: Slow operations on large repositories  
- **Cause**: Rate limiting delays during processing
- **Solution**: Expected behavior; operations will complete eventually

**Problem**: No retry warnings in logs
- **Cause**: Successful operations or non-rate-limit errors
- **Solution**: Check error logs for other GitHub API issues

### Debugging

Enable detailed logging to troubleshoot rate limiting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Rate limiting logs will show:
# - Retry attempts and delays
# - Rate limit status checks
# - Low rate limit warnings
```

## GitHub API Context

### Rate Limits

GitHub enforces rate limits per token:

- **Authenticated requests**: 5,000 requests per hour
- **Search API**: 30 requests per minute  
- **Secondary rate limits**: Apply to specific endpoints

### Best Practices

- Use personal access tokens for higher limits
- Cache results when possible to reduce API calls
- Implement retry logic (✅ done in this project)
- Monitor rate limit headers in responses

## Related Documentation

- [GitHub API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [Testing Documentation](testing.md)
- [Contributing Guidelines](../CONTRIBUTING.md)