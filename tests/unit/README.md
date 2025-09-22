# Unit Tests Documentation

This directory contains unit tests for the GitHub Data project. Unit tests focus on testing individual components in isolation with mocked dependencies.

## Test Organization

### Test Files

- `test_main_unit.py` - Main module and CLI argument handling
- `test_json_storage_unit.py` - JSON storage operations  
- `test_rate_limit_handling_unit.py` - GitHub API rate limiting
- `test_metadata_unit.py` - Metadata formatting functionality
- `test_dependency_injection_unit.py` - Dependency injection architecture
- `test_conflict_strategies_unit.py` - Label conflict resolution strategies
- `test_graphql_paginator_unit.py` - GraphQL pagination utilities
- `test_data_enrichment_unit.py` - Data enrichment utilities

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

#### Infrastructure Markers
Add infrastructure markers for API and storage tests:
- `pytest.mark.github_api` - GitHub API interaction tests
- `pytest.mark.storage` - Data storage and persistence tests
- `pytest.mark.rate_limiting` - Rate limiting behavior tests

#### Workflow Markers
Add workflow markers for backup/restore operations:
- `pytest.mark.backup_workflow` - Backup operation workflows
- `pytest.mark.restore_workflow` - Restore operation workflows

## Writing Unit Tests

### Basic Test Structure

```python
"""
Tests for [component name].

Brief description of what this test module covers.
"""

import pytest
from unittest.mock import Mock, patch
from tests.shared import TestDataHelper, AssertionHelper, MockHelper

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

#### FixtureHelper
Create test data structures:
```python
from tests.shared import FixtureHelper

def test_with_sample_data():
    # Get sample test data with realistic structure
    test_data = FixtureHelper.create_sample_test_data()
    
    assert len(test_data["labels"]) == 2
    assert len(test_data["issues"]) == 1
    assert test_data["issues"][0]["title"] == "Test Issue 1"
```

### Enhanced Fixtures Integration

Use enhanced fixtures from `tests.shared` for sophisticated testing:

```python
from tests.shared import (
    github_data_builder,
    parametrized_data_factory,
    boundary_with_repository_data,
    backup_workflow_services
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

def test_workflow_integration(backup_workflow_services):
    """Test complete workflow integration."""
    services = backup_workflow_services
    github_service = services["github"]
    storage_service = services["storage"]
    
    # Test with pre-configured workflow services
    backup_repository_data(github_service, storage_service, "test/repo")
    
    # Verify workflow interactions
    github_service._boundary.get_repository_labels.assert_called_once()
```

### Test Patterns

#### Pattern 1: Simple Unit Test
```python
@pytest.mark.unit
@pytest.mark.fast 
@pytest.mark.labels
def test_label_validation():
    """Test label validation logic."""
    label = TestDataHelper.create_test_label(color="invalid")
    
    with pytest.raises(ValidationError):
        validate_label(label)
```

#### Pattern 2: Mock Integration Test
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.github_api
def test_api_client_interaction():
    """Test GitHub API client interactions."""
    mock_client = MockHelper.create_github_client_mock()
    mock_client.get_repository_labels.return_value = [
        {"name": "bug", "color": "ff0000"}
    ]
    
    service = GitHubService(mock_client)
    labels = service.get_labels("owner/repo")
    
    assert len(labels) == 1
    AssertionHelper.assert_mock_called_with_repo(
        mock_client.get_repository_labels, "owner/repo"
    )
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

#### Pattern 4: Error Handling Test
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.error_simulation
def test_error_handling(boundary_with_api_errors):
    """Test error handling scenarios."""
    service = GitHubService(boundary_with_api_errors)
    
    with pytest.raises(GitHubAPIError):
        service.get_labels("owner/repo")
```

## Test Execution

### Run Unit Tests Only
```bash
# Fast development cycle
make test-unit

# Using pytest directly
pdm run pytest -m unit

# Specific feature tests
pdm run pytest -m "unit and labels"
pdm run pytest -m "unit and github_api"
```

### Run by Performance
```bash
# Fast tests only (< 1 second)
pdm run pytest -m "unit and fast"

# Exclude slow tests
pdm run pytest -m "unit and not slow"
```

### Run by Feature
```bash
# Label-related unit tests
pdm run pytest -m "unit and labels"

# API interaction tests 
pdm run pytest -m "unit and github_api"

# Storage tests
pdm run pytest -m "unit and storage"

# Workflow tests
pdm run pytest -m "unit and (backup_workflow or restore_workflow)"
```

## Best Practices

### Test Organization
1. Group related tests in classes with descriptive names
2. Use clear, descriptive test method names
3. Follow the AAA pattern (Arrange, Act, Assert)
4. Use appropriate markers for test categorization

### Data Management
1. Use `TestDataHelper` for standardized test entities
2. Use `FixtureHelper` for consistent test data structures
3. Prefer shared fixtures over inline test data creation
4. Keep test data minimal but realistic

### Mock Usage
1. Use `MockHelper` for consistent mock setup
2. Mock at appropriate boundaries (services, not individual methods)
3. Verify mock interactions with `AssertionHelper`
4. Use shared enhanced fixtures for complex scenarios

### Test Isolation
1. Ensure tests can run independently in any order
2. Use proper fixture scopes for resource management
3. Clean up any global state modifications
4. Use temporary directories for file operations

### Performance
1. Keep unit tests fast (< 1 second each)
2. Use appropriate fixture scopes to avoid repeated setup
3. Mock expensive operations and external dependencies
4. Use performance markers for test categorization

### Documentation
1. Include docstrings for test classes and methods
2. Use descriptive names that explain what's being tested
3. Add comments for complex test setup or assertions
4. Document any special test requirements or dependencies