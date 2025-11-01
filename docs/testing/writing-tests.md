# Writing Tests

[← Testing Guide](README.md)

## Table of Contents

- [Basic Test Structure](#basic-test-structure)
- [Integration Test Structure](#integration-test-structure)
- [Container Test Structure](#container-test-structure)
- [Testing Standards and Requirements](#testing-standards-and-requirements)

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
