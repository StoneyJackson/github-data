# Test Infrastructure

[← Testing Guide](README.md)

## Overview

This document covers the core testing infrastructure used in the GitHub Data project, including test markers, test organization, configuration patterns, fixtures, and boundary mocks. This infrastructure enables efficient test development and comprehensive test coverage.

## Test Categories and Markers

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
- `@pytest.mark.save_workflow` - Save operation workflows
- `@pytest.mark.restore_workflow` - Restore operation workflows

#### Enhanced Fixture Category Markers
- `@pytest.mark.enhanced_fixtures` - Tests using enhanced fixture patterns
- `@pytest.mark.data_builders` - Tests using dynamic data builder fixtures
- `@pytest.mark.workflow_services` - Tests using workflow service fixtures
- `@pytest.mark.error_simulation` - Error condition simulation tests

## Pytest Marker Reference

The project uses 71 registered pytest markers for sophisticated test organization and selective execution.

### Performance Markers

| Marker | Description | Typical Duration | Usage |
|--------|-------------|-----------------|-------|
| `@pytest.mark.fast` | Fast tests | < 1 second | Unit tests, quick feedback |
| `@pytest.mark.medium` | Medium tests | 1-10 seconds | Integration tests |
| `@pytest.mark.slow` | Slow tests | > 10 seconds | Container tests, end-to-end |
| `@pytest.mark.performance` | Performance tests | Varies | Performance benchmarking |

**Example:**
```python
@pytest.mark.fast
@pytest.mark.unit
def test_quick_operation():
    assert True
```

### Test Type Markers

| Marker | Description | Scope |
|--------|-------------|-------|
| `@pytest.mark.unit` | Unit tests | Single component, isolated |
| `@pytest.mark.integration` | Integration tests | Multiple components |
| `@pytest.mark.container` | Container tests | Full Docker workflow |
| `@pytest.mark.asyncio` | Async tests | Asynchronous operations |

**Example:**
```python
@pytest.mark.integration
@pytest.mark.medium
def test_service_interaction():
    # Test multiple components working together
    pass
```

### Feature Area Markers

#### Core Features

| Marker | Description | Use For |
|--------|-------------|---------|
| `@pytest.mark.labels` | Label management | Label save/restore tests |
| `@pytest.mark.issues` | Issue management | Issue save/restore tests |
| `@pytest.mark.comments` | Comment management | Comment handling tests |
| `@pytest.mark.pull_requests` | Pull requests | PR save/restore tests |

**Example:**
```python
@pytest.mark.integration
@pytest.mark.labels
def test_label_save_restore():
    # Test label workflow
    pass
```

#### Comment Features

| Marker | Description | Use For |
|--------|-------------|---------|
| `@pytest.mark.include_issue_comments` | Issue comments | Tests with issue comment inclusion |
| `@pytest.mark.include_pull_request_comments` | PR comments | Tests with PR comment inclusion |
| `@pytest.mark.pr_comments` | PR comment functionality | PR comment-specific tests |

#### Advanced Features

| Marker | Description | Use For |
|--------|-------------|---------|
| `@pytest.mark.sub_issues` | Sub-issues workflow | Hierarchical issue tests |
| `@pytest.mark.milestones` | Milestone management | Milestone save/restore |
| `@pytest.mark.milestone_relationships` | Milestone relationships | Issue/PR milestone links |
| `@pytest.mark.milestone_integration` | Milestone end-to-end | Complete milestone workflow |
| `@pytest.mark.milestone_config` | Milestone configuration | INCLUDE_MILESTONES config tests |
| `@pytest.mark.git_repositories` | Git repository backup | Git repo save/restore |

### Infrastructure Markers

| Marker | Description | Use For |
|--------|-------------|---------|
| `@pytest.mark.github_api` | GitHub API interaction | API client tests |
| `@pytest.mark.storage` | Data storage | Persistence layer tests |
| `@pytest.mark.save_workflow` | Save workflows | Save operation tests |
| `@pytest.mark.restore_workflow` | Restore workflows | Restore operation tests |
| `@pytest.mark.save_operation` | Save operations | Specific save operations |
| `@pytest.mark.restore_operation` | Restore operations | Specific restore operations |
| `@pytest.mark.error_handling` | Error handling | Error resilience tests |
| `@pytest.mark.strategy_factory` | Strategy factory | Factory pattern tests |
| `@pytest.mark.end_to_end` | End-to-end | Complete feature workflows |

