# Testing Guide

This document provides a comprehensive guide to testing in the GitHub Data project. The project uses a multi-layered testing approach with pytest to ensure code quality and reliability across all components.

## Table of Contents

- [Overview](#overview)
- [Test Categories](#test-categories)
- [Running Tests](#running-tests)
- [Test Organization](#test-organization)
- [Container Integration Testing](#container-integration-testing)
- [Writing Tests](#writing-tests)
- [Test Configuration](#test-configuration)
- [Continuous Integration](#continuous-integration)
- [Debugging Tests](#debugging-tests)
- [Advanced Testing Patterns](#advanced-testing-patterns)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)
- [Continuous Improvement](#continuous-improvement)
- [Troubleshooting](#troubleshooting)


## Overview

The GitHub Data project employs a comprehensive testing strategy that includes:

- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: Tests for component interactions and workflows
- **Container Integration Tests**: Full Docker workflow validation
- **Performance Tests**: Resource usage and timing validation

All tests use pytest with custom markers for organization and selective execution.

## Test Categories

### 1. Unit Tests (`@pytest.mark.unit`)

**Purpose**: Test individual functions and classes in isolation.

**Characteristics**:
- Fast execution (< 1 second each)
- No external dependencies
- Use mocks for external services
- High code coverage focus

**Examples**:
```python
def test_get_existing_env_var():
    """Test retrieval of existing environment variable."""
    with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
        result = _get_env_var('TEST_VAR')
        assert result == 'test_value'
```

**Location**: All test files with `pytestmark = [pytest.mark.unit]`

### 2. Integration Tests (`@pytest.mark.integration`)

**Purpose**: Test component interactions and end-to-end workflows.

**Characteristics**:
- Moderate execution time (1-10 seconds each)
- Test real component integration
- May use file system and temporary directories
- Mock external APIs

**Examples**:
```python
def test_complete_save_restore_cycle_preserves_data_integrity(
    self, mock_boundary_class, temp_data_dir, sample_github_data
):
    """Test that complete save → restore cycle preserves all data correctly."""
    # Test full save/restore workflow
```

**Location**: `tests/test_integration.py`

### 3. Container Tests (`@pytest.mark.container`)

**Purpose**: Test Docker container functionality and workflows.

**Characteristics**:
- Slow execution (30+ seconds each)
- Require Docker to be running
- Test full containerized workflows
- May create/destroy Docker resources

**Examples**:
```python
def test_dockerfile_builds_successfully(self):
    """Test that Dockerfile builds without errors."""
    image_tag = DockerTestHelper.build_image()
    assert image_tag == DockerTestHelper.IMAGE_NAME
```

**Location**: 
- `tests/test_container_integration.py`
- `tests/test_docker_compose_integration.py`

### 4. Additional Markers

- `@pytest.mark.docker`: All Docker-related tests
- `@pytest.mark.slow`: Tests that take significant time
- `@pytest.mark.integration`: All integration-level tests

## Running Tests

### Quick Commands

```bash
# Run all tests with source code coverage
make test

# Run only unit tests (fastest)
make test-unit

# Run integration tests (exclude container tests)
make test-integration

# Run all tests except container tests (good for development)
make test-fast

# Run container integration tests only (requires Docker)
make test-container

# Run tests with test file coverage analysis
make test-with-test-coverage

# Run fast tests with test file coverage analysis
make test-fast-with-test-coverage

# Run quality checks without container tests
make check

# Run all quality checks including container tests
make check-all
```

### Direct Pytest Commands

```bash
# Run specific test categories
pdm run pytest -m unit                    # Unit tests only
pdm run pytest -m integration             # All integration tests
pdm run pytest -m "integration and not container"  # Non-container integration
pdm run pytest -m container               # Container tests only
pdm run pytest -m "not slow"             # Exclude slow tests

# Run specific test files
pdm run pytest tests/test_main.py         # Single test file
pdm run pytest tests/test_container_integration.py::TestDockerBuild  # Specific class

# Run with options
pdm run pytest -v                         # Verbose output
pdm run pytest --timeout=300              # Set timeout
pdm run pytest --cov-report=html          # HTML coverage report
pdm run pytest -x                         # Stop on first failure
```

### Container Test Helper Script

For advanced container testing options:

```bash
# Run all container tests with cleanup
./scripts/test-containers

# Run specific test types
./scripts/test-containers container        # Container tests only  
./scripts/test-containers docker          # All Docker tests
./scripts/test-containers all             # All container integration tests

# Skip cleanup (useful for debugging)
./scripts/test-containers container no
./scripts/test-containers docker no

# Get help
./scripts/test-containers --help
```

## Test Organization

### Directory Structure

```
tests/
├── __init__.py                          # Test package initialization
├── test_main.py                         # Main module unit tests
├── test_json_storage.py                 # Storage layer unit tests
├── test_integration.py                  # Application integration tests
├── test_container_integration.py        # Docker container tests
└── test_docker_compose_integration.py   # Docker Compose tests
```

### File Naming Conventions

- `test_*.py`: All test files must start with `test_`
- `Test*`: Test classes must start with `Test`
- `test_*`: Test methods must start with `test_`

### Pytest Markers Usage

The project uses an extensive marker system for test organization and selection:

#### Marker Categories

**Test Type Markers:**
- `@pytest.mark.unit`: Unit tests (isolated, fast)
- `@pytest.mark.integration`: Integration tests (service interactions)
- `@pytest.mark.container`: Container-based tests (Docker required)

**Performance Markers:**
- `@pytest.mark.fast`: < 100ms execution time
- `@pytest.mark.medium`: 100ms - 1s execution time
- `@pytest.mark.slow`: > 1s execution time
- `@pytest.mark.performance`: Performance benchmarking tests

**Fixture Category Markers:**
- `@pytest.mark.enhanced_fixtures`: Tests using enhanced fixture patterns
- `@pytest.mark.data_builders`: Tests using dynamic data builders
- `@pytest.mark.error_simulation`: Tests using error simulation fixtures
- `@pytest.mark.workflow_services`: Tests using workflow service fixtures

**Scenario Markers:**
- `@pytest.mark.empty_repository`: Empty repository scenarios
- `@pytest.mark.large_dataset`: Large dataset scenarios
- `@pytest.mark.rate_limiting`: Rate limiting scenarios
- `@pytest.mark.api_errors`: API error scenarios

**Feature-Specific Markers:**
- `@pytest.mark.labels`: Label-related functionality
- `@pytest.mark.backup_workflow`: Backup workflow tests
- `@pytest.mark.restore_workflow`: Restore workflow tests

#### Test Selection Examples

```bash
# Fast development cycle - exclude slow tests
pytest -m "not slow and not container"

# Feature-focused development
pytest -m "labels" tests/integration/

# Performance testing
pytest -m "performance" --verbose

# Error handling validation
pytest -m "error_simulation or api_errors"

# Tests using enhanced fixtures
pytest -m "enhanced_fixtures"

# Workflow tests excluding slow ones
pytest -m "workflow_services and not slow"
```

Each test file should declare its markers at the top:

```python
import pytest

# For unit tests
pytestmark = [pytest.mark.unit]

# For integration tests  
pytestmark = [pytest.mark.integration]

# For container tests
pytestmark = [pytest.mark.container, pytest.mark.integration, pytest.mark.docker, pytest.mark.slow]
```

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

#### DockerComposeTestHelper

Provides utilities for Docker Compose testing:

```python
# Run compose command
result = DockerComposeTestHelper.run_compose_command("up", ["service-name"])

# Get service logs
logs = DockerComposeTestHelper.get_service_logs("service-name")

# Cleanup compose resources
DockerComposeTestHelper.cleanup_compose()
```

### Container Test Categories

1. **Build Tests**: Verify Dockerfile builds correctly
2. **Runtime Tests**: Test container execution and environment
3. **Volume Tests**: Validate data persistence and mounting
4. **Compose Tests**: Test service orchestration
5. **Performance Tests**: Validate build times and resource usage

## Writing Tests

### Unit Test Structure

```python
import pytest
from unittest.mock import Mock, patch

pytestmark = [pytest.mark.unit]

class TestComponentName:
    """Test cases for ComponentName."""
    
    def test_specific_behavior(self):
        """Test that specific behavior works correctly."""
        # Arrange
        input_data = "test input"
        expected_result = "expected output"
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_result
```

### Integration Test Structure

```python
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

pytestmark = [pytest.mark.integration]

class TestIntegrationScenario:
    """Integration tests for specific scenario."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data."""
        with TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_end_to_end_workflow(self, temp_data_dir):
        """Test complete workflow from start to finish."""
        # Test implementation
```

### Container Test Structure

```python
import pytest
import subprocess
from pathlib import Path

pytestmark = [pytest.mark.container, pytest.mark.integration, pytest.mark.docker, pytest.mark.slow]

class TestContainerBehavior:
    """Container integration tests."""
    
    @pytest.fixture
    def docker_image(self):
        """Build Docker image for tests."""
        yield DockerTestHelper.build_image()
        DockerTestHelper.cleanup_containers()
        DockerTestHelper.cleanup_images()
    
    def test_container_functionality(self, docker_image):
        """Test specific container functionality."""
        # Test implementation
```

### Test Fixtures

The project includes comprehensive shared fixtures for enhanced testing capabilities:

### Shared Fixture System

The project implements a comprehensive shared fixture system organized in `tests/shared/`:

```
tests/shared/
├── __init__.py               # Comprehensive fixture exports
├── fixtures.py               # Core and enhanced fixtures
├── enhanced_fixtures.py      # Advanced testing patterns
├── mocks.py                  # Mock utilities and factories
└── builders.py               # Data builder patterns
```

#### Core Fixtures

```python
from tests.shared import (
    temp_data_dir,               # Basic temp directory
    sample_github_data,          # Comprehensive sample data
    github_service_with_mock,    # Service with mocked boundary
    boundary_with_repository_data, # Enhanced boundary mock
    github_data_builder,         # Dynamic data builder
    backup_workflow_services     # Pre-configured workflow services
)
```

**Basic Infrastructure Fixtures:**
- `temp_data_dir`: Clean temporary directory for each test (< 10ms setup)
- `sample_github_data`: Comprehensive GitHub API sample data (session-scoped, ~50ms setup)
- `github_service_with_mock`: GitHub service with basic mocked boundary (< 20ms setup)

#### Enhanced Boundary Mocks

**Scenario-Specific Fixtures:**
- `boundary_with_repository_data`: Full repository data responses using realistic sample data
- `boundary_with_large_dataset`: Large dataset simulation (250+ items) for performance testing
- `boundary_with_empty_repository`: Empty repository simulation for edge case testing
- `boundary_with_api_errors`: Simulate various GitHub API errors (ConnectionError, Timeout, etc.)
- `boundary_with_rate_limiting`: Simulate rate limiting scenarios

#### Workflow Service Fixtures

**Pre-configured Service Compositions:**
- `backup_workflow_services`: Complete backup workflow testing environment
- `restore_workflow_services`: Complete restore workflow with pre-populated data files
- `error_handling_workflow_services`: Error handling workflow testing with partial failures
- `performance_monitoring_services`: Services with timing and performance monitoring

#### Data Builder Patterns

**Dynamic Data Generation:**
- `github_data_builder`: Build custom GitHub data for specific test scenarios
- `parametrized_data_factory`: Create predefined data scenarios (basic, large, pr_focused, etc.)

```python
# Example: Custom data building
@pytest.mark.data_builders
def test_custom_hierarchy(github_data_builder):
    data = (github_data_builder
            .reset()
            .with_labels(5)
            .with_issues(10)
            .with_sub_issue_hierarchy(depth=3, children_per_level=2)
            .build())
    
    assert len(data["sub_issues"]) > 0
```

## Test Configuration

### pytest.ini Configuration

Test configuration is centralized in the [`pytest.ini`](../pytest.ini) file, which includes:

- Test discovery paths and naming conventions
- Test markers for categorization  
- Coverage reporting settings
- Branch coverage configuration
- Output formatting (concise with short tracebacks)
- Timeout settings for different test types

### Coverage Configuration

The project uses pytest-cov with branch coverage enabled by default:

#### Coverage Types

- **Source Coverage** (default): Measures coverage of `src/` files only
  - Commands: `make test`, `make test-fast`, `make test-unit`, etc.
  - Purpose: Monitor production code test coverage
  
- **Test Coverage** (optional): Measures coverage of test files only  
  - Commands: `make test-with-test-coverage`, `make test-fast-with-test-coverage`
  - Purpose: Analyze how thoroughly test files themselves are tested

#### Coverage Features

- **Branch Coverage**: Enabled for all test scenarios to catch untested code paths
- **Terminal Report**: Shows missing lines during test execution with short tracebacks
- **HTML Report**: Detailed coverage analysis generated in `htmlcov/` directory
- **Target**: Aim for >90% coverage on `src/` directory

#### Configuration Files

Coverage settings are centralized in `pytest.ini`:
- Shared test configuration (markers, filterwarnings, timeout)
- Branch coverage enabled by default
- Concise output with detailed failure information

### Timeout Configuration

- **Unit Tests**: No timeout (should be fast)
- **Integration Tests**: 30-60 seconds per test
- **Container Tests**: 300 seconds (5 minutes) per test

## Continuous Integration

### Local Pre-commit Checks

Before committing, run:

```bash
make check          # Fast checks (excludes container tests)
make check-all      # Complete checks (includes container tests)
```

### CI Pipeline Stages

1. **Fast Feedback**: Unit tests and linting
2. **Integration**: Non-container integration tests
3. **Container**: Full Docker workflow tests
4. **Quality Gates**: Coverage and performance validation

## Debugging Tests

### Common Debugging Commands

```bash
# Run single test with verbose output
pdm run pytest -v -s tests/test_main.py::TestMain::test_specific_case

# Run tests without capturing output
pdm run pytest -s

# Run tests with Python debugger
pdm run pytest --pdb

# Run tests with coverage and stop on first failure
pdm run pytest --cov=src -x

# Show test durations
pdm run pytest --durations=10
```

### Container Test Debugging

```bash
# Run container tests without cleanup for inspection
./scripts/test-containers container no

# Manually inspect test containers
docker ps -a --filter "name=github-data-test"
docker logs <container-name>

# Inspect test images
docker images --filter "reference=github-data-test*"

# Manual cleanup
docker system prune -f
```

### Debug Test Failures

1. **Check Test Output**: Use `-v` and `-s` flags for verbose output
2. **Isolate Tests**: Run single test methods to isolate issues
3. **Check Fixtures**: Verify test fixtures are set up correctly
4. **Environment**: Ensure test environment matches expectations
5. **Container Logs**: For container tests, check Docker logs

## Advanced Testing Patterns

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

#### Naming Conventions
- `test_<module>_unit.py` - Unit tests for specific modules
- `test_<feature>_integration.py` - Feature integration tests
- `test_<feature>_container.py` - Container-based tests

### Fixture Selection Guidelines

| Test Complexity | Recommended Fixture Category | Setup Time | Best Use Case |
|------------------|------------------------------|------------|---------------|
| Simple | Core fixtures | < 20ms | Standard testing |
| Medium | Enhanced boundary mocks | < 50ms | Realistic scenarios |
| Complex | Data builders + error simulation | 50-200ms | Custom scenarios |
| End-to-end | Workflow service fixtures | < 100ms | Complete workflows |

### Usage Pattern Examples

#### Simple Integration Test
```python
@pytest.mark.integration
@pytest.mark.fast
def test_basic_operation(github_service_with_mock, temp_data_dir):
    # Basic integration test with minimal setup
    pass
```

#### Complex Scenario Test
```python
@pytest.mark.integration
@pytest.mark.enhanced_fixtures
@pytest.mark.large_dataset
def test_large_dataset_scenario(boundary_with_large_dataset, performance_monitoring_services):
    # Complex test with enhanced fixtures
    pass
```

#### Error Handling Test
```python
@pytest.mark.integration
@pytest.mark.error_simulation
@pytest.mark.api_errors
def test_api_error_handling(boundary_with_api_errors, error_handling_workflow_services):
    # Error simulation and handling test
    pass
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

### Development Workflow Optimization

```bash
# CI/CD Pipeline stages
pytest -m "unit" --cov=src                                    # Unit test stage
pytest -m "integration and not container" --cov=src --cov-append  # Integration stage  
pytest -m "container" --cov=src --cov-append                      # Container stage
pytest -m "performance" --benchmark                               # Performance validation
```

## Best Practices

### Test Quality Standards

1. **Test readability**
   - Clear test names describing scenarios
   - Appropriate fixture usage for test complexity
   - Comprehensive test documentation

2. **Test maintainability**
   - Consistent marker usage across similar tests
   - Proper fixture selection for test needs
   - Regular cleanup of unused fixtures

3. **Test reliability**
   - Proper test isolation with fixture scopes
   - Consistent test data patterns
   - Reliable error simulation patterns

### General Testing

1. **AAA Pattern**: Arrange, Act, Assert
2. **Descriptive Names**: Test names should describe expected behavior
3. **Single Responsibility**: One test should test one thing
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Feedback**: Keep unit tests fast (< 1 second)

### Mock Usage

```python
# Mock external dependencies
@patch('src.github.service.GitHubApiBoundary')
def test_with_mocked_github(mock_boundary_class):
    mock_boundary = Mock()
    mock_boundary_class.return_value = mock_boundary
    # Test implementation
```

### Container Testing

1. **Resource Cleanup**: Always clean up Docker resources
2. **Timeout Handling**: Set appropriate timeouts for slow operations
3. **Error Scenarios**: Test both success and failure cases
4. **Resource Limits**: Test with constrained resources
5. **Image Size**: Validate reasonable image sizes

### Data Management

1. **Temporary Files**: Use `tempfile` for test data
2. **Test Isolation**: Don't share data between tests
3. **Cleanup**: Clean up test resources after use
4. **Realistic Data**: Use realistic test data that matches production

### Error Testing

1. **Use error simulation fixtures** for resilience testing
2. **Test both partial and complete failures**
3. **Verify error recovery mechanisms**
4. **Use appropriate error markers** for test selection

### Workflow Testing

1. **Use workflow services** for end-to-end scenarios
2. **Test complete workflows** rather than individual components
3. **Verify service interactions** and data flow
4. **Use appropriate workflow markers** for organization

### Performance Considerations

1. **Parallel Execution**: Design tests for parallel execution
2. **Resource Efficiency**: Minimize resource usage in tests
3. **Caching**: Leverage pytest fixtures for expensive setup
4. **Test Selection**: Use markers for selective test execution

## Continuous Improvement

### Metrics and Monitoring

1. **Track fixture usage patterns**
   - Monitor which fixtures are most used
   - Identify opportunities for optimization
   - Remove unused or redundant fixtures

2. **Monitor test performance**
   - Track test execution times
   - Identify slow tests for optimization
   - Validate performance improvements

3. **Analyze test organization**
   - Review marker effectiveness
   - Optimize test selection patterns
   - Improve development workflow efficiency

### Maintenance Strategies

1. **Regular fixture review**
   - Update fixtures to match evolving needs
   - Optimize fixture implementations
   - Maintain fixture documentation

2. **Test organization optimization**
   - Refactor test organization as needed
   - Update marker usage patterns
   - Improve test selection strategies

## Testing Scripts and Tools

### Development Testing Scripts

The project includes specialized scripts for enhanced testing workflows:

- **[scripts/test-development.py](scripts/test-development.md)**: Development workflow automation script
  - Fast development testing cycles
  - Enhanced fixture validation 
  - Performance analysis and reporting
  - Fixture usage metrics

- **[scripts/manual-testing/](scripts/manual-testing.md)**: Manual container testing tools
  - Real repository testing against GitHub API
  - Container integration validation
  - Batch testing across multiple repositories
  - Manual data verification workflows

These scripts complement the standard testing commands and provide specialized workflows for development and validation scenarios.

## Troubleshooting

### Common Issues

**Docker Tests Failing**:
- Ensure Docker is running
- Check available disk space
- Verify network connectivity
- Clean up Docker resources: `docker system prune -f`

**Timeout Errors**:
- Increase timeout values in pytest.ini
- Check for infinite loops or blocking operations
- Verify external service availability

**Import Errors**:
- Ensure PDM dependencies are installed: `make install-dev`
- Check PYTHONPATH configuration
- Verify virtual environment activation

**Coverage Issues**:
- Check that all source files are included in coverage
- Verify test coverage configuration in pytest.ini
- Use `--cov-report=html` for detailed coverage analysis

### Getting Help

1. **Documentation**: Check this guide and inline code comments
2. **Test Output**: Use verbose flags for detailed test information
3. **Logs**: Check test logs and container logs for errors
4. **Community**: Refer to pytest and Docker documentation
5. **Debugging**: Use Python debugger (`--pdb`) for interactive debugging

---

For more information about specific testing scenarios or to contribute to the test suite, see the project's [CONTRIBUTING.md](../CONTRIBUTING.md) guide.