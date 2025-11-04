# Writing Tests

[← Testing Guide](README.md)

## Table of Contents

- [Configuration Patterns - EntityRegistry](#configuration-patterns---entityregistry)
- [Basic Test Structure](#basic-test-structure)
- [Integration Test Structure](#integration-test-structure)
- [Container Test Structure](#container-test-structure)
- [Testing Standards and Requirements](#testing-standards-and-requirements)

## Configuration Patterns - EntityRegistry

### Overview

Tests use `EntityRegistry.from_environment()` to create service configurations from environment variables. This is the standard approach for all test configuration.

### Basic Pattern

```python
import pytest
from github_data.core.registry import EntityRegistry

def test_with_entity_registry(temp_data_dir, monkeypatch):
    """Example test using EntityRegistry configuration."""
    # Set up environment variables
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")
    monkeypatch.setenv("GITHUB_REPO", "owner/repo")
    monkeypatch.setenv("DATA_PATH", str(temp_data_dir))
    monkeypatch.setenv("OPERATION", "save")

    # Create registry from environment
    registry = EntityRegistry.from_environment()

    # Access services
    github_service = registry.github_service
    storage_service = registry.storage_service

    # Perform test operations
    result = github_service.get_repository_info()
    assert result is not None
```

### Environment Variable Setup

Common environment variables for tests:

| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `GITHUB_TOKEN` | GitHub API authentication | `"test_token_123"` |
| `GITHUB_REPO` | Target repository | `"owner/repo"` |
| `DATA_PATH` | Data storage path | `str(temp_data_dir)` |
| `OPERATION` | Operation type | `"save"` or `"restore"` |
| `INCLUDE_ISSUES` | Include issues | `"true"` or `"false"` |
| `INCLUDE_PULL_REQUESTS` | Include PRs | `"true"` or `"false"` |

### Using monkeypatch for Environment Variables

Always use pytest's `monkeypatch` fixture for setting environment variables in tests:

```python
def test_with_custom_config(temp_data_dir, monkeypatch):
    """Test with custom configuration."""
    monkeypatch.setenv("GITHUB_TOKEN", "custom_token")
    monkeypatch.setenv("GITHUB_REPO", "custom/repo")
    monkeypatch.setenv("DATA_PATH", str(temp_data_dir))
    monkeypatch.setenv("INCLUDE_ISSUES", "true")
    monkeypatch.setenv("INCLUDE_PULL_REQUESTS", "false")

    registry = EntityRegistry.from_environment()

    # Test with custom configuration
    assert registry.config.include_issues is True
    assert registry.config.include_pull_requests is False
```

### When to Use EntityRegistry

**Use EntityRegistry when:**
- Testing components that need full service integration
- Testing end-to-end workflows
- Testing configuration parsing and validation
- Integration tests requiring multiple services

**Use mocks when:**
- Unit testing individual components
- Testing error handling
- Testing API interaction patterns
- Fast feedback tests that don't need real service configuration

### Example: Integration Test with EntityRegistry

```python
@pytest.mark.integration
@pytest.mark.labels
def test_label_save_workflow(temp_data_dir, monkeypatch):
    """Test complete label save workflow with EntityRegistry."""
    # Setup environment
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")
    monkeypatch.setenv("GITHUB_REPO", "test/repo")
    monkeypatch.setenv("DATA_PATH", str(temp_data_dir))
    monkeypatch.setenv("OPERATION", "save")

    # Create registry
    registry = EntityRegistry.from_environment()

    # Execute workflow
    label_saver = registry.create_label_saver()
    result = label_saver.save_labels()

    # Verify results
    assert result.success is True
    assert (temp_data_dir / "labels.json").exists()
```

## Basic Test Structure

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

### Testing with Entity Discovery

When writing tests that validate entity-related behavior (factories, registries, workflows), use entity discovery fixtures instead of hardcoding entity names or counts.

**Pattern: Registry and Factory Tests**

```python
import pytest
from tests.shared import all_entity_names
from github_data.entities.registry import EntityRegistry
from github_data.operations.strategy_factory import StrategyFactory

@pytest.mark.unit
@pytest.mark.fast
def test_factory_completeness(all_entity_names):
    """Test factory creates strategies for all entities."""
    factory = StrategyFactory(registry=EntityRegistry())
    strategies = factory.create_strategies()

    strategy_names = [s.get_entity_name() for s in strategies]
    assert set(strategy_names) == set(all_entity_names)
```

**Pattern: Dependency Validation**

```python
@pytest.mark.integration
def test_dependency_order(enabled_entity_names):
    """Test enabled entities respect dependencies."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()

    # Verify count matches discovery
    assert len(enabled) == len(enabled_entity_names)

    # Verify specific dependency contracts
    # (These are explicit requirements that shouldn't change)
    for entity in enabled:
        for dep in entity.get_dependencies():
            dep_entity = registry.get_entity(dep)
            assert dep_entity.is_enabled()
```

**Pattern: Conditional Entity Handling**

```python
@pytest.mark.integration
def test_conditional_entity(all_entity_names):
    """Test entity included only when condition met."""
    registry = EntityRegistry()

    # Test without condition
    factory = StrategyFactory(registry)
    strategies_without = factory.create_strategies()
    names_without = [s.get_entity_name() for s in strategies_without]

    # Test with condition
    strategies_with = factory.create_strategies(git_service=Mock())
    names_with = [s.get_entity_name() for s in strategies_with]

    # Verify all entities included when condition met
    assert set(names_with) == set(all_entity_names)
```

**When NOT to Use Entity Discovery:**

Entity discovery fixtures are for testing **system-wide entity behavior**. Don't use them when:

- Testing a specific entity (just test that entity directly)
- Entity names are part of the test's explicit contract
- Testing exact dependency relationships (hardcode those - they're requirements)

**Example of Appropriate Hardcoding:**

```python
def test_issues_depend_on_milestones():
    """Test explicit dependency contract."""
    registry = EntityRegistry()
    issues_entity = registry.get_entity("issues")

    # This is a requirement, not a discovery - hardcode it
    assert "milestones" in issues_entity.get_dependencies()
```

## Integration Test Structure

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

## Container Test Structure

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

## Testing Standards and Requirements

### **MANDATORY REQUIREMENTS FOR ALL NEW TESTS**

The following standards are **REQUIRED** for all new tests and **SHOULD BE APPLIED** when modifying existing tests:

#### 1. Boundary Mock Creation (MANDATORY)
- **✅ REQUIRED**: Use `MockBoundaryFactory.create_auto_configured()` for ALL boundary mocks
- **✅ REQUIRED**: Validate protocol completeness with `assert_boundary_mock_complete()`
- **❌ PROHIBITED**: Manual `Mock()` creation for boundary objects
- **❌ PROHIBITED**: Incomplete protocol implementations

#### 2. Sample Data Usage (REQUIRED)
- **✅ REQUIRED**: Use existing `sample_github_data` fixtures when possible
- **✅ REQUIRED**: Leverage shared test infrastructure in `tests/shared/`
- **PREFERENCE**: Extend existing fixtures rather than creating custom data

#### 3. Test Organization Requirements (MANDATORY)
- **✅ REQUIRED**: Use appropriate pytest markers for all tests
- **✅ REQUIRED**: Follow standard test structure patterns documented here
- **✅ REQUIRED**: Include proper docstrings describing test scenarios

### Adding MockBoundaryFactory Patterns
If you create mock patterns for specific scenarios:
1. **EXTEND** MockBoundaryFactory with specialized creation methods
2. **ENSURE** protocol completeness validation
3. **PROVIDE** clear documentation of the pattern's use case

### Adding Shared Fixtures
If you create fixtures that could benefit multiple test scenarios:
1. **ADD** fixtures to `tests/shared/fixtures.py`
2. **EXPORT** through `tests/shared/__init__.py`
3. **DOCUMENT** usage patterns and benefits

---

[← Testing Guide](README.md) | [Test Infrastructure →](test-infrastructure.md)