**Example:**
```python
@pytest.mark.integration
@pytest.mark.save_workflow
@pytest.mark.github_api
@pytest.mark.storage
def test_complete_save_workflow():
    # Test full save operation
    pass
```

### Special Scenario Markers

| Marker | Description | Use For |
|--------|-------------|---------|
| `@pytest.mark.empty_repository` | Empty repository | Tests with no data |
| `@pytest.mark.large_dataset` | Large datasets | Performance/scale tests |
| `@pytest.mark.rate_limiting` | Rate limiting | API rate limit tests |
| `@pytest.mark.error_simulation` | Error conditions | Simulated error tests |

**Example:**
```python
@pytest.mark.integration
@pytest.mark.empty_repository
@pytest.mark.fast
def test_save_empty_repo():
    # Test saving repository with no issues
    pass
```

### Enhanced Fixture Category Markers

| Marker | Description | Use For |
|--------|-------------|---------|
| `@pytest.mark.enhanced_fixtures` | Enhanced fixture patterns | Tests using enhanced fixtures |
| `@pytest.mark.data_builders` | Data builder fixtures | Tests using builder patterns |
| `@pytest.mark.workflow_services` | Workflow service fixtures | Tests using workflow services |
| `@pytest.mark.performance_fixtures` | Performance monitoring | Tests with performance tracking |

### Additional Quality Markers

| Marker | Description | Use For |
|--------|-------------|---------|
| `@pytest.mark.memory_intensive` | High memory usage | Memory-heavy tests |
| `@pytest.mark.simple_data` | Simple data structures | Basic data tests |
| `@pytest.mark.complex_hierarchy` | Complex hierarchical data | Nested structure tests |
| `@pytest.mark.temporal_data` | Time-sensitive data | Timestamp/date tests |
| `@pytest.mark.mixed_states` | Mixed state data | Multi-state tests |
| `@pytest.mark.cross_component_interaction` | Multi-component | Cross-component tests |
| `@pytest.mark.data_enrichment` | Data enrichment | Enrichment utility tests |
| `@pytest.mark.edge_cases` | Edge cases | Boundary condition tests |
| `@pytest.mark.issue_comments_validation` | Issue comment validation | Comment validation tests |
| `@pytest.mark.backward_compatibility` | Backward compatibility | Compatibility tests |

### Marker Combination Patterns

**Pattern 1: Unit test with feature area**
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.labels
def test_label_validation():
    pass
```

**Pattern 2: Integration test with workflow**
```python
@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.save_workflow
@pytest.mark.issues
def test_issue_save_workflow():
    pass
```

**Pattern 3: Container test with scenario**
```python
@pytest.mark.container
@pytest.mark.slow
@pytest.mark.large_dataset
@pytest.mark.end_to_end
def test_large_dataset_save():
    pass
```

**Pattern 4: Error handling test**
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.error_handling
@pytest.mark.github_api
def test_api_error_handling():
    pass
```

### Running Tests by Marker

**Single marker:**
```bash
pytest -m fast
pytest -m unit
pytest -m labels
```

**Multiple markers (AND):**
```bash
pytest -m "unit and fast"
pytest -m "integration and labels"
```

**Multiple markers (OR):**
```bash
pytest -m "fast or medium"
pytest -m "labels or issues"
```

**Exclude markers:**
```bash
pytest -m "not slow"
pytest -m "not container"
pytest -m "unit and not slow"
```

**Complex combinations:**
```bash
pytest -m "integration and save_workflow and not slow"
pytest -m "(unit or integration) and not container"
```

### Marker Selection Best Practices

1. **Always include test type**: `unit`, `integration`, or `container`
2. **Always include performance**: `fast`, `medium`, or `slow`
3. **Include feature area**: `labels`, `issues`, `comments`, etc.
4. **Add workflow markers**: `save_workflow`, `restore_workflow`, etc. for integration tests
5. **Add scenario markers**: `empty_repository`, `large_dataset`, etc. when relevant
6. **Add quality markers**: `edge_cases`, `error_handling`, etc. when appropriate

**Good marker usage:**
```python
@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.save_workflow
@pytest.mark.labels
@pytest.mark.storage
def test_label_save_to_storage():
    """Test saving labels to storage."""
    pass
```

