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
  - [Boundary Mock Standardization](#boundary-mock-standardization)
  - [Error Testing and Error Handling Integration](#error-testing-and-error-handling-integration)
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

- `@pytest.mark.container`: All Docker-related tests
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

### Enhanced Marker-Based Commands

```bash
# Performance-based test execution
make test-fast-only           # Fast tests only (< 1 second)
make test-unit-only           # Unit tests only
make test-integration-only    # Integration tests (excluding containers)
make test-container-only      # Container tests only

# Feature-specific test execution
make test-by-feature FEATURE=labels        # Label management tests
make test-by-feature FEATURE=sub_issues    # Sub-issues workflow tests
make test-by-feature FEATURE=pull_requests # Pull request tests
make test-by-feature FEATURE=issues        # Issue management tests
make test-by-feature FEATURE=comments      # Comment management tests

# Workflow-specific test execution
make test-by-markers MARKERS="backup_workflow"      # Backup workflow tests
make test-by-markers MARKERS="restore_workflow"     # Restore workflow tests
make test-by-markers MARKERS="github_api"           # GitHub API interaction tests
make test-by-markers MARKERS="storage"              # Storage and persistence tests

# Combined marker execution
make test-by-markers MARKERS="fast and labels"      # Fast label tests
make test-by-markers MARKERS="integration and github_api"  # API integration tests
make test-by-markers MARKERS="unit and storage"     # Unit storage tests

# Development workflow commands
make test-dev                 # Development workflow (fast + integration, no containers)
make test-ci                  # CI workflow (all tests with coverage)

# Test discovery and information
make test-list-markers        # List all available test markers
make test-collect-only        # Show test collection without running tests
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

### Test Categories Script

For advanced marker-based test execution:

```bash
# Run categorized tests with the test-categories script
python scripts/test-categories.py --fast           # Fast tests only
python scripts/test-categories.py --unit           # Unit tests only
python scripts/test-categories.py --integration    # Integration tests only
python scripts/test-categories.py --container      # Container tests only

# Feature-specific execution
python scripts/test-categories.py --feature labels      # Label tests
python scripts/test-categories.py --feature sub_issues  # Sub-issues tests

# With coverage reporting
python scripts/test-categories.py --unit --coverage     # Unit tests with coverage
python scripts/test-categories.py --fast --coverage     # Fast tests with coverage

# Default: runs all test categories in sequence
python scripts/test-categories.py
```

## Test Organization

### Directory Structure

```
tests/
├── __init__.py                          # Test package initialization
├── conftest.py                          # Global test configuration
├── shared/                              # Shared test infrastructure
│   ├── __init__.py                     # Comprehensive fixture exports
│   ├── fixtures.py                     # Core and enhanced fixtures
│   ├── enhanced_fixtures.py            # Advanced testing patterns
│   ├── mocks.py                        # Mock utilities and factories
│   ├── builders.py                     # Data builder patterns
│   └── helpers.py                      # Test helper utilities
├── integration/                         # Integration tests directory
│   ├── __init__.py                     # Integration test package
│   ├── test_*.py                       # Integration test files
├── mocks/                              # Mock implementations
│   ├── __init__.py                     # Mock package
│   ├── mock_github_service.py          # GitHub service mocks
│   └── mock_storage_service.py         # Storage service mocks
├── github/                             # GitHub-specific tests
│   └── utils/                          # GitHub utility tests
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

### Comprehensive Marker System

The project uses an extensive marker system for test organization and selective execution. Markers are automatically applied based on file patterns and can be manually added for specific scenarios.

#### Performance Markers

- `@pytest.mark.fast` - Tests completing in < 1 second (suitable for TDD cycles)
- `@pytest.mark.medium` - Tests completing in 1-10 seconds (integration tests)
- `@pytest.mark.slow` - Tests completing in > 10 seconds (container/end-to-end tests)

#### Test Type Markers

- `@pytest.mark.unit` - Isolated component tests with mocked dependencies
- `@pytest.mark.integration` - Tests verifying component interactions
- `@pytest.mark.container` - Full Docker workflow tests

#### Feature Area Markers

- `@pytest.mark.labels` - Label management functionality
- `@pytest.mark.issues` - Issue management functionality
- `@pytest.mark.comments` - Comment management functionality
- `@pytest.mark.sub_issues` - Sub-issues workflow functionality
- `@pytest.mark.pull_requests` - Pull request workflow functionality

#### Infrastructure Markers

- `@pytest.mark.github_api` - GitHub API interaction tests (real or mocked)
- `@pytest.mark.storage` - Data storage and persistence tests
- `@pytest.mark.backup_workflow` - Backup operation workflows
- `@pytest.mark.restore_workflow` - Restore operation workflows

#### Special Scenario Markers

- `@pytest.mark.empty_repository` - Empty repository scenario tests
- `@pytest.mark.large_dataset` - Large dataset scenario tests
- `@pytest.mark.rate_limiting` - Rate limiting behavior tests
- `@pytest.mark.error_simulation` - Error condition simulation tests

#### Enhanced Fixture Category Markers

- `@pytest.mark.enhanced_fixtures` - Tests using enhanced fixture patterns
- `@pytest.mark.data_builders` - Tests using dynamic data builder fixtures
- `@pytest.mark.workflow_services` - Tests using workflow service fixtures
- `@pytest.mark.performance_fixtures` - Tests using performance monitoring fixtures

#### Additional Markers

- `@pytest.mark.performance` - Performance testing and benchmarking
- `@pytest.mark.memory_intensive` - Tests with high memory usage
- `@pytest.mark.simple_data` - Tests with simple data structures
- `@pytest.mark.complex_hierarchy` - Tests with complex hierarchical data
- `@pytest.mark.temporal_data` - Tests with time-sensitive data patterns
- `@pytest.mark.mixed_states` - Tests with mixed state data (open/closed, etc.)

#### Automatic Marker Assignment

The test system automatically applies markers based on patterns:

- **Container tests**: Auto-marked with `container` and `slow`
- **Integration tests**: Auto-marked with `integration` and `medium`
- **Other tests**: Auto-marked with `unit` and `fast`
- **Feature areas**: Auto-marked based on filename patterns (e.g., "sub_issues" → `sub_issues`)
- **GitHub API tests**: Auto-marked based on code analysis

#### Test Selection Examples

```bash
# Fast development cycle - TDD workflow
pdm run pytest -m fast

# Feature-focused development
pdm run pytest -m labels                    # All label-related tests
pdm run pytest -m sub_issues               # All sub-issues tests
pdm run pytest -m "labels and unit"        # Unit tests for labels only

# Performance-based selection
pdm run pytest -m "fast and not container" # Fast tests excluding containers
pdm run pytest -m "medium and integration" # Medium-speed integration tests
pdm run pytest -m slow                     # All slow tests

# Infrastructure testing
pdm run pytest -m github_api               # GitHub API interaction tests
pdm run pytest -m storage                  # Storage and persistence tests
pdm run pytest -m "backup_workflow or restore_workflow"  # Workflow tests

# Scenario-based testing
pdm run pytest -m empty_repository         # Empty repository scenarios
pdm run pytest -m large_dataset           # Large dataset scenarios
pdm run pytest -m error_simulation        # Error handling tests
pdm run pytest -m rate_limiting           # Rate limiting tests

# Complex combinations
pdm run pytest -m "integration and github_api and not container"  # API integration tests
pdm run pytest -m "unit and (labels or issues)"  # Unit tests for labels or issues
pdm run pytest -m "fast and storage"             # Fast storage tests

# Development workflows
pdm run pytest -m "fast or (integration and not container)"  # Development cycle
pdm run pytest -m "not slow"                                 # Exclude slow tests
pdm run pytest -m "enhanced_fixtures"                        # Enhanced fixture tests
```

Each test file should declare its markers at the top:

```python
import pytest

# For unit tests
pytestmark = [pytest.mark.unit]

# For integration tests
pytestmark = [pytest.mark.integration]

# For container tests
pytestmark = [pytest.mark.container, pytest.mark.integration, pytest.mark.slow]
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

pytestmark = [pytest.mark.container, pytest.mark.integration, pytest.mark.slow]

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

### Error Simulation Test Structure ⭐ **NEW**

```python
import pytest
import requests
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

pytestmark = [pytest.mark.integration, pytest.mark.error_simulation]

class TestErrorHandling:
    """Error handling and resilience tests."""

    def test_api_failure_resilience(self, sample_github_data):
        """Test system resilience to API failures."""
        # ✅ Hybrid factory pattern for error testing
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
        
        # ✅ Configure specific error scenarios
        mock_boundary.create_label.side_effect = [
            {"id": 100, "name": "success"},      # Success
            Exception("API rate limit exceeded"), # Failure
        ]
        
        # Test error handling logic
        with pytest.raises(Exception, match="Failed to create label"):
            # Your error handling test implementation
            pass

    def test_network_timeout_handling(self, sample_github_data):
        """Test handling of network timeouts."""
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
        
        # ✅ Timeout simulation
        mock_boundary.create_issue.side_effect = requests.exceptions.Timeout("Request timed out")
        
        # Test timeout handling logic
        pass

    def test_malformed_data_handling(self):
        """Test handling of malformed API responses."""
        # ✅ Use factory with edge case data
        mock_boundary = MockBoundaryFactory.create_auto_configured({})
        
        # ✅ Simulate malformed responses
        mock_boundary.get_repository_issues.return_value = [
            {"id": None, "title": "", "body": None}  # Malformed data
        ]
        
        # Test malformed data handling
        pass

    @pytest.mark.parametrize("error_type,error_instance", [
        ("connection", ConnectionError("Network down")),
        ("timeout", requests.exceptions.Timeout("Request timeout")),
        ("rate_limit", Exception("Rate limit exceeded")),
    ])
    def test_various_error_scenarios(self, sample_github_data, error_type, error_instance):
        """Test various error scenarios with parameterized data."""
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
        mock_boundary.create_label.side_effect = error_instance
        
        # Test each error scenario
        pass
```

### Comprehensive Shared Fixture System

The project implements a sophisticated shared fixture system organized in `tests/shared/` that provides enhanced testing capabilities and follows established patterns for different test scenarios.

```
tests/shared/
├── __init__.py               # Comprehensive fixture exports
├── fixtures.py               # Core and enhanced fixtures
├── enhanced_fixtures.py      # Advanced testing patterns
├── mocks.py                  # Mock utilities and factories
└── builders.py               # Data builder patterns
```

#### Core Infrastructure Fixtures

```python
from tests.shared import (
    temp_data_dir,               # Basic temp directory
    sample_github_data,          # Comprehensive sample data
    github_service_mock,         # Basic GitHub service mock
    storage_service_mock,        # Storage service mock
    github_service_with_mock,    # Service with mocked boundary
)
```

**Basic Infrastructure Fixtures:**
- `temp_data_dir`: Clean temporary directory for each test (< 10ms setup)
- `sample_github_data`: Comprehensive GitHub API sample data (session-scoped, ~50ms setup)
- `github_service_mock`: Basic GitHub service mock (< 20ms setup)
- `storage_service_mock`: Storage service mock
- `github_service_with_mock`: GitHub service with mocked boundary

#### Enhanced Mock Fixtures

```python
from tests.shared import (
    mock_boundary_class,         # Mock GitHubApiBoundary class for patching
    mock_boundary,              # Configured mock boundary instance
    boundary_with_repository_data, # Enhanced boundary mock
)
```

**Scenario-Specific Fixtures:**
- `boundary_with_repository_data`: Full repository data responses using realistic sample data
- `boundary_with_large_dataset`: Large dataset simulation (250+ items) for performance testing
- `boundary_with_empty_repository`: Empty repository simulation for edge case testing
- `boundary_with_api_errors`: Simulate various GitHub API errors (ConnectionError, Timeout, etc.)
- `boundary_with_rate_limiting`: Simulate rate limiting scenarios

#### Specialized Data Fixtures

```python
from tests.shared import (
    empty_repository_data,       # Empty repository scenario data
    sample_sub_issues_data,      # Sub-issues hierarchical data
    sample_pr_data,             # Pull request workflow data
    sample_labels_data,         # Label management data
    complex_hierarchy_data,      # Complex sub-issue hierarchy data
)
```

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

### Fixture Usage Patterns

#### Pattern 1: Basic Unit Test

```python
import pytest
from tests.shared import temp_data_dir, sample_labels_data

@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.labels
def test_label_validation(sample_labels_data):
    """Test label validation logic."""
    # Use sample_labels_data for test input
    pass
```

#### Pattern 2: Service Integration Test

```python
import pytest
from tests.shared import github_service_with_mock, temp_data_dir

@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.github_api
def test_service_integration(github_service_with_mock, temp_data_dir):
    """Test service integration with mocked boundary."""
    # Use pre-configured service and temp directory
    pass
```

#### Pattern 3: Storage Workflow Test

```python
import pytest
from tests.shared import temp_data_dir, storage_service_mock, sample_github_data

@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.storage
def test_storage_workflow(temp_data_dir, storage_service_mock, sample_github_data):
    """Test complete storage workflow."""
    # Use all three fixtures for comprehensive testing
    pass
```

#### Pattern 4: Complex Scenario Test

```python
import pytest
from tests.shared import (
    temp_data_dir,
    complex_hierarchy_data,
    github_service_with_mock
)

@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.sub_issues
@pytest.mark.large_dataset
def test_complex_hierarchy_workflow(
    temp_data_dir,
    complex_hierarchy_data,
    github_service_with_mock
):
    """Test complex sub-issues hierarchy workflow."""
    # Use specialized data and services for complex scenarios
    pass
```

#### Fixture Selection Guidelines

| Test Complexity | Recommended Fixture Category | Setup Time | Best Use Case |
|------------------|------------------------------|------------|---------------|
| Simple | Core fixtures | < 20ms | Standard testing |
| Medium | Enhanced boundary mocks | < 50ms | Realistic scenarios |
| Complex | Data builders + error simulation | 50-200ms | Custom scenarios |
| End-to-end | Workflow service fixtures | < 100ms | Complete workflows |

#### Fixture Best Practices

1. **Start with minimal fixtures** - Use only what you need
2. **Prefer shared fixtures** - Avoid creating test-specific fixtures
3. **Combine appropriately** - Use multiple fixtures for complex scenarios
4. **Follow naming conventions** - Use descriptive fixture parameter names

#### Import Organization

```python
# Preferred import style
from tests.shared import (
    temp_data_dir,
    sample_github_data,
    github_service_with_mock,
    storage_service_mock
)

# Avoid importing individual modules
# from tests.shared.fixtures import temp_data_dir  # Not preferred
```

#### Fixture Scope Awareness

- Most fixtures use `function` scope for test isolation
- Use `session` or `module` scope fixtures sparingly
- Be aware of fixture cleanup behavior

#### Common Patterns by Test Type

**Unit Tests:**
- Use data fixtures (`sample_*_data`)
- Minimal service mocking
- Focus on single component behavior

**Integration Tests:**
- Use service fixtures (`*_service_mock`)
- Combine data and service fixtures
- Test component interactions

**Container Tests:**
- Use `temp_data_dir` for file operations
- Combine with service fixtures for end-to-end workflows
- Include cleanup verification

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

## Test Development Workflow

### Recommended Development Cycle

#### 1. TDD Cycle (Fast Feedback)
```bash
# Fast tests for immediate feedback during development
make test-fast-only           # < 1 second tests only
make test-unit-only          # Unit tests for quick validation
```

#### 2. Feature Development
```bash
# Feature-specific testing during development
make test-by-feature FEATURE=labels        # Label feature development
make test-by-feature FEATURE=sub_issues    # Sub-issues feature development
```

#### 3. Integration Validation
```bash
# Integration testing before commit
make test-integration-only    # Integration tests excluding containers
make test-dev                # Fast + integration (no containers)
```

#### 4. Full Validation
```bash
# Complete validation before merge
make test-ci                 # All tests with coverage
make check-all               # Full quality validation
```

### Marker-Based Development Patterns

#### TDD Workflow
```bash
# 1. Write failing test
# 2. Run fast tests to see failure
make test-fast-only

# 3. Implement minimal code
# 4. Run fast tests to see pass
make test-fast-only

# 5. Refactor
# 6. Run integration tests
make test-integration-only
```

#### Feature Development Workflow
```bash
# Focus on specific feature area
make test-by-markers MARKERS="labels and unit"      # Unit tests for labels
make test-by-markers MARKERS="labels and fast"      # Fast label tests
make test-by-markers MARKERS="labels"               # All label tests
```

#### Bug Fix Workflow
```bash
# Reproduce with specific scenario markers
make test-by-markers MARKERS="error_simulation"     # Error scenarios
make test-by-markers MARKERS="large_dataset"        # Large data scenarios
make test-by-markers MARKERS="rate_limiting"        # Rate limiting scenarios
```

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

### Boundary Mock Standardization

The GitHub Data project uses an advanced **boundary mock factory system** that provides 100% protocol completeness with automatic validation. This system eliminates manual mock configuration and prevents protocol extension failures.

#### MockBoundaryFactory - Enhanced Mock Creation

**Location:** `tests/shared/mocks/boundary_factory.py`

The MockBoundaryFactory provides automated, protocol-complete boundary mocks with intelligent configuration:

##### Core Factory Methods

```python
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

# ✅ RECOMMENDED: Auto-configured with 100% protocol completeness
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

# ✅ RECOMMENDED: Protocol-complete with validation
mock_boundary = MockBoundaryFactory.create_protocol_complete(sample_github_data)

# ✅ GOOD: For restore workflows
mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)

# ✅ ACCEPTABLE: Traditional patterns (still protocol-complete)
mock_boundary = MockBoundaryFactory.create_with_data("full", sample_data=sample_github_data)
```

##### Before/After Comparison

**❌ OLD WAY - Manual Configuration (AVOID):**
```python
# Manual mock setup - brittle and protocol-incomplete
mock_boundary = Mock()
mock_boundary.get_repository_labels.return_value = []
mock_boundary.get_repository_issues.return_value = sample_data["issues"]
mock_boundary.get_all_issue_comments.return_value = []
mock_boundary.get_repository_pull_requests.return_value = []
mock_boundary.get_all_pull_request_comments.return_value = []
# Missing 20+ other required protocol methods!
# Breaks when new protocol methods are added!
```

**✅ NEW WAY - Factory Pattern (RECOMMENDED):**
```python
# Factory-based setup - robust and protocol-complete
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
# All 28+ protocol methods automatically configured
# Future-proof: new methods included automatically
# 100% protocol completeness guaranteed
```

#### Protocol Validation System

**Location:** `tests/shared/mocks/protocol_validation.py`

The validation system ensures boundary mocks are protocol-complete and catches configuration issues:

##### Validation in Tests

```python
from tests.shared.mocks.protocol_validation import (
    validate_boundary_mock, assert_boundary_mock_complete
)

def test_with_boundary_validation(sample_github_data):
    """Example test with protocol validation."""
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

    # ✅ Validate protocol completeness
    assert validate_boundary_mock(mock_boundary)

    # ✅ Or use assertion (raises detailed error if incomplete)
    assert_boundary_mock_complete(mock_boundary)

    # Your test logic here...
```

##### Validation Reports

```python
from tests.shared.mocks.protocol_validation import ProtocolValidator

# Generate detailed validation report
report = ProtocolValidator.generate_validation_report(mock_boundary, GitHubApiBoundary)
print(report)
# Output:
# ✅ **PASSED: Mock boundary is fully protocol-compliant**
# **Protocol completeness**: 100.0%
# **Total protocol methods**: 28
# **Properly configured**: 28
```

#### Migration from Manual Mocks

The project includes migration utilities to help convert manual boundary mocks to factory patterns:

##### Migration Detection

```python
from tests.shared.mocks.migration_utils import BoundaryMockMigrator

# Analyze test file for manual mock patterns
patterns = BoundaryMockMigrator.detect_manual_mock_patterns(file_content)
report = BoundaryMockMigrator.create_migration_report(file_path, patterns)
```

##### Quick Migration Guide

1. **Identify Manual Mock Usage:**
   ```python
   # Look for these patterns in your tests:
   mock_boundary = Mock()  # ❌ Manual creation
   mock_boundary.get_*.return_value = []  # ❌ Manual configuration
   ```

2. **Replace with Factory Pattern:**
   ```python
   # ✅ Replace with auto-configured factory
   mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
   ```

3. **Remove Manual Configurations:**
   ```python
   # ❌ Delete these lines (factory handles automatically):
   # mock_boundary.get_repository_labels.return_value = []
   # mock_boundary.get_repository_issues.return_value = []
   # ... (all other manual configurations)
   ```

4. **Add Custom Configurations (if needed):**
   ```python
   # ✅ Only add custom configs that differ from defaults
   mock_boundary.create_issue.side_effect = [
       {"number": 101}, {"number": 102}
   ]
   ```

#### Best Practices for Boundary Mocks

##### ✅ DO - Recommended Patterns

```python
class TestExample:
    """Example test class using best practices."""

    def test_save_workflow(self, sample_github_data):
        """Test with auto-configured boundary mock."""
        # ✅ Use factory with sample data
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

        # ✅ Validate protocol completeness in development
        assert validate_boundary_mock(mock_boundary)

        # ✅ Only add custom behavior when needed
        mock_boundary.create_issue.return_value = {"number": 999}

        # Your test logic...

    def test_restore_workflow(self):
        """Test restore with specialized factory method."""
        # ✅ Use specialized restore factory
        mock_boundary = MockBoundaryFactory.create_for_restore()

        # ✅ Custom configurations for restore behavior
        mock_boundary.create_issue.side_effect = [
            {"number": 101}, {"number": 102}
        ]

        # Your test logic...
```

##### ❌ DON'T - Anti-patterns to Avoid

```python
# ❌ DON'T: Manual Mock() creation
mock_boundary = Mock()
mock_boundary.get_repository_labels.return_value = []

# ❌ DON'T: Incomplete protocol implementation
mock_boundary.get_repository_issues.return_value = []
# Missing 25+ other required methods!

# ❌ DON'T: Hardcoded return values without sample data
mock_boundary.get_repository_labels.return_value = [
    {"name": "bug", "color": "ff0000"}  # Use sample_github_data instead
]

# ❌ DON'T: Ignoring validation failures
# Always ensure protocol completeness
```

#### Integration Test Examples

##### Complete Integration Test Structure

```python
import pytest
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

pytestmark = [pytest.mark.integration]

class TestGitHubIntegration:
    """Integration tests using enhanced boundary mocks."""

    @pytest.fixture
    def mock_github_service(self, sample_github_data):
        """Create protocol-complete GitHub service mock."""
        github_service = Mock()
        # ✅ Use auto-configured boundary with sample data
        boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
        github_service.boundary = boundary
        return github_service

    def test_save_workflow_integration(self, mock_github_service, temp_data_dir):
        """Test complete save workflow with boundary mock."""
        # Test uses protocol-complete mock automatically
        # All GitHub API methods properly configured
        # Uses realistic sample data
        pass

    def test_restore_workflow_integration(self, temp_data_dir, sample_github_data):
        """Test restore workflow with specialized boundary mock."""
        # ✅ Use restore-specific factory
        mock_boundary = MockBoundaryFactory.create_for_restore()

        # ✅ Custom restore responses
        mock_boundary.create_issue.side_effect = [
            {"number": 101, "title": "Restored Issue 1"},
            {"number": 102, "title": "Restored Issue 2"}
        ]

        # Test restore logic...
```

#### Advanced Configuration Patterns

##### Custom Data Integration

```python
def test_with_custom_data_integration(self):
    """Test with custom data while maintaining protocol completeness."""
    # ✅ Create custom data that extends sample data
    custom_data = {
        "labels": [{"name": "custom", "color": "blue"}],
        "issues": [{"number": 1, "title": "Custom Issue"}]
    }

    # ✅ Use factory with custom data
    mock_boundary = MockBoundaryFactory.create_auto_configured(custom_data)

    # ✅ Validate it's still protocol complete
    assert validate_boundary_mock(mock_boundary)
```

##### Error Simulation with Factory

```python
def test_error_handling_with_factory(self, sample_github_data):
    """Test error handling with protocol-complete boundary."""
    # ✅ Start with complete boundary
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

    # ✅ Add error simulation to specific methods
    mock_boundary.create_issue.side_effect = Exception("API Error")

    # ✅ Verify other methods still work (protocol complete)
    assert mock_boundary.get_repository_labels() == sample_github_data["labels"]
```

##### Hybrid Factory + Custom Override Pattern ⭐ **RECOMMENDED FOR ERROR TESTING**

The hybrid pattern is the recommended approach for error testing, combining factory protocol completeness with custom error simulation:

```python
@pytest.mark.integration
@pytest.mark.error_simulation
def test_hybrid_error_pattern(self, sample_github_data):
    """Demonstrate the hybrid factory + custom override pattern."""
    # ✅ Step 1: Factory provides protocol completeness
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # ✅ Step 2: Custom error simulation via side_effect
    mock_boundary.create_label.side_effect = [
        {"id": 100, "name": "bug"},           # Success
        Exception("Rate limit exceeded"),     # Error
        {"id": 101, "name": "enhancement"}    # Recovery
    ]
    
    # ✅ Step 3: Complex error scenarios
    mock_boundary.create_issue.side_effect = [
        {"number": 1, "id": 999},
        ConnectionError("Network failure"),
        {"number": 2, "id": 998}
    ]
    
    # ✅ All other methods remain protocol-complete and functional
    assert len(mock_boundary.get_repository_issues()) > 0
    assert mock_boundary.get_repository_labels() == sample_github_data["labels"]
```

**Benefits of Hybrid Pattern:**
- **Protocol Completeness**: All GitHub API methods automatically configured
- **Error Flexibility**: Custom error simulation via `side_effect` and `return_value`
- **Future-Proof**: New protocol methods included automatically  
- **Performance**: Factory-generated mocks are efficient
- **Maintainability**: Centralized base configuration with targeted customization

**Migration Pattern:**
```python
# ❌ BEFORE: Manual incomplete mock
mock_boundary = Mock()
mock_boundary.get_repository_labels.return_value = []
mock_boundary.create_label.side_effect = Exception("Error")
# Missing 25+ protocol methods!

# ✅ AFTER: Hybrid factory pattern  
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
mock_boundary.create_label.side_effect = Exception("Error")
# All protocol methods complete ✅
```

#### Troubleshooting Boundary Mocks

##### Common Issues and Solutions

**Issue: Protocol incomplete error**
```python
# ❌ Problem: Mock is missing required methods
mock_boundary = Mock()
mock_boundary.get_repository_labels.return_value = []

# ✅ Solution: Use factory for completeness
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
```

**Issue: New protocol method breaks tests**
```python
# ❌ Problem: Manual mocks don't include new methods
# When GitHubApiBoundary gets new methods, manual mocks break

# ✅ Solution: Factory automatically includes new methods
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
# Automatically includes all current and future protocol methods
```

**Issue: Custom behavior with protocol completeness**
```python
# ✅ Solution: Factory + custom configuration
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
# All protocol methods configured ✅

# Add custom behavior only where needed
mock_boundary.create_issue.side_effect = custom_side_effect
# Still protocol complete ✅
```

##### Validation and Debugging

```python
from tests.shared.mocks.protocol_validation import ProtocolValidator

def debug_boundary_mock(mock_boundary):
    """Debug helper for boundary mock issues."""
    is_complete, issues, details = ProtocolValidator.validate_protocol_completeness(
        mock_boundary, GitHubApiBoundary
    )

    if not is_complete:
        print(f"❌ Protocol incomplete: {details['completeness_percentage']:.1f}%")
        print(f"Missing methods: {issues}")

        # Generate detailed report
        report = ProtocolValidator.generate_validation_report(
            mock_boundary, GitHubApiBoundary
        )
        print(report)
    else:
        print("✅ Mock boundary is protocol complete!")
```

### Usage Pattern Examples

#### Simple Integration Test
```python
@pytest.mark.integration
@pytest.mark.fast
def test_basic_operation(sample_github_data, temp_data_dir):
    """Basic integration test with factory-based boundary mock."""
    # ✅ Use factory for protocol completeness
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

    # Your test logic here...
```

#### Complex Scenario Test
```python
@pytest.mark.integration
@pytest.mark.enhanced_fixtures
@pytest.mark.large_dataset
def test_large_dataset_scenario(boundary_with_large_dataset, performance_monitoring_services):
    """Complex test with enhanced fixtures and boundary factory."""
    # Enhanced fixtures already use factory pattern internally
    # Guaranteed protocol completeness
    pass
```

#### Error Handling Test
```python
@pytest.mark.integration
@pytest.mark.error_simulation
@pytest.mark.api_errors
def test_api_error_handling(sample_github_data):
    """Error simulation test with protocol-complete boundary."""
    # ✅ Start with complete boundary
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

    # ✅ Add error simulation
    mock_boundary.get_repository_issues.side_effect = Exception("API Error")

    # Test error handling logic...
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

4. **Boundary Mock Standards** ⭐ **NEW**
   - **Always use MockBoundaryFactory** instead of manual Mock() creation
   - **Ensure protocol completeness** with `create_auto_configured()` method
   - **Validate mocks in development** using protocol validation utilities
   - **Leverage shared sample data** for consistent test scenarios
   - **Use hybrid factory pattern for error testing** - combine protocol completeness with custom error simulation
   - See [Boundary Mock Standardization](#boundary-mock-standardization) for complete guide

5. **Error Testing Standards** ⭐ **NEW**
   - **Use hybrid factory + custom override pattern** for error simulation
   - **Start with protocol-complete boundary** via `MockBoundaryFactory.create_auto_configured()`
   - **Add custom error behavior** using `side_effect` and `return_value` overrides
   - **Test error recovery mechanisms** and graceful degradation
   - **Use error markers** (`@pytest.mark.error_simulation`) for test organization
   - **Cover multiple error scenarios** (timeouts, rate limits, malformed data, connection failures)
   - See [Error Testing and Error Handling Integration](#error-testing-and-error-handling-integration) for detailed guide

### General Testing

1. **AAA Pattern**: Arrange, Act, Assert
2. **Descriptive Names**: Test names should describe expected behavior
3. **Single Responsibility**: One test should test one thing
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Feedback**: Keep unit tests fast (< 1 second)

### Mock Usage

#### Standard Mock Usage with Factory Pattern ⭐ **RECOMMENDED**

```python
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

# ✅ Mock external dependencies with protocol completeness
@patch('src.github.service.GitHubApiBoundary')
def test_with_mocked_github(mock_boundary_class, sample_github_data):
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    mock_boundary_class.return_value = mock_boundary
    # All protocol methods automatically configured ✅
```

#### Hybrid Pattern for Error Testing ⭐ **RECOMMENDED FOR ERROR SCENARIOS**

```python
# ✅ Hybrid pattern: Factory + custom error simulation
@patch('src.github.service.GitHubApiBoundary')
def test_error_handling(mock_boundary_class, sample_github_data):
    # Step 1: Protocol-complete foundation
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # Step 2: Custom error behavior
    mock_boundary.create_issue.side_effect = [
        {"number": 1, "id": 999},           # Success
        Exception("API rate limit exceeded") # Error
    ]
    
    mock_boundary_class.return_value = mock_boundary
    # Test error handling implementation...
```

#### Legacy Pattern (Avoid for New Tests)

```python
# ❌ Avoid: Manual mock creation (incomplete protocol)
@patch('src.github.service.GitHubApiBoundary')
def test_with_manual_mock(mock_boundary_class):
    mock_boundary = Mock()  # Missing most protocol methods!
    mock_boundary.get_repository_labels.return_value = []
    mock_boundary_class.return_value = mock_boundary
    # Brittle and protocol-incomplete ❌
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

### Error Testing and Error Handling Integration

#### Overview

Error handling tests validate system resilience and failure recovery mechanisms. The GitHub Data project uses a hybrid approach combining MockBoundaryFactory protocol completeness with custom error simulation patterns.

#### Error Testing Best Practices

1. **Use Hybrid Factory + Custom Override Pattern** for error simulation
2. **Test both partial and complete failures** with realistic error scenarios
3. **Verify error recovery mechanisms** and graceful degradation
4. **Use appropriate error markers** for test selection (`@pytest.mark.error_simulation`)

#### Hybrid Factory Pattern for Error Testing ⭐ **RECOMMENDED**

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

#### Error Simulation Patterns

##### Network Timeout Simulation
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

##### API Rate Limiting Simulation
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

##### Malformed Data Handling
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

#### Complex Error Scenarios

##### Multi-Stage Error Testing
```python
@pytest.mark.slow
@pytest.mark.error_simulation
def test_complex_error_recovery(sample_github_data):
    """Test complex error scenarios with partial failures."""
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # ✅ Configure multiple error points
    mock_boundary.create_label.side_effect = [
        {"id": 100}, Exception("Temp failure"), {"id": 101}  # Mixed success/failure
    ]
    mock_boundary.create_issue.side_effect = [
        {"number": 1}, {"number": 2}  # All succeed
    ]
    
    # Test partial failure recovery logic...
```

##### Error State Validation
```python
def test_error_state_preservation(sample_github_data):
    """Test that error states are properly preserved and reported."""
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # ✅ Error simulation with state tracking
    mock_boundary.create_issue_comment.side_effect = Exception("Connection lost")
    
    # Test error state tracking...
    # Verify error reporting...
    # Validate recovery mechanisms...
```

#### Error Testing Migration Guidelines

When migrating existing error tests to the hybrid factory pattern:

##### Before Migration (Manual Mock Pattern)
```python
# ❌ OLD: Manual mock with incomplete protocol
def test_error_handling_old():
    mock_boundary = Mock()
    mock_boundary.get_repository_labels.return_value = []
    mock_boundary.create_label.side_effect = Exception("API Error")
    # Missing 25+ other protocol methods!
```

##### After Migration (Hybrid Factory Pattern)  
```python
# ✅ NEW: Factory + custom error simulation
def test_error_handling_new(sample_github_data):
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    # All protocol methods configured ✅
    mock_boundary.create_label.side_effect = Exception("API Error")
    # Custom error behavior preserved ✅
```

#### Error Testing Checklist

✅ **Migration Checklist for Error Tests:**
- [ ] Replace `Mock()` with `MockBoundaryFactory.create_auto_configured()`
- [ ] Preserve all `side_effect` error simulation patterns
- [ ] Maintain custom error response validation
- [ ] Verify protocol completeness with validation utilities
- [ ] Test both error conditions and recovery paths
- [ ] Use appropriate error markers (`@pytest.mark.error_simulation`)

✅ **Error Scenario Coverage:**
- [ ] API failures (rate limiting, timeouts, connection errors)
- [ ] Malformed data handling (None values, empty fields, invalid formats)
- [ ] Partial failure scenarios (some operations succeed, others fail)
- [ ] Recovery mechanisms (retry logic, graceful degradation)
- [ ] Error reporting and logging validation

#### Advanced Error Testing Patterns

##### Data-Driven Error Testing
```python
@pytest.mark.parametrize("error_scenario", [
    {"method": "create_label", "error": Exception("Rate limit")},
    {"method": "create_issue", "error": ConnectionError("Network down")},
    {"method": "create_comment", "error": TimeoutError("Request timeout")},
])
def test_various_api_errors(sample_github_data, error_scenario):
    """Test various API error scenarios with parameterized data."""
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # ✅ Apply error to specific method
    getattr(mock_boundary, error_scenario["method"]).side_effect = error_scenario["error"]
    
    # Test error handling for each scenario...
```

##### Performance Impact Testing with Errors
```python
@pytest.mark.performance  
@pytest.mark.error_simulation
def test_error_performance_impact(sample_github_data):
    """Test that error handling doesn't significantly impact performance."""
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # ✅ Simulate intermittent errors
    mock_boundary.create_issue.side_effect = [
        {"number": i} if i % 3 != 0 else Exception("Intermittent error")
        for i in range(100)
    ]
    
    # Measure performance with error conditions...
```

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
