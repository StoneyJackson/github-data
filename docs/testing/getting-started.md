# Getting Started with Testing

[← Testing Guide](README.md)

This guide provides quick reference for daily testing commands and your first test tutorial.

## Essential Commands

### Development Cycle Commands (Recommended)

```bash
# Fast development cycle
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

## Test Categories Overview

### Unit Tests (`@pytest.mark.unit`)

**Purpose**: Test individual functions and classes in isolation.

**Characteristics**:
- Fast execution (< 1 second each)
- No external dependencies
- Use mocks for external services
- High code coverage focus

### Integration Tests (`@pytest.mark.integration`)

**Purpose**: Test component interactions and end-to-end workflows.

**Characteristics**:
- Moderate execution time (1-10 seconds each)
- Test real component integration
- May use file system and temporary directories
- Mock external APIs

### Container Tests (`@pytest.mark.container`)

**Purpose**: Test Docker container functionality and workflows.

**Characteristics**:
- Slow execution (30+ seconds each)
- Require Docker to be running
- Test full containerized workflows
- May create/destroy Docker resources

For comprehensive marker documentation, see [Test Infrastructure: Test Categories and Markers](test-infrastructure.md#test-categories-and-markers).

## Your First Test

Here's a simple example of a well-structured unit test:

```python
"""
Tests for label management functionality.

This module tests label creation, validation, and storage operations.
"""

import pytest
from tests.shared import TestDataHelper, AssertionHelper
from tests.shared.builders.config_factory import ConfigFactory
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

# Mark this test file with appropriate markers
pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.labels,
]

class TestLabelManagement:
    """Test cases for label management operations."""

    def test_label_creation_succeeds(self, sample_github_data):
        """Test that label creation works correctly with valid data."""
        # Arrange - Set up test data and configuration
        config = ConfigFactory.create_labels_only_config()
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

        # Act - Perform the operation
        result = create_label(config, mock_boundary, "bug", "d73a4a")

        # Assert - Verify the outcome
        AssertionHelper.assert_valid_label(result)
        assert result["name"] == "bug"
        assert result["color"] == "d73a4a"
```

**Key elements:**
1. **Docstrings**: Module and test method documentation
2. **Markers**: `pytestmark` for test categorization
3. **AAA Pattern**: Arrange, Act, Assert structure
4. **Modern Infrastructure**: ConfigFactory + MockBoundaryFactory
5. **Clear naming**: Test name describes expected behavior

For complete pattern documentation, see [Writing Tests](writing-tests.md).

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

## Next Steps

- **Ready to write tests?** → Continue to [Writing Tests](writing-tests.md)
- **Need to understand test infrastructure?** → See [Test Infrastructure](test-infrastructure.md)
- **Working on advanced scenarios?** → See [Specialized Testing](specialized-testing.md)
- **Tests failing?** → See [Reference: Debugging](reference/debugging.md)

---

[← Testing Guide](README.md) | [Writing Tests →](writing-tests.md)
