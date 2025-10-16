# Testing Guide

This document provides a comprehensive guide to testing in the GitHub Data project. The project uses a multi-layered testing approach with pytest to ensure code quality and reliability across all components.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Test Categories and Markers](#test-categories-and-markers)
- [Running Tests](#running-tests)
- [Test Organization](#test-organization)
- [Writing Tests](#writing-tests)
- [Shared Fixture System](#shared-fixture-system)
- [Boundary Mock Standardization](#boundary-mock-standardization)
- [Error Testing and Error Handling Integration](#error-testing-and-error-handling-integration)
- [Container Integration Testing](#container-integration-testing)
- [Test Configuration](#test-configuration)
- [Development Workflow](#development-workflow)
- [Advanced Testing Patterns](#advanced-testing-patterns)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)
- [Debugging Tests](#debugging-tests)
- [Testing Scripts and Tools](#testing-scripts-and-tools)
- [Troubleshooting](#troubleshooting)
- [Migration Guide](#migration-guide)

## Overview

The GitHub Data project employs a comprehensive testing strategy that includes:

- **Unit Tests**: Fast, isolated tests for individual components (< 1s each)
- **Integration Tests**: Tests for component interactions and workflows (1-10s each)
- **Container Integration Tests**: Full Docker workflow validation (30s+ each)
- **Performance Tests**: Resource usage and timing validation

All tests use pytest with custom markers for organization and selective execution.

## Quick Start

### Essential Commands

```bash
# Development cycle commands (recommended)
make test-fast              # All tests except container tests (fastest feedback)
make test-unit             # Unit tests only (fastest)
make test-integration      # Integration tests excluding containers

# Complete testing
make test                  # All tests with source code coverage
make test-container        # Container integration tests only

# Quality assurance
make check                 # All quality checks excluding container tests (fast)
make check-all            # Complete quality validation including container tests

# Coverage analysis
make test-with-test-coverage              # Coverage analysis of test files
make test-fast-with-test-coverage         # Fast tests with test file coverage
```

## Test Categories and Markers

### Core Test Types

#### 1. Unit Tests (`@pytest.mark.unit`)

**Purpose**: Test individual functions and classes in isolation.

**Characteristics**:
- Fast execution (< 1 second each)
- No external dependencies
- Use mocks for external services
- High code coverage focus

**Example**:
```python
import pytest
from unittest.mock import Mock, patch
from tests.shared import TestDataHelper, AssertionHelper

pytestmark = [pytest.mark.unit, pytest.mark.fast]

class TestComponentName:
    """Test cases for ComponentName."""
    
    def test_specific_behavior(self):
        """Test that specific behavior works correctly."""
        # Arrange
        test_data = TestDataHelper.create_test_label()
        
        # Act
        result = function_under_test(test_data)
        
        # Assert
        AssertionHelper.assert_valid_label(result)
        assert result.name == "test-label"
```

#### 2. Integration Tests (`@pytest.mark.integration`)

**Purpose**: Test component interactions and end-to-end workflows.

**Characteristics**:
- Moderate execution time (1-10 seconds each)
- Test real component integration
- May use file system and temporary directories
- Mock external APIs

**Example**:
```python
import pytest
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

pytestmark = [pytest.mark.integration]

class TestIntegrationScenario:
    """Integration tests for specific scenario."""

    def test_complete_save_restore_cycle(self, temp_data_dir, sample_github_data):
        """Test that complete save → restore cycle preserves all data correctly."""
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
        # Test full save/restore workflow
```

#### 3. Container Tests (`@pytest.mark.container`)

**Purpose**: Test Docker container functionality and workflows.

**Characteristics**:
- Slow execution (30+ seconds each)
- Require Docker to be running
- Test full containerized workflows
- May create/destroy Docker resources

**Example**:
```python
import pytest

pytestmark = [pytest.mark.container, pytest.mark.integration, pytest.mark.slow]

class TestContainerBehavior:
    """Container integration tests."""

    def test_dockerfile_builds_successfully(self):
        """Test that Dockerfile builds without errors."""
        image_tag = DockerTestHelper.build_image()
        assert image_tag == DockerTestHelper.IMAGE_NAME
```

### Comprehensive Marker System

#### Performance Markers
- `@pytest.mark.fast` - Tests completing in < 1 second (suitable for TDD cycles)
- `@pytest.mark.medium` - Tests completing in 1-10 seconds (integration tests)
- `@pytest.mark.slow` - Tests completing in > 10 seconds (container/end-to-end tests)

#### Feature Area Markers
- `@pytest.mark.labels` - Label management functionality
- `@pytest.mark.issues` - Issue management functionality
- `@pytest.mark.comments` - Comment management functionality
- `@pytest.mark.sub_issues` - Sub-issues workflow functionality
- `@pytest.mark.pull_requests` - Pull request workflow functionality

#### Infrastructure Markers
- `@pytest.mark.github_api` - GitHub API interaction tests
- `@pytest.mark.storage` - Data storage and persistence tests
- `@pytest.mark.rate_limiting` - Rate limiting behavior tests
- `@pytest.mark.backup_workflow` - Backup operation workflows
- `@pytest.mark.restore_workflow` - Restore operation workflows

#### Enhanced Fixture Category Markers
- `@pytest.mark.enhanced_fixtures` - Tests using enhanced fixture patterns
- `@pytest.mark.data_builders` - Tests using dynamic data builder fixtures
- `@pytest.mark.workflow_services` - Tests using workflow service fixtures
- `@pytest.mark.error_simulation` - Error condition simulation tests

## Running Tests

### Performance-Based Test Execution

```bash
# Fast development cycle
make test-fast-only           # Fast tests only (< 1 second)
make test-unit-only           # Unit tests only
make test-integration-only    # Integration tests (excluding containers)
make test-container-only      # Container tests only

# Development workflow
make test-dev                 # Development workflow (fast + integration, no containers)
make test-ci                  # CI workflow (all tests with coverage)
```

### Feature-Specific Test Execution

```bash
# Feature-specific testing
make test-by-feature FEATURE=labels        # Label management tests
make test-by-feature FEATURE=sub_issues    # Sub-issues workflow tests
make test-by-feature FEATURE=pull_requests # Pull request tests
make test-by-feature FEATURE=issues        # Issue management tests
make test-by-feature FEATURE=comments      # Comment management tests
```

### Direct Pytest Commands

```bash
# Run specific test categories
pdm run pytest -m unit                    # Unit tests only
pdm run pytest -m integration             # All integration tests
pdm run pytest -m "integration and not container"  # Non-container integration
pdm run pytest -m container               # Container tests only
pdm run pytest -m "not slow"             # Exclude slow tests

# Feature combinations
pdm run pytest -m "fast and labels"       # Fast label tests
pdm run pytest -m "integration and github_api"  # API integration tests
pdm run pytest -m "unit and storage"      # Unit storage tests

# Run specific test files
pdm run pytest tests/test_main.py         # Single test file
pdm run pytest tests/test_container_integration.py::TestDockerBuild  # Specific class

# Run with options
pdm run pytest -v                         # Verbose output
pdm run pytest --timeout=300              # Set timeout
pdm run pytest --cov-report=html          # HTML coverage report
pdm run pytest -x                         # Stop on first failure
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
├── unit/                               # Unit tests directory
│   ├── __init__.py                     # Unit test package
│   ├── README.md                       # Unit tests documentation
│   └── test_*.py                       # Unit test files
├── integration/                         # Integration tests directory
│   ├── __init__.py                     # Integration test package
│   └── test_*.py                       # Integration test files
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
- `test_<module>_unit.py` - Unit tests for specific modules
- `test_<feature>_integration.py` - Feature integration tests
- `test_<feature>_container.py` - Container-based tests
- `Test*`: Test classes must start with `Test`
- `test_*`: Test methods must start with `test_`

### Standardized Markers

All unit tests use consistent pytest markers for organization and selective execution:

#### Required Base Markers
```python
pytestmark = [pytest.mark.unit, pytest.mark.fast]
```

#### Feature-Specific Markers
Add appropriate feature markers based on the functionality being tested:
- `pytest.mark.labels` - Label management functionality
- `pytest.mark.issues` - Issue management functionality
- `pytest.mark.comments` - Comment management functionality
- `pytest.mark.sub_issues` - Sub-issues workflow functionality
- `pytest.mark.pull_requests` - Pull request workflow functionality

## Writing Tests

### ⭐ **RECOMMENDED TEST PATTERN** - Modern Infrastructure Pattern

The GitHub Data project has evolved to use a **modern test infrastructure pattern** that combines ConfigBuilder, MockBoundaryFactory, and Protocol Validation for maximum resilience and maintainability.

#### Standard Modern Test Pattern

```python
"""
Modern test pattern combining ConfigBuilder + MockBoundaryFactory + Validation.
This pattern provides 100% schema resilience and protocol completeness.
"""

import pytest
from tests.shared.builders.config_builder import ConfigBuilder
from tests.shared.mocks.boundary_factory import MockBoundaryFactory
from tests.shared.mocks.protocol_validation import assert_boundary_mock_complete

@pytest.mark.integration
def test_example_operation(tmp_path, sample_github_data):
    """Test with complete infrastructure pattern."""
    
    # ✅ Step 1: Configuration with fluent API (schema-resilient)
    config = (
        ConfigBuilder()
        .with_operation("save")
        .with_data_path(str(tmp_path))
        .with_pr_features()
        .build()
    )
    
    # ✅ Step 2: Protocol-complete mock with validation
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    assert_boundary_mock_complete(mock_boundary)
    
    # ✅ Step 3: Test logic with confidence in infrastructure
    result = perform_operation(config, mock_boundary)
    assert result.success
```

#### Benefits of Modern Pattern

1. **Schema Change Resilience**: ConfigBuilder handles new ApplicationConfig fields automatically
2. **Protocol Completeness**: MockBoundaryFactory ensures 100% protocol coverage
3. **Automatic Validation**: Protocol validation catches implementation gaps immediately
4. **Future-Proof**: Automatically adapts to protocol and schema changes
5. **Developer Experience**: Fluent APIs reduce boilerplate and improve readability

#### Pattern Variations

**For Unit Tests:**
```python
@pytest.mark.unit
@pytest.mark.fast
def test_unit_operation(sample_github_data):
    """Unit test with minimal configuration."""
    config = ConfigBuilder().with_minimal_features().build()
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    assert_boundary_mock_complete(mock_boundary)
    # Test logic...
```

**For Restore Operations:**
```python
@pytest.mark.integration
@pytest.mark.restore_workflow
def test_restore_operation(tmp_path):
    """Restore test with specialized mock."""
    config = (
        ConfigBuilder()
        .with_operation("restore")
        .with_data_path(str(tmp_path))
        .with_all_features()
        .build()
    )
    mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
    assert_boundary_mock_complete(mock_boundary)
    # Test logic...
```

**For Error Testing:**
```python
@pytest.mark.integration
@pytest.mark.error_simulation
def test_error_handling(sample_github_data):
    """Error test with hybrid factory pattern."""
    config = ConfigBuilder().with_pr_features().build()
    
    # Start with protocol-complete foundation
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    assert_boundary_mock_complete(mock_boundary)
    
    # Add specific error simulation
    mock_boundary.create_label.side_effect = [
        {"id": 100, "name": "success"},
        Exception("API rate limit exceeded"),
    ]
    # Test error handling logic...
```

### ⚠️ **AVOID** - Legacy Patterns

These patterns should be avoided in new tests as they lack resilience to schema changes:

```python
# ❌ DON'T: Manual ApplicationConfig constructors (brittle)
config = ApplicationConfig(
    operation="save",
    github_token="test_token",
    # Missing fields will break when schema changes
)

# ❌ DON'T: Manual Mock() creation (protocol incomplete)
mock_boundary = Mock()
mock_boundary.get_repository_labels.return_value = []
# Missing 20+ other required protocol methods!

# ❌ DON'T: No validation (catches errors too late)
# Missing: assert_boundary_mock_complete(mock_boundary)
```

### Migration Guidelines

**When writing new tests:**
- ALWAYS use `ConfigBuilder` for configuration
- ALWAYS use `MockBoundaryFactory.create_auto_configured()` for boundary mocks
- ALWAYS validate protocol completeness with `assert_boundary_mock_complete()`
- LEVERAGE existing sample data fixtures rather than creating custom data

**When modifying existing tests:**
- MIGRATE manual ApplicationConfig constructors to ConfigBuilder when touching the test
- REPLACE manual Mock() boundary creation with MockBoundaryFactory patterns
- ADD protocol validation to catch implementation gaps

### Basic Test Structure

```python
"""
Tests for [component name].

Brief description of what this test module covers.
"""

import pytest
from unittest.mock import Mock, patch
from tests.shared import TestDataHelper, AssertionHelper
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

# Add appropriate markers
pytestmark = [
    pytest.mark.unit, 
    pytest.mark.fast,
    pytest.mark.labels,  # Example feature marker
]

class TestComponentName:
    """Test cases for ComponentName."""
    
    def test_specific_behavior(self):
        """Test that specific behavior works correctly."""
        # Arrange
        test_data = TestDataHelper.create_test_label()
        
        # Act
        result = function_under_test(test_data)
        
        # Assert
        AssertionHelper.assert_valid_label(result)
        assert result.name == "test-label"
```

### Integration Test Structure

```python
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

pytestmark = [pytest.mark.integration]

class TestIntegrationScenario:
    """Integration tests for specific scenario."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data."""
        with TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_end_to_end_workflow(self, temp_data_dir, sample_github_data):
        """Test complete workflow from start to finish."""
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
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

## Shared Fixture System

The project includes a comprehensive shared fixture system in `tests/shared/` that provides enhanced testing capabilities and follows established patterns for different test scenarios.

### Core Infrastructure Fixtures

```python
from tests.shared import (
    temp_data_dir,               # Basic temp directory
    sample_github_data,          # Comprehensive sample data
    github_service_mock,         # Basic GitHub service mock
    storage_service_mock,        # Storage service mock
    github_service_with_mock,    # Service with mocked boundary
)
```

### Enhanced Mock Fixtures

```python
from tests.shared import (
    mock_boundary_class,         # Mock GitHubApiBoundary class for patching
    mock_boundary,              # Configured mock boundary instance
    boundary_with_repository_data, # Enhanced boundary mock
)
```

### Using Shared Test Utilities

The project provides comprehensive test utilities in `tests.shared.helpers`:

#### TestDataHelper
Create standardized test entities:
```python
from tests.shared import TestDataHelper

# Create test entities with defaults
user = TestDataHelper.create_test_user()
issue = TestDataHelper.create_test_issue()
comment = TestDataHelper.create_test_comment()
label = TestDataHelper.create_test_label()

# Customize with parameters
user = TestDataHelper.create_test_user(login="alice", user_id=123)
issue = TestDataHelper.create_test_issue(
    title="Custom Issue",
    state="closed",
    user=user
)
```

#### MockHelper
Create standardized mock objects:
```python
from tests.shared import MockHelper

# Create mock services with common methods pre-configured
mock_github = MockHelper.create_github_client_mock()
mock_storage = MockHelper.create_storage_service_mock()

# Use in tests
def test_with_mocks():
    github_mock = MockHelper.create_github_client_mock()
    github_mock.create_label.return_value = {"name": "created-label"}
    
    # Test code using mock
    result = service_function(github_mock)
    github_mock.create_label.assert_called_once()
```

#### AssertionHelper
Validate test entities:
```python
from tests.shared import AssertionHelper

def test_entity_validation():
    user = create_user_somehow()
    issue = create_issue_somehow()
    
    # Validate entities are well-formed
    AssertionHelper.assert_valid_github_user(user)
    AssertionHelper.assert_valid_issue(issue)
    
    # Validate mock interactions
    AssertionHelper.assert_mock_called_with_repo(
        mock_method, "owner/repo"
    )
```

### Data Builder Patterns

**Dynamic Data Generation:**
- `github_data_builder`: Build custom GitHub data for specific test scenarios
- `parametrized_data_factory`: Create predefined data scenarios

```python
from tests.shared import (
    github_data_builder,
    parametrized_data_factory,
)

def test_with_enhanced_fixtures(github_data_builder):
    """Test using enhanced fixture patterns."""
    # Build custom test data
    test_data = (github_data_builder
                .with_labels(3)
                .with_issues(5)
                .with_comments()
                .build())
    
    # Test with realistic data
    process_github_data(test_data)
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

#### Pattern 3: Data Builder Test
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.issues
@pytest.mark.enhanced_fixtures
def test_issue_processing(github_data_builder):
    """Test issue processing with builder data."""
    test_data = github_data_builder.with_issues(3, state="mixed").build()
    
    processor = IssueProcessor()
    results = processor.process_issues(test_data["issues"])
    
    assert len(results) == 3
    for result in results:
        AssertionHelper.assert_valid_issue(result)
```

## Boundary Mock Standardization

The GitHub Data project uses an advanced **boundary mock factory system** that provides 100% protocol completeness with automatic validation. This system eliminates manual mock configuration and prevents protocol extension failures.

### MockBoundaryFactory - Enhanced Mock Creation

**Location:** `tests/shared/mocks/boundary_factory.py`

The MockBoundaryFactory provides automated, protocol-complete boundary mocks with intelligent configuration:

#### Core Factory Methods

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

#### Before/After Comparison

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

### MockBoundaryFactory Methods and Usage Patterns

#### Core Factory Methods

##### `create_auto_configured(sample_data=None, validate_completeness=True)`

**Purpose:** Creates a fully automated mock boundary with 100% protocol coverage.

**Recommended Use:** ⭐ **PRIMARY METHOD** - Use for most test scenarios.

```python
# ✅ Basic usage with sample data
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

# ✅ Empty repository scenario
mock_boundary = MockBoundaryFactory.create_auto_configured({})

# ✅ Custom data scenario
custom_data = {"labels": [{"name": "bug", "color": "red"}]}
mock_boundary = MockBoundaryFactory.create_auto_configured(custom_data)
```

**Features:**
- **Automatic Protocol Discovery:** Finds all protocol methods automatically
- **Intelligent Configuration:** Configures methods based on naming patterns
- **Data Integration:** Maps sample data to appropriate methods
- **Validation:** Optional protocol completeness validation
- **Future-Proof:** Automatically includes new protocol methods

##### `create_protocol_complete(sample_data=None)`

**Purpose:** Creates protocol-complete mock with mandatory validation.

```python
# ✅ Protocol-complete with validation guarantee
mock_boundary = MockBoundaryFactory.create_protocol_complete(sample_github_data)
```

##### `create_for_restore(success_responses=True)`

**Purpose:** Creates mock boundary optimized for restore operation testing.

```python
# ✅ Restore workflow with success responses
mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)

# ✅ Restore workflow with basic responses
mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=False)
```

#### Usage Patterns by Test Type

##### Pattern 1: Basic Integration Test

```python
@pytest.mark.integration
def test_basic_save_workflow(sample_github_data, temp_data_dir):
    """Test basic save workflow with factory mock."""
    
    # ✅ Use auto-configured factory
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # Test logic uses complete protocol mock automatically
    # All GitHub API methods properly configured
    # Realistic data responses from sample_github_data
```

##### Pattern 2: Error Simulation Test

```python
@pytest.mark.error_simulation
def test_api_error_handling(sample_github_data):
    """Test API error handling with hybrid factory pattern."""
    
    # ✅ Step 1: Start with protocol-complete foundation
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # ✅ Step 2: Add specific error simulation
    mock_boundary.create_label.side_effect = [
        {"id": 100, "name": "success"},           # First call succeeds
        Exception("API rate limit exceeded"),     # Second call fails
        {"id": 101, "name": "recovery"}          # Third call succeeds
    ]
    
    # ✅ Step 3: All other methods remain functional
    assert mock_boundary.get_repository_labels() == sample_github_data["labels"]
    
    # Test error handling logic...
```

##### Pattern 3: Restore Workflow Test

```python
@pytest.mark.restore_workflow
def test_restore_workflow_success(temp_data_dir):
    """Test restore workflow with realistic API responses."""
    
    # ✅ Use restore-specific factory
    mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
    
    # ✅ Override specific creation responses if needed
    mock_boundary.create_issue.side_effect = [
        {"number": 101, "id": 999, "title": "Restored Issue 1"},
        {"number": 102, "id": 998, "title": "Restored Issue 2"}
    ]
    
    # Test restore logic with realistic API responses
```

##### Pattern 4: Custom Data Integration

```python
def test_custom_data_scenario():
    """Test with custom data while maintaining protocol completeness."""
    
    # ✅ Create custom data that extends sample data
    custom_data = {
        "labels": [
            {"name": "critical", "color": "ff0000", "description": "Critical issues"},
            {"name": "feature", "color": "00ff00", "description": "New features"}
        ],
        "issues": [
            {"number": 1, "title": "Custom Issue", "labels": ["critical"]}
        ],
        "comments": [],
        "pull_requests": []
    }
    
    # ✅ Use factory with custom data
    mock_boundary = MockBoundaryFactory.create_auto_configured(custom_data)
    
    # ✅ Verify custom data integration
    assert mock_boundary.get_repository_labels() == custom_data["labels"]
    assert len(mock_boundary.get_repository_issues()) == 1
    
    # Test custom scenario logic...
```

### Best Practices for Boundary Mocks

#### ✅ DO - Recommended Patterns

1. **Use `create_auto_configured()` as primary method**
2. **Preserve custom behavior with `side_effect` after factory creation**
3. **Validate protocol completeness during development**
4. **Use sample data fixtures for consistent testing**
5. **Apply hybrid pattern for error testing**
6. **Choose appropriate factory method for test scenario**

```python
class TestExample:
    """Example test class using best practices."""

    def test_save_workflow(self, sample_github_data):
        """Test with auto-configured boundary mock."""
        # ✅ Use factory with sample data
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

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

#### ❌ DON'T - Anti-patterns to Avoid

1. **Manual `Mock()` creation for boundary objects**
2. **Multiple factory configurations per test**
3. **Manual protocol method configuration**
4. **Ignoring protocol completeness validation**
5. **Hardcoded return values without sample data**
6. **Creating incomplete mocks**

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

#### Method Selection Guide
- **Standard Testing:** `create_auto_configured(sample_github_data)`
- **Empty Repository:** `create_auto_configured({})`
- **Restore Testing:** `create_for_restore(success_responses=True)`
- **Protocol Validation:** `create_protocol_complete(sample_github_data)`
- **Legacy Support:** `create_with_data("full", sample_data=sample_github_data)`

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

## Test Configuration

### pytest.ini Configuration

Test configuration is centralized in the `pytest.ini` file, which includes:

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

## Development Workflow

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

4. **Modern Infrastructure Standards** ⭐ **REQUIRED FOR NEW TESTS**
   - **ALWAYS use ConfigBuilder** for ApplicationConfig creation - prevents schema change brittleness
   - **ALWAYS use MockBoundaryFactory.create_auto_configured()** - ensures 100% protocol completeness
   - **ALWAYS validate protocol completeness** with `assert_boundary_mock_complete()` - catches implementation gaps immediately
   - **LEVERAGE existing sample data fixtures** for consistent, realistic test scenarios
   - **FOLLOW the ConfigBuilder + MockBoundaryFactory + Validation pattern** for maximum resilience

5. **Boundary Mock Standards** ⭐ **CRITICAL**
   - **Never use manual Mock() creation** for boundary objects - protocol incomplete and brittle
   - **Always start with factory methods** that guarantee protocol completeness
   - **Use hybrid factory pattern for error testing** - combine protocol completeness with custom error simulation
   - **Validate mock completeness during development** to catch missing protocol methods early

6. **Error Testing Standards** ⭐ **ENHANCED**
   - **Use hybrid factory + custom override pattern** for error simulation
   - **Start with protocol-complete boundary** via `MockBoundaryFactory.create_auto_configured()`
   - **Add custom error behavior** using `side_effect` and `return_value` overrides after factory creation
   - **Test error recovery mechanisms** and graceful degradation
   - **Use error markers** (`@pytest.mark.error_simulation`) for test organization
   - **Cover multiple error scenarios** (timeouts, rate limits, malformed data, connection failures)

7. **Configuration Standards** ⭐ **MANDATORY**
   - **Never use manual ApplicationConfig() constructors** in new tests - breaks with schema changes
   - **Always use ConfigBuilder fluent API** for configuration creation
   - **Leverage preset methods** like `with_pr_features()`, `with_minimal_features()`, `with_all_features()`
   - **Use environment variable mapping** (`as_env_dict()`) for container tests

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

### MockBoundaryFactory Migration Issues

#### Common Error Messages and Solutions

**"Mock boundary missing methods"**
```python
# Solution: Use auto-configured factory
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
```

**"'Mock' object has no attribute 'create_auto_configured'"**
```python
# Solution: Fix import statement
from tests.shared.mocks.boundary_factory import MockBoundaryFactory
```

**"TypeError: 'NoneType' object is not iterable"**
```python
# Solution: Provide proper sample data format
sample_data = {"labels": [], "issues": [], "comments": []}
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
```

### Getting Help

1. **Documentation**: Check this guide and inline code comments
2. **Test Output**: Use verbose flags for detailed test information
3. **Logs**: Check test logs and container logs for errors
4. **Community**: Refer to pytest and Docker documentation
5. **Debugging**: Use Python debugger (`--pdb`) for interactive debugging

## Migration Guide

### MockBoundaryFactory Migration

#### Before/After Pattern
```python
# ❌ BEFORE - Manual mock (avoid)
mock_boundary = Mock()
mock_boundary.get_repository_labels.return_value = []
mock_boundary.get_repository_issues.return_value = sample_data["issues"]
# ... 20+ more manual configurations

# ✅ AFTER - Factory pattern (use)
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
# All protocol methods automatically configured ✅
```

#### Migration Steps
1. **Update Imports:**
   ```python
   # Add this import
   from tests.shared.mocks.boundary_factory import MockBoundaryFactory
   
   # Remove if no longer needed
   from unittest.mock import Mock
   ```

2. **Replace Mock Creation:**
   ```python
   # ❌ Replace this
   mock_boundary = Mock()
   
   # ✅ With this
   mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
   ```

3. **Remove Manual Configurations:**
   ```python
   # ❌ Delete these (factory handles automatically)
   mock_boundary.get_repository_labels.return_value = []
   mock_boundary.get_repository_issues.return_value = []
   mock_boundary.get_all_issue_comments.return_value = []
   # ... all other manual return_value assignments
   ```

4. **Preserve Custom Behavior:**
   ```python
   # ✅ Keep these AFTER factory creation
   mock_boundary.create_issue.side_effect = custom_side_effect
   mock_boundary.some_method.return_value = custom_response
   ```

---

For more information about specific testing scenarios or to contribute to the test suite, see the project's [CONTRIBUTING.md](../CONTRIBUTING.md) guide.