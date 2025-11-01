# Writing Tests

[← Testing Guide](README.md)

## Table of Contents

- [REQUIRED TEST PATTERNS](#required-test-patterns)
- [Prohibited Legacy Patterns](#prohibited-legacy-patterns)
- [Migration Guidelines](#migration-guidelines)
- [Basic Test Structure](#basic-test-structure)
- [Integration Test Structure](#integration-test-structure)
- [Container Test Structure](#container-test-structure)
- [Configuration Patterns - ConfigFactory and ConfigBuilder](#configuration-patterns---configfactory-and-configbuilder)
- [Testing Standards and Requirements](#testing-standards-and-requirements)
- [Pattern Extension Requirements](#pattern-extension-requirements)

## REQUIRED TEST PATTERNS

### ⭐ **REQUIRED TEST PATTERN** - Modern Infrastructure Pattern

The GitHub Data project has evolved to use a **modern test infrastructure pattern** that combines ConfigBuilder, ConfigFactory, MockBoundaryFactory, and Protocol Validation for maximum resilience and maintainability. **This pattern is REQUIRED for all new tests** and should be used when modifying existing tests.

#### Standard Modern Test Pattern

```python
"""
Modern test pattern combining ConfigBuilder/ConfigFactory + MockBoundaryFactory + Validation.
This pattern provides 100% schema resilience and protocol completeness.
"""

import pytest
from tests.shared.builders.config_builder import ConfigBuilder
from tests.shared.builders.config_factory import ConfigFactory
from tests.shared.mocks.boundary_factory import MockBoundaryFactory
from tests.shared.mocks.protocol_validation import assert_boundary_mock_complete

@pytest.mark.integration
def test_example_operation(tmp_path, sample_github_data):
    """Test with complete infrastructure pattern."""

    # ✅ Step 1: Configuration with fluent API (schema-resilient)
    # Option A: Using ConfigBuilder for complex configurations
    config = (
        ConfigBuilder()
        .with_operation("save")
        .with_data_path(str(tmp_path))
        .with_pr_features()
        .build()
    )

    # Option B: Using ConfigFactory for common scenarios
    # config = ConfigFactory.create_save_config(DATA_PATH=str(tmp_path))

    # ✅ Step 2: Protocol-complete mock with validation
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    assert_boundary_mock_complete(mock_boundary)

    # ✅ Step 3: Test logic with confidence in infrastructure
    result = perform_operation(config, mock_boundary)
    assert result.success
```

#### Benefits of Modern Pattern

1. **Schema Change Resilience**: ConfigBuilder/ConfigFactory handle new ApplicationConfig fields automatically
2. **Protocol Completeness**: MockBoundaryFactory ensures 100% protocol coverage
3. **Automatic Validation**: Protocol validation catches implementation gaps immediately
4. **Future-Proof**: Automatically adapts to protocol and schema changes
5. **Developer Experience**: Fluent APIs reduce boilerplate and improve readability
6. **Common Scenario Support**: ConfigFactory provides optimized methods for frequent test patterns
7. **Scenario-Specific Testing**: ConfigFactory includes specialized methods for dependency validation, boolean parsing, and error testing

#### Pattern Variations

**For Unit Tests:**
```python
@pytest.mark.unit
@pytest.mark.fast
def test_unit_operation(sample_github_data):
    """Unit test with minimal configuration."""
    # Option A: ConfigBuilder for custom minimal setup
    config = ConfigBuilder().with_minimal_features().build()

    # Option B: ConfigFactory for standard minimal setup
    # config = ConfigFactory.create_minimal_config()

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
    # Option A: ConfigBuilder for complex restore setup
    config = (
        ConfigBuilder()
        .with_operation("restore")
        .with_data_path(str(tmp_path))
        .with_all_features()
        .build()
    )

    # Option B: ConfigFactory for standard restore setup
    # config = ConfigFactory.create_restore_config(DATA_PATH=str(tmp_path))

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
    # Use ConfigFactory for dependency validation scenarios
    config = ConfigFactory.create_dependency_validation_config(
        feature="pull_request_comments",
        enabled=True,
        dependency_enabled=False
    )

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

**For Boolean Parsing Tests:**
```python
@pytest.mark.unit
@pytest.mark.fast
def test_boolean_parsing():
    """Test boolean field parsing with ConfigFactory."""
    config = ConfigFactory.create_boolean_parsing_config(
        field="INCLUDE_MILESTONES",
        value="yes"  # Test various formats: "yes", "1", "true", "on"
    )
    assert config.include_milestones is True
```

**For Feature-Specific Tests:**
```python
@pytest.mark.integration
@pytest.mark.sub_issues
def test_sub_issues_workflow(tmp_path, sample_github_data):
    """Test sub-issues workflow with specialized config."""
    config = ConfigFactory.create_sub_issues_config(DATA_PATH=str(tmp_path))
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    assert_boundary_mock_complete(mock_boundary)
    # Test sub-issues logic...
```

## Prohibited Legacy Patterns

These patterns are **PROHIBITED** in new tests and should be migrated when modifying existing tests:

```python
# ❌ NEVER: Manual ApplicationConfig constructors (brittle)
config = ApplicationConfig(
    operation="save",
    github_token="test_token",
    # Missing fields will break when schema changes
)

# ❌ NEVER: Manual Mock() creation (protocol incomplete)
mock_boundary = Mock()
mock_boundary.get_repository_labels.return_value = []
# Missing 20+ other required protocol methods!

# ❌ NEVER: No validation (catches errors too late)
# Missing: assert_boundary_mock_complete(mock_boundary)

# ❌ NEVER: Manual environment variable setup
with patch.dict("os.environ", {"OPERATION": "save", "GITHUB_TOKEN": "test"}):
    config = ApplicationConfig.from_environment()
# Use ConfigBuilder or ConfigFactory instead!
```

## Migration Guidelines

**When writing new tests:**
- **ALWAYS** use `ConfigBuilder` or `ConfigFactory` for configuration creation
- **ALWAYS** use `MockBoundaryFactory.create_auto_configured()` for boundary mocks
- **ALWAYS** validate protocol completeness with `assert_boundary_mock_complete()`
- **LEVERAGE** existing sample data fixtures rather than creating custom data
- **CHOOSE** ConfigFactory for common scenarios, ConfigBuilder for complex custom configurations

**When modifying existing tests:**
- **MIGRATE** manual ApplicationConfig constructors to ConfigBuilder/ConfigFactory patterns
- **REPLACE** manual Mock() boundary creation with MockBoundaryFactory patterns
- **ADD** protocol validation to catch implementation gaps
- **PREFER** ConfigFactory methods for standard scenarios (save, restore, PR workflows, etc.)

**ConfigBuilder vs ConfigFactory Selection:**
- **Use ConfigFactory** for:
  - Standard operations (save, restore)
  - Common feature combinations (PR workflows, issues-only, labels-only)
  - Dependency validation testing
  - Boolean parsing tests
  - Error scenario testing
- **Use ConfigBuilder** for:
  - Complex custom configurations
  - Selective feature combinations not covered by ConfigFactory
  - Tests requiring fine-grained control over configuration

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

## Configuration Patterns - ConfigFactory and ConfigBuilder

The GitHub Data project provides two complementary approaches for creating test configurations: **ConfigFactory** for common scenarios and **ConfigBuilder** for complex custom configurations.

### ConfigFactory - Scenario-Based Configuration ⭐ **RECOMMENDED FOR COMMON SCENARIOS**

**Location:** `tests/shared/builders/config_factory.py`

ConfigFactory provides static methods for creating ApplicationConfig instances for common test scenarios with sensible defaults.

#### Basic Configuration Methods

```python
from tests.shared.builders.config_factory import ConfigFactory

# Basic operations
save_config = ConfigFactory.create_save_config()
restore_config = ConfigFactory.create_restore_config()

# Feature-specific configurations
pr_config = ConfigFactory.create_pr_config()
milestone_config = ConfigFactory.create_milestone_config()
minimal_config = ConfigFactory.create_minimal_config()
full_config = ConfigFactory.create_full_config()

# Specialized feature combinations
issues_only_config = ConfigFactory.create_issues_only_config()
labels_only_config = ConfigFactory.create_labels_only_config()
git_only_config = ConfigFactory.create_git_only_config()
comments_disabled_config = ConfigFactory.create_comments_disabled_config()
reviews_only_config = ConfigFactory.create_reviews_only_config()
sub_issues_config = ConfigFactory.create_sub_issues_config()
```

#### Phase 2 Scenario-Specific Methods

```python
# Dependency validation testing
invalid_config = ConfigFactory.create_dependency_validation_config(
    feature="pull_request_comments",
    enabled=True,
    dependency_enabled=False  # Creates invalid dependency state
)

# Boolean parsing testing
config = ConfigFactory.create_boolean_parsing_config(
    field="INCLUDE_MILESTONES",
    value="yes"  # Test various formats: "yes", "1", "true", "on"
)

# Error scenario testing
config = ConfigFactory.create_error_scenario_config(
    invalid_field="OPERATION",
    invalid_value="invalid_op"
)
```

#### Environment Variable Generation

```python
# Generate environment dictionaries for container tests
env_dict = ConfigFactory.create_container_env_dict(
    DATA_PATH="/custom/path",
    INCLUDE_PULL_REQUESTS="true"
)

# Base environment with overrides
env_dict = ConfigFactory.create_base_env_dict(
    OPERATION="restore",
    GITHUB_REPO="custom/repo"
)
```

#### Mock Configuration Generation

```python
# Generate mock configurations for testing
mock_config = ConfigFactory.create_mock_config(
    operation="save",
    repository_owner="custom-owner"
)

# Specialized mock configurations
milestone_mock = ConfigFactory.create_milestone_mock_config()
pr_mock = ConfigFactory.create_pr_mock_config()
```

### ConfigBuilder - Complex Custom Configuration

**Location:** `tests/shared/builders/config_builder.py`

ConfigBuilder provides a fluent API for creating complex custom configurations when ConfigFactory methods don't meet specific needs.

```python
from tests.shared.builders.config_builder import ConfigBuilder

# Complex configuration with fluent API
config = (
    ConfigBuilder()
    .with_operation("save")
    .with_token("custom_token")
    .with_repo("owner/repo")
    .with_data_path(str(tmp_path))
    .with_label_strategy("overwrite")
    .with_git_repo(False)
    .with_issues({1, 3, 5})  # Selective issue numbers
    .with_issue_comments(True)
    .with_pull_requests([101, 102])  # Selective PR numbers
    .with_pr_reviews(True)
    .with_sub_issues(True)
    .build()
)
```

### Configuration Pattern Decision Tree

#### 🔄 **Decision Workflow for Configuration Creation**

```
1. Is this a standard, common scenario?
   ├─ YES → Does ConfigFactory have a method for this?
   │   ├─ YES → ✅ Use ConfigFactory.create_[scenario]_config()
   │   └─ NO → Is it used by 2+ tests?
   │       ├─ YES → ✅ Add to ConfigFactory, then use
   │       └─ NO → Use ConfigBuilder for now
   └─ NO → Does it require selective/complex configuration?
       ├─ YES → ✅ Use ConfigBuilder
       └─ NO → Consider if pattern should be in ConfigFactory
```

#### Use ConfigFactory When:
- **Standard Operations**: save, restore, minimal, full configurations
- **Common Feature Combinations**: PR workflows, issues-only, labels-only, git-only
- **Standard Test Scenarios**: dependency validation, boolean parsing, error scenarios
- **Container Testing**: environment variable generation
- **Mock Configurations**: standard mock setups
- **Business Scenarios**: milestone testing, comments disabled, reviews-only

#### Use ConfigBuilder When:
- **Selective Operations**: specific issue/PR numbers, custom date ranges
- **Complex Logic**: conditional feature enabling, performance constraints
- **Fine-Grained Control**: custom label strategies, advanced filtering
- **Unique Requirements**: non-standard feature combinations
- **Multi-Step Configuration**: configurations requiring multiple interdependent settings
- **Edge Cases**: one-off scenarios that don't fit standard patterns

#### Extension Decision Matrix

| Scenario Type | Reusability | Complexity | Recommended Approach |
|---------------|-------------|------------|---------------------|
| Standard business scenario | High (2+ tests) | Low-Medium | ✅ ConfigFactory |
| Selective operations | Medium | High | ✅ ConfigBuilder |
| Validation patterns | High | Low | ✅ ConfigFactory |
| Edge cases | Low (1 test) | Any | ✅ ConfigBuilder |
| Environment setup | High | Low | ✅ ConfigFactory |
| Custom workflows | Medium | High | ✅ ConfigBuilder |

## Testing Standards and Requirements

### ⭐ **MANDATORY REQUIREMENTS FOR ALL NEW TESTS**

The following standards are **REQUIRED** for all new tests and **SHOULD BE APPLIED** when modifying existing tests:

#### 1. Configuration Creation (MANDATORY)
- **✅ REQUIRED**: Use `ConfigFactory` or `ConfigBuilder` for ALL configuration creation
- **❌ PROHIBITED**: Manual `ApplicationConfig()` constructors
- **❌ PROHIBITED**: Manual `os.environ` patches for configuration setup
- **PREFERENCE**: Use `ConfigFactory` for standard scenarios, `ConfigBuilder` for complex custom needs

#### 2. Boundary Mock Creation (MANDATORY)
- **✅ REQUIRED**: Use `MockBoundaryFactory.create_auto_configured()` for ALL boundary mocks
- **✅ REQUIRED**: Validate protocol completeness with `assert_boundary_mock_complete()`
- **❌ PROHIBITED**: Manual `Mock()` creation for boundary objects
- **❌ PROHIBITED**: Incomplete protocol implementations

#### 3. Sample Data Usage (REQUIRED)
- **✅ REQUIRED**: Use existing `sample_github_data` fixtures when possible
- **✅ REQUIRED**: Leverage shared test infrastructure in `tests/shared/`
- **PREFERENCE**: Extend existing fixtures rather than creating custom data

#### 4. Pattern Extension Requirements (MANDATORY FOR COMMON SCENARIOS)
- **✅ REQUIRED**: When creating tests for common scenarios (save, restore, feature workflows), add ConfigFactory methods
- **✅ REQUIRED**: When adding new test patterns used by multiple tests, centralize in shared infrastructure
- **✅ REQUIRED**: Follow established naming conventions for consistency

#### 5. Test Organization Requirements (MANDATORY)
- **✅ REQUIRED**: Use appropriate pytest markers for all tests
- **✅ REQUIRED**: Follow standard test structure patterns documented here
- **✅ REQUIRED**: Include proper docstrings describing test scenarios

## Pattern Extension Requirements

When implementing new test scenarios that could benefit other tests:

### Adding ConfigFactory Methods ⭐ **PREFERRED FOR COMMON SCENARIOS**

**When to Add ConfigFactory Methods:**
- Pattern is used by 2+ tests across different test files
- Configuration represents a common business scenario (e.g., "milestone testing", "comments disabled")
- Configuration involves standard environment variable combinations
- Pattern includes dependency validation, boolean parsing, or error scenarios

**How to Add ConfigFactory Methods:**
1. **ADD** the pattern as a new static method in `ConfigFactory`
2. **FOLLOW** naming conventions:
   - `create_[scenario]_config()` for feature scenarios
   - `create_[validation_type]_config()` for validation scenarios
   - `create_[feature]_only_config()` for isolated feature testing
3. **IMPLEMENT** using existing base methods for consistency:
   ```python
   @staticmethod
   def create_new_scenario_config(**overrides) -> ApplicationConfig:
       """Create configuration for new scenario testing."""
       env_dict = ConfigFactory.create_base_env_dict(
           INCLUDE_FEATURE_X="true",
           INCLUDE_FEATURE_Y="false",
           **overrides,
       )

       with patch.dict("os.environ", env_dict, clear=True):
           return ApplicationConfig.from_environment()
   ```
4. **DOCUMENT** in ConfigFactory class docstring with usage examples
5. **TEST** with comprehensive unit tests in `tests/unit/builders/test_config_factory.py`

**ConfigFactory Extension Examples:**
```python
# ✅ Good ConfigFactory extensions
create_security_testing_config()     # Common security test scenario
create_performance_testing_config()  # Performance test configuration
create_minimal_api_config()         # Minimal API-only configuration
create_dependency_error_config()    # Dependency validation errors

# ❌ Avoid ConfigFactory for these
create_issue_123_specific_config()  # Too specific, use ConfigBuilder
create_custom_edge_case_config()    # Unique edge case, use ConfigBuilder
```

### Adding ConfigBuilder Methods ⭐ **FOR COMPLEX EXTENSION PATTERNS**

**When to Add ConfigBuilder Methods:**
- Pattern involves complex conditional logic or selective operations
- Configuration requires fine-grained control over multiple interdependent features
- Pattern is reused across tests but with significant variations
- Method enhances ConfigBuilder's fluent API capabilities

**How to Add ConfigBuilder Methods:**
1. **ADD** fluent API methods that return `self` for chaining
2. **FOLLOW** naming conventions:
   - `with_[feature]_[configuration]()` for feature methods
   - `with_selective_[operation]()` for selective operations
   - `with_[validation]_scenario()` for validation scenarios
3. **IMPLEMENT** with proper validation and defaults:
   ```python
   def with_custom_pr_workflow(self, pr_numbers: Set[int] = None, include_reviews: bool = True) -> 'ConfigBuilder':
       """Configure for custom PR workflow testing."""
       self._include_pull_requests = pr_numbers or set()
       self._include_pr_reviews = include_reviews
       if include_reviews:
           self._include_pr_review_comments = True
       return self
   ```
4. **MAINTAIN** consistency with existing ConfigBuilder patterns
5. **TEST** integration with other ConfigBuilder methods

**ConfigBuilder Extension Examples:**
```python
# ✅ Good ConfigBuilder extensions
with_selective_issues()             # Selective issue number sets
with_performance_constraints()      # Performance testing constraints
with_custom_label_strategy()       # Complex label conflict strategies
with_conditional_features()        # Complex conditional feature logic

# ❌ Avoid ConfigBuilder for these
with_standard_save_operation()     # Too simple, use ConfigFactory
with_basic_pr_workflow()          # Standard scenario, use ConfigFactory
```

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

### 📋 **Practical Extension Examples**

#### Example 1: Adding a ConfigFactory Method

**Scenario**: Multiple tests need to test rate limiting behavior

```python
# Step 1: Identify the pattern (used in 3+ test files)
# tests/test_rate_limiting.py
# tests/integration/test_api_resilience.py
# tests/unit/test_github_client.py

# Step 2: Add to ConfigFactory
@staticmethod
def create_rate_limiting_config(**overrides) -> ApplicationConfig:
    """Create configuration for rate limiting testing scenarios."""
    env_dict = ConfigFactory.create_base_env_dict(
        INCLUDE_PULL_REQUESTS="true",
        INCLUDE_PR_REVIEWS="true",
        INCLUDE_PR_REVIEW_COMMENTS="true",
        # Enable features that trigger rate limits
        **overrides,
    )

    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()

# Step 3: Document in ConfigFactory class docstring
# Step 4: Add comprehensive tests
```

#### Example 2: Adding a ConfigBuilder Method

**Scenario**: Tests need selective PR processing with custom review requirements

```python
# Step 1: Identify complex pattern needing flexibility
# Multiple tests need different PR number sets with varying review requirements

# Step 2: Add to ConfigBuilder
def with_selective_pr_workflow(
    self,
    pr_numbers: Set[int],
    require_reviews: bool = True,
    include_review_comments: bool = None
) -> 'ConfigBuilder':
    """Configure selective PR workflow with custom review requirements."""
    self._include_pull_requests = pr_numbers
    self._include_pr_reviews = require_reviews

    # Conditional logic based on review requirements
    if include_review_comments is None:
        include_review_comments = require_reviews
    self._include_pr_review_comments = include_review_comments

    return self

# Step 3: Use in tests
config = (
    ConfigBuilder()
    .with_operation("save")
    .with_selective_pr_workflow(
        pr_numbers={101, 103, 105},
        require_reviews=True,
        include_review_comments=False
    )
    .build()
)
```

#### Example 3: Extending vs Using Existing Patterns

```python
# ❌ DON'T: Create new method for simple variations
def create_save_with_custom_path_config(custom_path: str):
    # This is just ConfigFactory.create_save_config() with DATA_PATH override
    pass

# ✅ DO: Use existing method with overrides
config = ConfigFactory.create_save_config(DATA_PATH=custom_path)

# ❌ DON'T: Create ConfigBuilder method for standard scenarios
def with_standard_milestone_testing(self):
    # This is already covered by ConfigFactory.create_milestone_config()
    pass

# ✅ DO: Use ConfigFactory for standard patterns
config = ConfigFactory.create_milestone_config()

# ✅ DO: Create ConfigBuilder method for complex selective scenarios
def with_selective_milestone_workflow(self, milestone_ids: Set[int], include_closed: bool = False):
    # Complex logic for selective milestone processing
    pass
```

#### Example 4: Pattern Migration Decision

```python
# Scenario: You have a pattern in 2 different test files

# File 1: tests/test_backup.py
config = ConfigFactory.create_base_env_dict(
    INCLUDE_GIT_REPO="true",
    INCLUDE_ISSUES="false",
    INCLUDE_PULL_REQUESTS="false",
    # All other features disabled
)

# File 2: tests/test_repository_cloning.py
config = ConfigFactory.create_base_env_dict(
    INCLUDE_GIT_REPO="true",
    INCLUDE_ISSUES="false",
    INCLUDE_PULL_REQUESTS="false",
    # Same pattern repeated
)

# ✅ SOLUTION: Extract to ConfigFactory
@staticmethod
def create_git_repository_only_config(**overrides) -> ApplicationConfig:
    """Create configuration for git repository testing only (no issues/PRs)."""
    return ConfigFactory.create_git_only_config(**overrides)  # Reuse existing!

# Update both test files:
config = ConfigFactory.create_git_only_config()  # Already exists!
```

### Compliance Enforcement

#### Code Review Requirements
- **All new tests** must use the modern infrastructure pattern
- **Configuration creation** must use ConfigBuilder/ConfigFactory
- **Boundary mocks** must use MockBoundaryFactory with validation
- **Legacy patterns** in modified tests should be migrated

#### Migration Guidelines for Legacy Tests
When modifying existing tests that use legacy patterns:
1. **MIGRATE** manual ApplicationConfig constructors to ConfigFactory/ConfigBuilder
2. **REPLACE** manual Mock() boundary creation with MockBoundaryFactory
3. **ADD** protocol validation where missing
4. **DOCUMENT** migration reasoning in commit messages

---

[← Testing Guide](README.md) | [Test Infrastructure →](test-infrastructure.md)