**Poor marker usage:**
```python
@pytest.mark.integration  # Only one marker, missing context
def test_label_save():
    pass
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

### Milestone Fixtures

The project provides comprehensive milestone testing fixtures for testing milestone save/restore workflows and relationships with issues and pull requests.

**Source:** `tests/shared/fixtures/milestone_fixtures.py` (22KB comprehensive fixture file)

#### Core Milestone Data Fixtures

**`sample_milestone_data`** - Basic milestone dictionary with standard fields
```python
@pytest.mark.unit
@pytest.mark.milestones
def test_milestone_creation(sample_milestone_data):
    milestone = Milestone(**sample_milestone_data)
    assert milestone.title == "Version 1.0"
    assert milestone.state == "open"
```

**`sample_closed_milestone_data`** - Closed milestone with completion data

**`sample_milestone`** - Milestone entity instance

**`sample_closed_milestone`** - Closed milestone entity instance

**`multiple_milestones`** - Collection of milestones with varied states

#### Milestone Builder Fixtures

**`milestone_builder`** - Dynamic milestone creation
```python
def test_custom_milestone(milestone_builder):
    milestone = milestone_builder(
        title="Sprint 1",
        state="open",
        open_issues=5
    )
    assert milestone.title == "Sprint 1"
```

**`bulk_milestone_builder`** - Create multiple milestones efficiently

#### Milestone Relationship Fixtures

**`issue_with_milestone_data`** - Issue associated with milestone
```python
@pytest.mark.integration
@pytest.mark.milestone_relationships
def test_issue_milestone_link(issue_with_milestone_data):
    issue, milestone = issue_with_milestone_data
    assert issue["milestone_id"] == milestone["id"]
```

**`pr_with_milestone_data`** - Pull request with milestone association

**`multiple_issues_with_milestones`** - Multiple issues linked to milestones

**`multiple_prs_with_milestones`** - Multiple PRs linked to milestones

#### Milestone Strategy Fixtures

**`milestone_save_strategy`** - Configured save strategy

**`milestone_restore_strategy`** - Configured restore strategy

**`milestone_enabled_repository_context`** - Full repository with milestone support

#### Milestone Mock Response Fixtures

**`mock_github_milestone_response`** - GitHub REST API milestone response

**`mock_graphql_milestone_response`** - GitHub GraphQL milestone response

#### Milestone Test Data Fixtures

**`milestone_test_data_directory`** - Temporary directory with milestone JSON files

**`complex_milestone_dataset`** - Complex scenario with multiple milestones, issues, and PRs

**`large_milestone_dataset`** - Large-scale dataset for performance testing

**`milestone_error_scenarios`** - Error condition test data

**`milestone_integration_context`** - Complete end-to-end integration setup

#### Complete Example: Integration Test with Milestone Fixtures

```python
@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.milestones
@pytest.mark.milestone_relationships
@pytest.mark.save_workflow
def test_milestone_with_issues_save(
    temp_data_dir,
    monkeypatch,
    multiple_issues_with_milestones,
    mock_github_service
):
    """Test saving milestones with associated issues."""
    # Setup configuration
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")
    monkeypatch.setenv("GITHUB_REPO", "test/repo")
    monkeypatch.setenv("DATA_PATH", str(temp_data_dir))
    monkeypatch.setenv("OPERATION", "save")
    monkeypatch.setenv("INCLUDE_MILESTONES", "true")

    # Get test data
    issues, milestones = multiple_issues_with_milestones

    # Configure mock
    mock_github_service.get_milestones.return_value = milestones
    mock_github_service.get_issues.return_value = issues

    # Create registry and execute save
    registry = EntityRegistry.from_environment()
    saver = registry.create_milestone_saver()
    result = saver.save_milestones()

    # Verify
    assert result.success is True
    milestone_file = temp_data_dir / "milestones.json"
    assert milestone_file.exists()

    # Verify relationships preserved
    import json
    saved_data = json.loads(milestone_file.read_text())
    assert len(saved_data["milestones"]) == len(milestones)
```

#### Common Marker Combinations for Milestone Tests

```python
# Unit test with milestone data
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.milestones
def test_milestone_validation(sample_milestone_data):
    pass

# Integration test with relationships
@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.milestones
@pytest.mark.milestone_relationships
def test_milestone_issue_links(multiple_issues_with_milestones):
    pass

# End-to-end milestone workflow
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.milestones
@pytest.mark.milestone_integration
@pytest.mark.end_to_end
def test_milestone_complete_workflow(milestone_integration_context):
    pass

