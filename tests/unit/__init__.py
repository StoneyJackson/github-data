"""
Unit Tests Package - Modernized Test Infrastructure

This package contains fast, isolated unit tests that test individual components
in isolation using mocks and fixtures. The unit tests have been modernized with
standardized markers, shared utilities, and enhanced fixture integration.

## Test Organization

### Core Requirements
All unit tests must:
- Execute quickly (< 1 second each)
- Use mocks for external dependencies
- Focus on single units of functionality
- Be marked with @pytest.mark.unit and @pytest.mark.fast

### Standardized Markers
Tests should include appropriate markers based on functionality:

#### Feature Markers:
- @pytest.mark.labels - Label management functionality
- @pytest.mark.issues - Issue management functionality
- @pytest.mark.comments - Comment management functionality
- @pytest.mark.sub_issues - Sub-issues workflow functionality
- @pytest.mark.pull_requests - Pull request workflow functionality

#### Infrastructure Markers:
- @pytest.mark.github_api - GitHub API interaction tests
- @pytest.mark.storage - Data storage and persistence tests
- @pytest.mark.rate_limiting - Rate limiting behavior tests

#### Workflow Markers:
- @pytest.mark.backup_workflow - Backup operation workflows
- @pytest.mark.restore_workflow - Restore operation workflows

### Test File Organization

- `test_main_unit.py` - Main module and CLI (backup_workflow, restore_workflow)
- `test_json_storage_unit.py` - JSON storage operations (storage)
- `test_rate_limit_handling_unit.py` - GitHub API rate limiting
  (github_api, rate_limiting)
- `test_metadata_unit.py` - Metadata formatting (issues, comments)
- `test_dependency_injection_unit.py` - Dependency injection
  (backup_workflow, restore_workflow)
- `test_conflict_strategies_unit.py` - Label conflict resolution
  (labels, restore_workflow)
- `test_graphql_paginator_unit.py` - GraphQL pagination (github_api)
- `test_data_enrichment_unit.py` - Data enrichment (comments, sub_issues, pull_requests)

### Shared Test Utilities

Use standardized helpers from `tests.shared.helpers`:
- `TestDataHelper` - Create standardized test entities
- `MockHelper` - Create standardized mock objects
- `AssertionHelper` - Validate test entities and mock interactions
- `FixtureHelper` - Create consistent test data structures
- `TestMarkerHelper` - Work with pytest markers

### Enhanced Fixtures

Leverage enhanced fixtures from `tests.shared`:
- `github_data_builder` - Dynamic test data generation
- `parametrized_data_factory` - Predefined test scenarios
- `backup_workflow_services` - Complete workflow testing
- `boundary_with_repository_data` - Realistic API simulation

## Example Usage

```python
import pytest
from tests.shared import TestDataHelper, AssertionHelper, MockHelper

pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.labels,  # Feature marker
    pytest.mark.restore_workflow  # Workflow marker
]

class TestLabelRestore:
    def test_label_restoration(self):
        # Use shared utilities
        label = TestDataHelper.create_test_label()
        mock_client = MockHelper.create_github_client_mock()

        # Test logic
        result = restore_label(mock_client, label)

        # Validate results
        AssertionHelper.assert_valid_label(result)
        AssertionHelper.assert_mock_called_with_repo(
            mock_client.create_label, "owner/repo"
        )
```

See `README.md` in this directory for comprehensive documentation and examples.
"""

import pytest

# Default markers for all unit tests
pytestmark = [pytest.mark.unit, pytest.mark.fast]
