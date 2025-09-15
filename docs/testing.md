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
- [Best Practices](#best-practices)

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

Common fixtures are available across tests:

```python
@pytest.fixture
def temp_data_dir():
    """Temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture  
def sample_github_data():
    """Sample GitHub API data for testing."""
    return {
        "labels": [...],
        "issues": [...],
        "comments": [...]
    }

@pytest.fixture
def docker_image():
    """Built Docker image for testing."""
    yield DockerTestHelper.build_image()
    # Cleanup happens automatically
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

## Best Practices

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

### Performance Considerations

1. **Parallel Execution**: Design tests for parallel execution
2. **Resource Efficiency**: Minimize resource usage in tests
3. **Caching**: Leverage pytest fixtures for expensive setup
4. **Test Selection**: Use markers for selective test execution

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