# Milestone configuration test
@pytest.mark.integration
@pytest.mark.fast
@pytest.mark.milestone_config
def test_milestone_config_parsing(monkeypatch):
    monkeypatch.setenv("INCLUDE_MILESTONES", "true")
    # Test configuration parsing
    pass
```

For complete fixture definitions and additional fixtures, see `tests/shared/fixtures/milestone_fixtures.py`.

### Migration Utilities

The project provides migration utilities to help transition tests to modern patterns. These are specialized tools for automated test refactoring.

**Source Files:**
- `tests/shared/builders/migration_utilities.py` (13KB)
- `tests/shared/mocks/migration_utils.py` (14KB)

#### Purpose

Migration utilities provide automated assistance for:
- Converting static fixtures to GitHubDataBuilder patterns
- Migrating manual boundary mocks to MockBoundaryFactory
- Detecting and refactoring legacy test patterns

**Important:** These are specialized refactoring tools, not standard test infrastructure. Most developers won't need to use these directly.

#### Fixture Migration: FixtureToBuilderMigrator

**Use when:** Converting static milestone/issue/PR fixtures to dynamic builder patterns

```python
from tests.shared.builders.migration_utilities import FixtureToBuilderMigrator

# Convert static fixture data to builder
fixture_data = {
    "milestones": [...],  # Static milestone data
    "issues": [...]       # Static issue data
}

builder = FixtureToBuilderMigrator.convert_milestone_fixtures(fixture_data)
# Returns GitHubDataBuilder configured with equivalent data
```

**Benefits:**
- Automated conversion of static fixtures
- Maintains data relationships
- Reduces manual refactoring effort

#### Boundary Mock Migration: BoundaryMockMigrator

**Use when:** Detecting and migrating manual `Mock()` boundary patterns

```python
from tests.shared.mocks.migration_utils import BoundaryMockMigrator

# Detect manual mock patterns in test file
with open("tests/test_something.py") as f:
    content = f.read()

patterns = BoundaryMockMigrator.detect_manual_mock_patterns(content)
# Returns list of manual mock patterns found

for pattern in patterns:
    print(f"Line {pattern['line']}: {pattern['type']}")
    print(f"  Variable: {pattern['variable']}")
    print(f"  Suggestion: Use MockBoundaryFactory.create_auto_configured()")
```

**Detects:**
- Manual `Mock()` boundary creation
- Manual `return_value` assignments
- Incomplete protocol implementations

#### When to Use Migration Utilities

**Use migration utilities when:**
- Batch refactoring multiple test files
- Auditing codebase for legacy patterns
- Automated migration scripts

**Do NOT use migration utilities when:**
- Writing new tests (use current patterns directly)
- Updating a single test (manual refactoring is clearer)
- Learning test patterns (learn current patterns, not migrations)

#### Migration Utility Best Practices

1. **Understand before using**: Read the generated code, don't blindly apply
2. **Test after migration**: Run tests to verify conversion correctness
3. **Review changes**: Migration tools are helpers, not guaranteed correct
4. **Incremental migration**: Migrate one file/pattern at a time
5. **Commit frequently**: Commit each successful migration separately

**Example migration workflow:**
```python
# 1. Detect patterns
migrator = BoundaryMockMigrator()
test_file = "tests/test_labels.py"
with open(test_file) as f:
    patterns = migrator.detect_manual_mock_patterns(f.read())

# 2. Review findings
print(f"Found {len(patterns)} manual mock patterns")
for pattern in patterns[:5]:  # Show first 5
    print(f"  {pattern['line']}: {pattern['type']}")

# 3. Manual refactoring with guidance
# Use patterns to guide manual updates to MockBoundaryFactory

