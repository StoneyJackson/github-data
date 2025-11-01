# Specialized Testing

[← Testing Guide](README.md)

## Overview

This document covers advanced and specialized testing approaches for the GitHub Data project, including error testing, container integration testing, advanced testing patterns, performance optimization, and testing tools. These specialized techniques extend the foundational testing knowledge covered in the main Testing Guide.

## Error Testing and Error Handling Integration

Error handling tests validate system resilience and failure recovery mechanisms. The GitHub Data project uses a hybrid approach combining MockBoundaryFactory protocol completeness with custom error simulation patterns.

### Hybrid Factory Pattern for Error Testing ⭐ **RECOMMENDED**

The hybrid pattern provides the benefits of protocol completeness while preserving the flexibility needed for complex error simulation:

```python
import pytest
import requests
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

@pytest.mark.integration
@pytest.mark.error_simulation
def test_api_failure_handling(sample_github_data):
    """Test handling of GitHub API failures with hybrid pattern."""
    # ✅ Step 1: Start with protocol-complete boundary
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

    # ✅ Step 2: Add specific error simulation via side_effect
    mock_boundary.create_label.side_effect = [
        {"id": 100, "name": "bug", "color": "d73a4a"},  # First succeeds
        Exception("API rate limit exceeded"),            # Second fails
    ]

    # ✅ Step 3: Test error handling logic
    with pytest.raises(Exception, match="Failed to create label"):
        # Your error handling test logic here
        pass

    # ✅ Step 4: Verify error state and recovery
    assert mock_boundary.create_label.call_count == 2
```

### Error Simulation Patterns

#### Network Timeout Simulation
```python
def test_network_timeout_handling(sample_github_data):
    """Test handling of network timeouts during API calls."""
    # ✅ Factory provides protocol completeness
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

    # ✅ Custom timeout simulation
    mock_boundary.create_issue.side_effect = [
        {"number": 101, "id": 999},                    # First succeeds
        requests.exceptions.Timeout("Request timed out"), # Second times out
    ]

    # Test timeout handling logic...
```

#### API Rate Limiting Simulation
```python
def test_rate_limiting_handling(sample_github_data):
    """Test handling of API rate limiting scenarios."""
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

    # ✅ Simulate rate limiting with custom responses
    mock_boundary.get_rate_limit_status.return_value = {
        "remaining": 0, "reset": 3600
    }
    mock_boundary.create_label.side_effect = Exception("Rate limit exceeded")

    # Test rate limiting logic...
```

#### Malformed Data Handling
```python
def test_malformed_data_handling():
    """Test handling of malformed or unexpected API responses."""
    # ✅ Use empty data factory for edge cases
    mock_boundary = MockBoundaryFactory.create_auto_configured({})

    # ✅ Simulate malformed responses
    mock_boundary.get_repository_issues.return_value = [
        {"id": None, "title": "", "body": None}  # Malformed issue data
    ]

    # Test malformed data handling...
```

### Error Testing Best Practices

1. **Use Hybrid Factory + Custom Override Pattern** for error simulation
2. **Test both partial and complete failures** with realistic error scenarios
3. **Verify error recovery mechanisms** and graceful degradation
4. **Use appropriate error markers** for test selection (`@pytest.mark.error_simulation`)

## Container Integration Testing

Container integration tests ensure the full Docker workflow functions correctly.

### Prerequisites

- Docker must be running
- docker-compose installed (for compose tests)
- Sufficient disk space for test images
- Network access for image building

### Test Helper Classes

#### DockerTestHelper

Provides utilities for Docker container testing:

```python
# Build test image
image_tag = DockerTestHelper.build_image()

# Run container with configuration
result = DockerTestHelper.run_container(
    image_tag,
    environment={"VAR": "value"},
    volumes={"/host/path": "/container/path"}
)

# Cleanup resources
DockerTestHelper.cleanup_containers()
DockerTestHelper.cleanup_images()
```

### Container Test Categories

1. **Build Tests**: Verify Dockerfile builds correctly
2. **Runtime Tests**: Test container execution and environment
3. **Volume Tests**: Validate data persistence and mounting
4. **Compose Tests**: Test service orchestration
5. **Performance Tests**: Validate build times and resource usage

## Advanced Testing Patterns

### Fixture Selection Guidelines

| Test Complexity | Recommended Fixture Category | Setup Time | Best Use Case |
|------------------|------------------------------|------------|---------------|
| Simple | Core fixtures | < 20ms | Standard testing |
| Medium | Enhanced boundary mocks | < 50ms | Realistic scenarios |
| Complex | Data builders + error simulation | 50-200ms | Custom scenarios |
| End-to-end | Workflow service fixtures | < 100ms | Complete workflows |

### Test Organization Strategies

#### File Organization
```
tests/
├── unit/                         # Unit tests (fast, isolated)
├── integration/                  # Integration tests (service interactions)
├── container/                    # Container integration tests
└── shared/                       # Shared test infrastructure
    ├── fixtures.py               # Core and enhanced fixtures
    ├── enhanced_fixtures.py      # Advanced testing patterns
    ├── mocks.py                  # Mock utilities and factories
    └── builders.py               # Data builder patterns
```

## Performance Optimization

### Test Execution Speed

1. **Use appropriate fixture scopes**
   - Session scope for expensive setup
   - Function scope for test isolation
   - Module scope for shared expensive resources

2. **Select efficient fixtures**
   - Core fixtures for simple scenarios
   - Enhanced fixtures only when needed
   - Avoid over-engineering test setup

3. **Organize tests by speed**
   - Group fast tests for development cycles
   - Separate slow tests for comprehensive validation
   - Use performance markers consistently

### Memory Management

1. **Monitor fixture memory usage**
   - Use session metrics to track memory patterns
   - Prefer lightweight fixtures for repeated tests
   - Clean up resources properly in fixture teardown

2. **Optimize data generation**
   - Cache expensive data generation when possible
   - Use parametrized factories for consistent scenarios
   - Avoid generating excessive test data

## Testing Scripts and Tools

### Development Testing Scripts

The project includes specialized scripts for enhanced testing workflows:

- **`scripts/test-development.py`**: Development workflow automation script
  - Fast development testing cycles
  - Enhanced fixture validation
  - Performance analysis and reporting
  - Fixture usage metrics

- **`scripts/manual-testing/`**: Manual container testing tools
  - Real repository testing against GitHub API
  - Container integration validation
  - Batch testing across multiple repositories
  - Manual data verification workflows

These scripts complement the standard testing commands and provide specialized workflows for development and validation scenarios.

---

[← Testing Guide](README.md) | [Test Infrastructure](test-infrastructure.md) | [Debugging →](reference/debugging.md)