# 4. Verify
# Run pytest to confirm tests still pass
```

**Note:** Migration utilities are tools for transitioning legacy code. New tests should use current patterns (EntityRegistry, MockBoundaryFactory, GitHubDataBuilder) from the start.

### Entity Discovery Fixtures

The project provides entity discovery fixtures in `tests.shared.fixtures.entity_fixtures` that dynamically discover all registered entities. These fixtures eliminate the need to hardcode entity counts or lists in tests.

**Available Fixtures:**

```python
from tests.shared import (
    entity_registry,                    # Fresh EntityRegistry instance
    all_entity_names,                   # All registered entity names
    enabled_entity_names,               # Default-enabled entity names
    entity_names_by_dependency_order,   # Entities in topological order
    independent_entity_names,           # Entities with no dependencies
)
```

**When to Use:**

- **all_entity_names**: When validating all entities are handled (factory tests, registry tests)
- **enabled_entity_names**: When testing default configuration behavior
- **entity_names_by_dependency_order**: When validating execution order
- **independent_entity_names**: When testing root entities without dependencies
- **entity_registry**: When tests need full registry access for custom queries

**Key Benefits:**

- Zero maintenance when adding/removing entities
- Tests automatically adapt to system changes
- Validates EntityRegistry discovery mechanism
- Eliminates hardcoded entity counts and lists

**Example: Factory Test with Entity Discovery**

```python
@pytest.mark.integration
def test_factory_creates_all_entities(all_entity_names):
    """Test factory creates strategies for all discovered entities."""
    factory = StrategyFactory(registry=EntityRegistry())
    strategies = factory.create_save_strategies(git_service=Mock())

    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify all discovered entities have strategies
    assert set(strategy_names) == set(all_entity_names)
```

**Example: Dependency Order Test**

```python
@pytest.mark.integration
def test_entities_in_dependency_order(entity_names_by_dependency_order):
    """Test entities are processed in correct dependency order."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    # Verify matches discovered order
    assert enabled_names == entity_names_by_dependency_order

    # Verify specific dependency contracts
    def idx(name):
        return enabled_names.index(name)

    assert idx("milestones") < idx("issues")
    assert idx("issues") < idx("comments")
```

**Example: Testing Conditional Entity Inclusion**

```python
@pytest.mark.integration
def test_strategy_without_git_service(all_entity_names):
    """Test git_repository excluded when git_service not provided."""
    registry = EntityRegistry()
    registry.get_entity("git_repository").enabled = False
    factory = StrategyFactory(registry)

    strategies = factory.create_save_strategies()
    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify all entities except git_repository
    expected = set(all_entity_names) - {"git_repository"}
    assert set(strategy_names) == expected
```

**Anti-Patterns to Avoid:**

❌ **Don't hardcode entity names in fixtures:**
```python
# BAD - creates coupling
def test_with_hardcoded_list():
    expected = ["labels", "issues", "releases"]  # Manual list
    assert actual == expected
```

✅ **Do use discovery fixtures:**
```python
# GOOD - uses discovery
def test_with_discovery(all_entity_names):
    assert set(actual) == set(all_entity_names)
```

❌ **Don't check specific entities unless testing that entity:**
```python
# BAD - unnecessary coupling
def test_factory(all_entity_names):
    strategies = create_strategies()
    assert "labels" in strategies  # Only needed if testing labels specifically
    assert "issues" in strategies  # Creates brittle test
```

✅ **Do use set equality for completeness:**
```python
# GOOD - validates behavior without coupling
def test_factory(all_entity_names):
    strategies = create_strategies()
    strategy_names = [s.get_entity_name() for s in strategies]
    assert set(strategy_names) == set(all_entity_names)
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

**OLD WAY - Manual Configuration (AVOID):**
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

**NEW WAY - Factory Pattern (RECOMMENDED):**
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

**Recommended Use:** PRIMARY METHOD - Use for most test scenarios.

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

#### DO - Recommended Patterns

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

#### DON'T - Anti-patterns to Avoid

1. **Manual `Mock()` creation for boundary objects**
2. **Multiple factory configurations per test**
3. **Manual protocol method configuration**
4. **Ignoring protocol completeness validation**
5. **Hardcoded return values without sample data**
6. **Creating incomplete mocks**

```python
# DON'T: Manual Mock() creation
mock_boundary = Mock()
mock_boundary.get_repository_labels.return_value = []

# DON'T: Incomplete protocol implementation
mock_boundary.get_repository_issues.return_value = []
# Missing 25+ other required methods!

# DON'T: Hardcoded return values without sample data
mock_boundary.get_repository_labels.return_value = [
    {"name": "bug", "color": "ff0000"}  # Use sample_github_data instead
]

# DON'T: Ignoring validation failures
# Always ensure protocol completeness
```

#### Method Selection Guide
- **Standard Testing:** `create_auto_configured(sample_github_data)`
- **Empty Repository:** `create_auto_configured({})`
- **Restore Testing:** `create_for_restore(success_responses=True)`
- **Protocol Validation:** `create_protocol_complete(sample_github_data)`
- **Legacy Support:** `create_with_data("full", sample_data=sample_github_data)`

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

---

[← Testing Guide](README.md) | [Writing Tests](writing-tests.md) | [Specialized Testing →](specialized-testing.md)
